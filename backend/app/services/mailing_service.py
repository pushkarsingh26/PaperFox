import json
import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status

from app.repositories.job_repository import JobRepository
from app.repositories.profile_repository import ProfileRepository
from app.schemas.mailing_schema import (
    MailingAIResponse,
    MailingDraftResponse,
    MailingDraftUpdate,
    MailingGenerateRequest,
    MailingInput,
)
from app.services.ai.provider_router import ProviderRouter
from app.services.mailing_data_builder import MailingDataBuilder

logger = logging.getLogger(__name__)

BANNED_PHRASES = [
    r"\bi hope this email finds you well\b",
    r"\bi am thrilled to\b",
    r"\bi am excited to\b",
    r"\bi would be an excellent fit\b",
    r"\bi believe my unique skill set\b",
    r"\blook no further\b",
    r"\bcutting-edge\b",
    r"\bpassionate about innovation\b",
    r"\bresults-driven\b",
    r"\bseamlessly\b",
    r"\bspearheaded\b",
    r"\brobust\b",
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

    async def _get_and_authorize_job(self, job_id: str, user_id: str) -> Dict[str, Any]:
        """
        Validates job existence and user authorization.
        Returns job_doc if user owns it.
        Raises 403 Forbidden if the job exists but belongs to another user.
        Raises 404 Not Found if the job does not exist anywhere.
        """
        job_doc = await self.job_repository.get_by_id(job_id, user_id)
        if job_doc:
            return job_doc

        unscoped_job = await self.job_repository.get_by_id_unscoped(job_id)
        if unscoped_job and str(unscoped_job.get("user_id")) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this job.",
            )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job application not found.",
        )

    def _sanitize_text(self, text: str) -> str:
        """Removes banned robotic/boilerplate expressions and markdown bolding."""
        cleaned = text
        for pat in BANNED_PHRASES:
            cleaned = re.sub(pat, "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\*{2,}([^*]+)\*{2,}", r"\1", cleaned)
        cleaned = re.sub(r"[ \t]+", " ", cleaned)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        return cleaned.strip()

    def _generate_fallback_draft(
        self,
        input_data: MailingInput,
    ) -> Dict[str, Any]:
        """Deterministic, professional fallback draft when AI provider is unavailable."""
        company = input_data.job.company
        role = input_data.job.role
        candidate_name = input_data.candidate.name
        recipient_name = input_data.recipient.name

        greeting = f"Hi {recipient_name}," if recipient_name else f"Hello {company} Hiring Team,"

        project_mention = ""
        cited_evidence = []
        if input_data.relevant_projects:
            top_proj = input_data.relevant_projects[0]
            project_mention = (
                f"In my recent work on {top_proj.name}, I focused on "
                f"{', '.join(top_proj.technologies[:3]) if top_proj.technologies else 'core backend components'} "
                f"which directly aligns with the technical goals of this position."
            )
            cited_evidence.append(top_proj.name)

        body = (
            f"{greeting}\n\n"
            f"I came across the {role} opening at {company} and wanted to reach out directly.\n\n"
            f"{project_mention}\n\n"
            f"I would welcome the opportunity to connect and share more context on how my background aligns with the team's roadmap. "
            f"Please let me know if you are open to a brief conversation.\n\n"
            f"Best,\n{candidate_name}"
        )

        short_body = (
            f"{greeting}\n\n"
            f"Reaching out regarding the {role} opening at {company}. "
            f"{project_mention} "
            f"Happy to share my resume or hop on a brief chat if convenient.\n\n"
            f"Best,\n{candidate_name}"
        )

        return {
            "subject": f"{role} — {candidate_name}",
            "subject_options": [
                f"{role} — {candidate_name}",
                f"Re: {role} opening at {company}",
                f"{company} {role} Role — {candidate_name}",
            ],
            "body": body,
            "short_body": short_body,
            "selected_evidence": cited_evidence,
        }

    async def generate_draft(
        self,
        user_id: str,
        req: MailingGenerateRequest,
    ) -> MailingDraftResponse:
        """
        Independent mailing draft generation consuming structured JD Intelligence
        and Optimized Resume snapshot via normalized MailingInput JSON.
        """
        # Step 1: Authorize and retrieve Job
        job_doc = await self._get_and_authorize_job(req.job_id, user_id)

        # Step 2: Retrieve Candidate Profile facts
        profile_doc = await self.profile_repository.get_by_user_id(user_id)

        # Step 3: Build normalized MailingInput JSON payload
        mailing_input = MailingDataBuilder.build_input(
            job_doc=job_doc,
            profile_doc=profile_doc,
            recipient_name=req.recipient_name,
            recipient_email=req.recipient_email,
            recipient_role=req.recipient_role,
        )

        input_json_str = json.dumps(mailing_input.model_dump(), indent=2)

        # Step 4: Construct Humanized Prompt
        system_prompt = (
            "PAPERFOX MAILING SYSTEM — HUMAN EMAIL GENERATION\n\n"
            "Generate a professional, natural, personalized email for contacting an HR, recruiter, "
            "hiring manager, or careers team regarding the selected job.\n\n"
            "The email must sound like it was genuinely written by the candidate, not generated from "
            "a template or by matching JD keywords.\n\n"
            "WRITING STYLE:\n"
            "- Natural and conversational while remaining professional.\n"
            "- Concise: ideally 100–150 words.\n"
            "- Confident but not arrogant.\n"
            "- Direct and purposeful.\n"
            "- Warm but not overly friendly.\n"
            "- Use simple, natural English.\n"
            "- Every sentence should have a reason to exist.\n"
            "- Personalize the email using the actual company, role, and strongest relevant candidate evidence.\n"
            "- Prefer specific evidence over generic claims.\n\n"
            "STRUCTURE:\n"
            "1. Greeting\n"
            "   - Use the recipient's name when provided.\n"
            "   - If no recipient name is available, use a natural greeting such as 'Hi Hiring Team,' "
            "or 'Hello [Company] Team,'.\n"
            "   - Never invent a recipient name.\n\n"
            "2. Opening\n"
            "   - Clearly state the role the candidate is contacting them about.\n"
            "   - Avoid generic openings such as:\n"
            "     'I came across...'\n"
            "     'I am writing to express my interest...'\n"
            "     'I hope this email finds you well.'\n\n"
            "3. Relevant candidate evidence\n"
            "   - Mention 1 strong, relevant project, experience, or achievement.\n"
            "   - Explain briefly what the candidate actually built or worked on.\n"
            "   - Mention only the technologies that are genuinely relevant.\n"
            "   - Do not dump a list of keywords.\n"
            "   - Prefer concrete work such as building an AI platform, developing APIs, implementing "
            "semantic retrieval, working with LLM workflows, or other verified evidence from the candidate data.\n\n"
            "4. Natural connection\n"
            "   - Explain why that experience is relevant to the role.\n"
            "   - Make the connection specific and natural.\n"
            "   - Do not use phrases such as:\n"
            "     'directly aligns with the technical goals of this position'\n"
            "     'aligns with the team's roadmap'\n"
            "     'matches the requirements of the role'\n"
            "   unless there is genuinely specific information supporting such wording.\n\n"
            "5. Closing\n"
            "   - Express genuine interest in discussing the opportunity.\n"
            "   - Ask for a reasonable next step, such as a brief conversation or consideration for the role.\n"
            "   - Keep the closing short.\n"
            "   - Do not sound desperate or overly formal.\n\n"
            "6. Signature\n"
            "   - Candidate's actual name only.\n\n"
            "CONTENT RULES:\n"
            "- Use the JD Intelligence to understand what matters in the role.\n"
            "- Use the Optimized Resume and verified candidate evidence to determine what the candidate "
            "can genuinely discuss.\n"
            "- Never invent experience, skills, projects, achievements, metrics, responsibilities, "
            "company information, recruiter information, or technology usage.\n"
            "- A JD skill alone does NOT mean the candidate possesses that skill.\n"
            "- Only mention candidate skills that exist in the candidate's verified data.\n"
            "- Do not claim that a candidate used a technology in a project unless the project evidence "
            "supports it.\n"
            "- Do not mention every skill from the resume.\n"
            "- Select the strongest 1–2 relevant pieces of evidence.\n"
            "- Do not copy sentences from the JD.\n"
            "- Do not repeat the job description.\n"
            "- Do not turn the email into a resume summary.\n"
            "- Do not mention ATS, keyword matching, optimization, JD Intelligence, AI, or PaperFox's "
            "internal process.\n\n"
            "AVOID AI-GENERATED PHRASES:\n"
            "Do not use generic phrases such as:\n"
            "- 'I came across...'\n"
            "- 'I wanted to reach out directly.'\n"
            "- 'I am writing to express my interest...'\n"
            "- 'I believe my skills make me a strong fit...'\n"
            "- 'My background aligns perfectly...'\n"
            "- 'directly aligns with the technical goals...'\n"
            "- 'aligns with the team's roadmap.'\n"
            "- 'I would welcome the opportunity to connect...'\n"
            "- 'share more context on how my background aligns...'\n"
            "- 'I am excited about the opportunity to leverage my skills...'\n"
            "- 'I am confident that...'\n"
            "- 'I look forward to hearing from you.'\n\n"
            "Do not mechanically replace these phrases with another equally generic phrase. "
            "The writing should remain natural rather than following a rigid template.\n\n"
            "TECHNOLOGY MENTION RULE:\n"
            "Bad: 'I have experience with Python, FastAPI, LangChain, FAISS, PostgreSQL, React, Docker, and LLMs.'\n"
            "Better: 'On DevMind, I built an AI software engineering platform with FastAPI and LangChain "
            "for repository analysis and semantic code retrieval.'\n"
            "Mention technologies naturally as part of describing actual work.\n\n"
            "EMAIL LENGTH:\n"
            "Keep the email concise enough for a recruiter to read quickly.\n"
            "Target:\n"
            "- 3–5 short paragraphs\n"
            "- Approximately 100–150 words\n"
            "- No unnecessary explanation\n"
            "- No long technical descriptions\n\n"
            "SUBJECT:\n"
            "Generate a short professional subject that clearly communicates the role.\n"
            "Examples of the style:\n"
            "  'Application — Junior AI Engineer'\n"
            "  'Junior AI Engineer — Pushkar Chhokar'\n"
            "  'Interest in Junior AI Engineer Role'\n"
            "Do not generate clickbait or overly enthusiastic subjects.\n\n"
            "OUTPUT:\n"
            "Return only the structured email result as valid JSON:\n"
            "{ \"subject\": \"...\", \"body\": \"...\" }\n\n"
            "The body should be ready to send with normal paragraph spacing.\n\n"
            "The final email must prioritize:\n"
            "AUTHENTICITY → SPECIFICITY → RELEVANCE → BREVITY → PROFESSIONALISM\n\n"
            "The candidate should sound like a real person contacting a real recruiting team, "
            "not an AI system generating a keyword-optimized message."
        )

        user_content = (
            f"Here is the structured candidate and job data for generating the outreach email:\n\n"
            f"```json\n{input_json_str}\n```\n\n"
            f"Using only the verified candidate evidence in this data, write a genuine, concise, "
            f"personalized email for the role at the specified company. "
            f"Return the result as JSON with 'subject' and 'body' fields."
        )

        # Step 5: Call AI Provider Layer
        data: Dict[str, Any] = {}
        try:
            schema = MailingAIResponse.model_json_schema()
            ai_res = await self.router.generate_structured_json(
                prompt=user_content,
                schema=schema,
                system_prompt=system_prompt,
            )
            raw_data = ai_res.get("data", {})
            if isinstance(raw_data, dict) and raw_data.get("subject") and raw_data.get("body"):
                data = raw_data
            else:
                logger.warning("AI response missing required subject or body fields. Using fallback.")
                data = self._generate_fallback_draft(mailing_input)
        except Exception as e:
            logger.error(f"AI generation failed: {e}. Utilizing fallback draft.", exc_info=True)
            data = self._generate_fallback_draft(mailing_input)

        # Step 6: Sanitize and validate
        subject = self._sanitize_text(data.get("subject") or f"{mailing_input.job.role} — {mailing_input.candidate.name}")
        body = self._sanitize_text(data.get("body") or "")
        short_body = self._sanitize_text(data.get("short_body") or "") if data.get("short_body") else None
        subject_options = [
            self._sanitize_text(s) for s in data.get("subject_options", []) if s
        ]
        if not subject_options:
            subject_options = [subject]

        selected_evidence = data.get("selected_evidence", [])

        now = datetime.now(timezone.utc)
        draft_dict = {
            "job_id": req.job_id,
            "recipient_name": req.recipient_name or None,
            "recipient_email": req.recipient_email or None,
            "recipient_role": req.recipient_role or None,
            "subject": subject,
            "subject_options": subject_options,
            "body": body,
            "short_body": short_body,
            "selected_evidence": selected_evidence,
            "status": "ready",
            "generated_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }

        # Step 7: Persist draft onto job document
        await self.job_repository.update_job(
            req.job_id,
            user_id,
            {"mailing_draft": draft_dict},
        )

        return MailingDraftResponse(
            job_id=req.job_id,
            recipient_name=req.recipient_name,
            recipient_email=req.recipient_email,
            recipient_role=req.recipient_role,
            subject=subject,
            subject_options=subject_options,
            body=body,
            short_body=short_body,
            selected_evidence=selected_evidence,
            status="ready",
            generated_at=now,
            updated_at=now,
        )

    async def get_draft(self, user_id: str, job_id: str) -> Optional[MailingDraftResponse]:
        """Retrieves existing mailing draft for the specified job."""
        job_doc = await self._get_and_authorize_job(job_id, user_id)
        draft_data = job_doc.get("mailing_draft")
        if not draft_data:
            return None

        return MailingDraftResponse(
            job_id=job_id,
            recipient_name=draft_data.get("recipient_name"),
            recipient_email=draft_data.get("recipient_email"),
            recipient_role=draft_data.get("recipient_role"),
            subject=draft_data.get("subject", ""),
            subject_options=draft_data.get("subject_options", []),
            body=draft_data.get("body", ""),
            short_body=draft_data.get("short_body"),
            selected_evidence=draft_data.get("selected_evidence", []),
            status=draft_data.get("status", "ready"),
            generated_at=draft_data.get("generated_at"),
            updated_at=draft_data.get("updated_at"),
        )

    async def update_draft(
        self,
        user_id: str,
        job_id: str,
        update_in: MailingDraftUpdate,
    ) -> MailingDraftResponse:
        """Saves user edits to the outreach draft."""
        job_doc = await self._get_and_authorize_job(job_id, user_id)
        existing_draft = job_doc.get("mailing_draft") or {}

        now = datetime.now(timezone.utc)
        updated_draft = {
            **existing_draft,
            "job_id": job_id,
            "recipient_name": update_in.recipient_name if update_in.recipient_name is not None else existing_draft.get("recipient_name"),
            "recipient_email": update_in.recipient_email if update_in.recipient_email is not None else existing_draft.get("recipient_email"),
            "recipient_role": update_in.recipient_role if update_in.recipient_role is not None else existing_draft.get("recipient_role"),
            "subject": update_in.subject if update_in.subject is not None else existing_draft.get("subject", ""),
            "body": update_in.body if update_in.body is not None else existing_draft.get("body", ""),
            "short_body": update_in.short_body if update_in.short_body is not None else existing_draft.get("short_body"),
            "status": update_in.status or existing_draft.get("status", "ready"),
            "updated_at": now.isoformat(),
        }

        await self.job_repository.update_job(
            job_id,
            user_id,
            {"mailing_draft": updated_draft},
        )

        return MailingDraftResponse(
            job_id=job_id,
            recipient_name=updated_draft.get("recipient_name"),
            recipient_email=updated_draft.get("recipient_email"),
            recipient_role=updated_draft.get("recipient_role"),
            subject=updated_draft.get("subject", ""),
            subject_options=updated_draft.get("subject_options", []),
            body=updated_draft.get("body", ""),
            short_body=updated_draft.get("short_body"),
            selected_evidence=updated_draft.get("selected_evidence", []),
            status=updated_draft.get("status", "ready"),
            generated_at=updated_draft.get("generated_at"),
            updated_at=now,
        )
