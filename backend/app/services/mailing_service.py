import copy
import json
import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status

from pydantic import BaseModel, Field
from app.repositories.job_repository import JobRepository
from app.repositories.profile_repository import ProfileRepository
from app.schemas.job import MailingDraft, MailingDraftUpdate, MailingGenerateRequest
from app.services.ai.provider_router import ProviderRouter

logger = logging.getLogger(__name__)


class MailingAIResponse(BaseModel):
    subject_options: List[str] = Field(default_factory=list, description="List of 3-4 specific, concise, professional subject lines")
    chosen_subject: str = Field(..., description="The single strongest subject line")
    body: str = Field(..., description="The complete outreach email body")
    short_body: Optional[str] = Field(None, description="Concise 2-3 paragraph alternative/follow-up version")
    selected_evidence: List[str] = Field(default_factory=list, description="List of 1-3 short strings noting cited evidence")

BANNED_EMAIL_PHRASES = [
    r"\bi hope this email finds you well\b",
    r"\bi am thrilled to apply\b",
    r"\bi am writing to express my enthusiasm\b",
    r"\bi would be an excellent fit\b",
    r"\bi am confident that i am\b",
    r"\blook no further\b",
    r"\bcutting-edge\b",
    r"\bseamless(?:ly)?\b",
    r"\bAI-powered\b",
    r"\brobust\b",
    r"\bspearheaded\b",
]


class MailingService:
    def __init__(
        self,
        job_repository: JobRepository,
        profile_repository: ProfileRepository,
        router: Optional[ProviderRouter] = None,
    ):
        self.job_repository = job_repository
        self.profile_repository = profile_repository
        self.router = router or ProviderRouter()

    async def generate_mailing_draft(
        self,
        user_id: str,
        job_id: str,
        req: Optional[MailingGenerateRequest] = None,
    ) -> MailingDraft:
        """
        Generates a personalized, humanized hiring-team cold outreach email
        grounded strictly in the candidate's verified profile facts and existing JD Intelligence.
        """
        job_doc = await self.job_repository.get_by_id(job_id, user_id)
        if not job_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job application not found",
            )

        if not job_doc.get("is_analyzed") or not job_doc.get("requirements"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job application must be analyzed with JD Intelligence before generating outreach emails.",
            )

        profile_doc = await self.profile_repository.get_by_user_id(user_id)
        if not profile_doc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Candidate profile not found. Please complete your master profile first.",
            )

        company_name = job_doc.get("company_name", "").strip() or "Company"
        role_title = job_doc.get("role_title", "").strip() or "Role"
        requirements = job_doc.get("requirements", {})
        job_description = job_doc.get("job_description", "")

        personal_details = profile_doc.get("personal_details", {})
        candidate_name = personal_details.get("full_name", "").strip() or "Candidate"

        # Collect candidate facts
        verified_skills = [
            s.get("name", "").strip()
            for s in profile_doc.get("skills", [])
            if s.get("name")
        ]
        confirmed_job_skills = job_doc.get("approved_additional_skills", [])

        # Collect verified projects with evidence
        projects_summary = []
        for p in profile_doc.get("projects", []):
            p_name = p.get("name", "")
            p_techs = ", ".join(p.get("technologies", []))
            p_desc = p.get("description", "")
            p_evidence = p.get("evidence", {})

            metrics = []
            if isinstance(p_evidence, dict):
                for m in p_evidence.get("measurable_outcomes", []):
                    metrics.append(str(m))

            metric_str = f" [Metrics: {'; '.join(metrics)}]" if metrics else ""
            projects_summary.append(
                f"- Project: {p_name} | Technologies: {p_techs} | Description: {p_desc}{metric_str}"
            )

        projects_context = "\n".join(projects_summary) if projects_summary else "No verified projects on file."

        recipient_name = req.recipient_name.strip() if (req and req.recipient_name) else ""
        recipient_email = req.recipient_email.strip() if (req and req.recipient_email) else ""
        recipient_role = req.recipient_role.strip() if (req and req.recipient_role) else ""

        # Construct prompt
        system_prompt = (
            "You are an elite technical career advisor and executive copywriter.\n"
            "Generate a concise, highly personalized cold outreach email from a job candidate to a hiring/recruiting team.\n\n"
            "CRITICAL WRITING RULES:\n"
            "1. AUTHENTIC HUMAN CONVERSATIONAL TONE:\n"
            "   - Write in genuine, confident, conversational professional English.\n"
            "   - Use short, digestible paragraphs (2-3 sentences max per paragraph).\n"
            "   - Varied sentence structures; sound like a real engineer reaching out peer-to-peer.\n"
            "   - Absolutely NO generic AI boilerplate or flattery.\n"
            "   - STRICTLY BANNED PHRASES:\n"
            "     * 'I hope this email finds you well'\n"
            "     * 'I am thrilled to apply' / 'I am excited to submit'\n"
            "     * 'I am writing to express my enthusiasm'\n"
            "     * 'I would be an excellent fit' / 'I am the ideal candidate'\n"
            "     * 'Look no further'\n"
            "     * 'cutting-edge', 'seamless', 'spearheaded', 'robust', 'AI-powered', 'dynamic'\n"
            "2. FACTUAL GROUNDING (STRICT):\n"
            "   - Mention ONLY verified technologies and project details from the candidate facts below.\n"
            "   - NEVER fabricate experience, companies, client relationships, or metrics.\n"
            "   - If confirmed job skills have no project evidence, they may only be mentioned as familiar tools, never as fabricated project work.\n"
            "3. RELEVANCE & CONNECTION:\n"
            "   - Select ONLY the 1-2 strongest pieces of candidate project/skill evidence that directly solve the role's primary technical needs.\n"
            "   - Clearly connect the candidate's verified work to what the team is building.\n"
            "4. EMAIL STRUCTURE:\n"
            "   - Greeting: If recipient name is provided, use 'Hi [Name],' or 'Hello [Name],'. Otherwise use 'Hello [Company] Hiring Team,'. NEVER fabricate names.\n"
            "   - Opening: Direct statement of outreach regarding the specific role.\n"
            "   - Body: 1-2 concise paragraphs highlighting verified project evidence and connecting it directly to role requirements.\n"
            "   - Closing: Low-pressure, professional call-to-action (e.g. sharing resume or chatting briefly).\n"
            "   - Sign-off: 'Best,' followed by Candidate Name.\n"
            "5. OUTPUT REQUIREMENTS:\n"
            "   - Return structured JSON with:\n"
            "     * 'subject_options': List of 3-4 specific, concise, professional subject lines (e.g. 'Software Engineer role — [Name]', 'Re: [Role] at [Company] — [Key Tech]'). NO emojis, NO clickbait, NO 'URGENT'.\n"
            "     * 'chosen_subject': The single strongest subject line.\n"
            "     * 'body': The complete outreach email body.\n"
            "     * 'short_body': A concise 2-3 paragraph alternative/follow-up version.\n"
            "     * 'selected_evidence': List of 1-3 short strings noting which verified project/skill evidence was cited."
        )

        user_content = (
            f"TARGET ROLE & COMPANY:\n"
            f"Company: {company_name}\n"
            f"Role Title: {role_title}\n"
            f"Key Required Skills: {', '.join(requirements.get('required_skills', []))}\n"
            f"AI/ML Requirements: {', '.join(requirements.get('ai_ml_requirements', []))}\n"
            f"Key Responsibilities: {', '.join(requirements.get('responsibilities', []))}\n\n"
            f"RECIPIENT CONTEXT:\n"
            f"Recipient Name: {recipient_name or 'Not specified (use company hiring team greeting)'}\n"
            f"Recipient Role: {recipient_role or 'Hiring Team'}\n\n"
            f"CANDIDATE FACTS (DO NOT EXCEED OR FABRICATE):\n"
            f"Candidate Name: {candidate_name}\n"
            f"Verified Skills: {', '.join(verified_skills)}\n"
            f"Job-Confirmed Skills: {', '.join(confirmed_job_skills)}\n"
            f"Verified Projects & Evidence:\n{projects_context}\n"
        )

        try:
            schema = MailingAIResponse.model_json_schema()
            ai_res = await self.router.generate_structured_json(
                prompt=user_content,
                schema=schema,
                system_prompt=system_prompt,
            )
            data = ai_res.get("data", {})
        except Exception as e:
            logger.error(f"AI generation for mailing draft failed: {e}", exc_info=True)
            # Fallback deterministic draft
            data = self._generate_fallback_draft(
                company_name=company_name,
                role_title=role_title,
                candidate_name=candidate_name,
                recipient_name=recipient_name,
                verified_skills=verified_skills,
                projects_summary=projects_summary,
            )

        # Sanitize outputs
        subject_options = data.get("subject_options", [])
        if not subject_options:
            subject_options = [
                f"{role_title} Application — {candidate_name}",
                f"{company_name} {role_title} Role — {candidate_name}",
                f"Re: {role_title} Opportunity at {company_name}",
            ]

        chosen_subject = data.get("chosen_subject") or subject_options[0]
        chosen_subject = self._sanitize_text(chosen_subject)

        body = self._sanitize_email_body(data.get("body", ""), candidate_name)
        short_body = self._sanitize_email_body(data.get("short_body", ""), candidate_name)
        selected_evidence = data.get("selected_evidence", [])

        now = datetime.now(timezone.utc)
        draft = MailingDraft(
            job_id=job_id,
            recipient_name=recipient_name or None,
            recipient_email=recipient_email or None,
            recipient_role=recipient_role or None,
            subject=chosen_subject,
            subject_options=subject_options,
            body=body,
            short_body=short_body,
            selected_evidence=selected_evidence,
            status="draft",
            generated_at=now,
            updated_at=now,
        )

        # Persist draft to job application in MongoDB
        await self.job_repository.update_job(
            job_id,
            user_id,
            {"mailing_draft": draft.model_dump()},
        )

        return draft

    async def get_mailing_draft(
        self,
        user_id: str,
        job_id: str,
    ) -> Optional[MailingDraft]:
        """Retrieve existing mailing draft for a job application."""
        job_doc = await self.job_repository.get_by_id(job_id, user_id)
        if not job_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job application not found",
            )

        draft_doc = job_doc.get("mailing_draft")
        if not draft_doc:
            return None

        try:
            return MailingDraft(**draft_doc) if isinstance(draft_doc, dict) else draft_doc
        except Exception:
            return None

    async def update_mailing_draft(
        self,
        user_id: str,
        job_id: str,
        update_data: MailingDraftUpdate,
    ) -> MailingDraft:
        """Update and persist candidate edits to an existing mailing draft."""
        job_doc = await self.job_repository.get_by_id(job_id, user_id)
        if not job_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job application not found",
            )

        existing_draft = job_doc.get("mailing_draft") or {}
        now = datetime.now(timezone.utc)

        updated_dict = copy.deepcopy(existing_draft)
        updated_dict["job_id"] = job_id
        updated_dict["updated_at"] = now

        if update_data.recipient_name is not None:
            updated_dict["recipient_name"] = update_data.recipient_name.strip() or None
        if update_data.recipient_email is not None:
            updated_dict["recipient_email"] = update_data.recipient_email.strip() or None
        if update_data.recipient_role is not None:
            updated_dict["recipient_role"] = update_data.recipient_role.strip() or None
        if update_data.subject is not None:
            updated_dict["subject"] = update_data.subject.strip()
        if update_data.body is not None:
            updated_dict["body"] = update_data.body.strip()
        if update_data.short_body is not None:
            updated_dict["short_body"] = update_data.short_body.strip()
        if update_data.status is not None:
            updated_dict["status"] = update_data.status.strip()

        draft = MailingDraft(**updated_dict)

        await self.job_repository.update_job(
            job_id,
            user_id,
            {"mailing_draft": draft.model_dump()},
        )

        return draft

    def _sanitize_email_body(self, text: str, candidate_name: str) -> str:
        """Strips markdown bolding, removes banned phrases, cleans whitespace."""
        if not text:
            return ""

        # Remove markdown bolding
        clean = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
        clean = re.sub(r"\*([^*]+)\*", r"\1", clean)

        # Remove banned phrases
        for pattern in BANNED_EMAIL_PHRASES:
            clean = re.sub(pattern, "", clean, flags=re.IGNORECASE)

        # Normalize clean double spaces
        clean = re.sub(r"[ \t]+", " ", clean)
        clean = re.sub(r"\n{3,}", "\n\n", clean)

        clean = clean.strip()
        return clean

    def _sanitize_text(self, text: str) -> str:
        if not text:
            return ""
        clean = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
        clean = re.sub(r"[ \t]+", " ", clean)
        return clean.strip()

    def _generate_fallback_draft(
        self,
        company_name: str,
        role_title: str,
        candidate_name: str,
        recipient_name: str,
        verified_skills: List[str],
        projects_summary: List[str],
    ) -> Dict[str, Any]:
        greeting = f"Hi {recipient_name}," if recipient_name else f"Hello {company_name} Hiring Team,"
        top_skills = ", ".join(verified_skills[:4]) if verified_skills else "software engineering"

        body = (
            f"{greeting}\n\n"
            f"I'm reaching out regarding the {role_title} opportunity at {company_name}. "
            f"My recent background focuses on {top_skills}, building production systems with clear engineering outcomes.\n\n"
            f"I've verified experience with technical projects that align closely with {company_name}'s requirements, "
            f"and I'd welcome the chance to discuss how my background could support your team's goals.\n\n"
            f"I'd be glad to share my resume and relevant project details if helpful.\n\n"
            f"Best,\n{candidate_name}"
        )

        short_body = (
            f"{greeting}\n\n"
            f"I'm reaching out regarding the {role_title} opening at {company_name}. "
            f"With experience across {top_skills}, my background aligns well with what your team is building.\n\n"
            f"I'd welcome the chance to connect briefly and share my resume.\n\n"
            f"Best,\n{candidate_name}"
        )

        return {
            "subject_options": [
                f"{role_title} Role — {candidate_name}",
                f"{company_name} {role_title} Application — {candidate_name}",
                f"Re: {role_title} Opportunity / {candidate_name}",
            ],
            "chosen_subject": f"{role_title} Role — {candidate_name}",
            "body": body,
            "short_body": short_body,
            "selected_evidence": [f"Technical background in {top_skills}"],
        }
