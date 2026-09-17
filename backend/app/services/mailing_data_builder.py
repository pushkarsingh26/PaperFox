import logging
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status
from app.schemas.mailing_schema import (
    MailingCandidateContext,
    MailingInput,
    MailingJDContext,
    MailingJobContext,
    MailingProjectContext,
    MailingRecipientContext,
)

logger = logging.getLogger(__name__)


class MailingDataBuilder:
    """
    Constructs a normalized MailingInput payload by consuming pre-existing
    structured JD Intelligence and Optimized Resume snapshots.
    """

    @staticmethod
    def build_input(
        job_doc: Dict[str, Any],
        profile_doc: Optional[Dict[str, Any]],
        recipient_name: Optional[str] = None,
        recipient_email: Optional[str] = None,
        recipient_role: Optional[str] = None,
    ) -> MailingInput:
        # Stage 1: Validate JD Intelligence
        reqs = job_doc.get("requirements")
        if not reqs or not job_doc.get("is_analyzed"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="JD Intelligence unavailable: Job description must be analyzed before generating outreach emails.",
            )

        # Stage 2: Validate Candidate Profile
        if not profile_doc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Candidate profile unavailable: Candidate profile facts could not be found.",
            )

        # Stage 3: Validate Optimized Resume snapshot
        opt_data = job_doc.get("optimization")
        if not opt_data and not job_doc.get("is_optimized"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Optimized Resume unavailable: Please generate an optimized resume for this job before drafting outreach.",
            )

        try:
            # 1. Job Context
            company = str(job_doc.get("company_name", "")).strip() or "Company"
            role = str(job_doc.get("role_title", "")).strip() or "Role"
            job_context = MailingJobContext(company=company, role=role)

            # 2. JD Intelligence Context
            jd_context = MailingJDContext(
                responsibilities=list(reqs.get("responsibilities", []) or []),
                required_skills=list(reqs.get("required_skills", []) or []),
                preferred_skills=list(reqs.get("preferred_skills", []) or []),
                important_keywords=list(reqs.get("important_keywords", []) or []),
            )

            # 3. Candidate Context (from Optimized Resume snapshot with profile fallback)
            personal_details = (
                opt_data.get("personal_details", {})
                if isinstance(opt_data, dict)
                else {}
            )
            candidate_name = (
                personal_details.get("full_name")
                or profile_doc.get("personal_details", {}).get("full_name")
                or "Candidate"
            ).strip()

            candidate_summary = ""
            if isinstance(opt_data, dict) and opt_data.get("summary"):
                candidate_summary = str(opt_data["summary"]).strip()
            elif profile_doc.get("summary"):
                candidate_summary = str(profile_doc["summary"]).strip()

            # Candidate Skills: extract from optimized skill groups or confirmed skills
            candidate_skills: List[str] = []
            if isinstance(opt_data, dict) and opt_data.get("skills"):
                for group in opt_data.get("skills", []):
                    if isinstance(group, dict):
                        for sk in group.get("skills", []):
                            if sk and sk not in candidate_skills:
                                candidate_skills.append(str(sk))
            # Supplement with job confirmed skills
            for cs in job_doc.get("confirmed_skills", []):
                s_name = cs.get("skill") if isinstance(cs, dict) else str(cs)
                if s_name and s_name not in candidate_skills:
                    candidate_skills.append(s_name)
            for s in job_doc.get("approved_additional_skills", []):
                if s and s not in candidate_skills:
                    candidate_skills.append(str(s))

            candidate_context = MailingCandidateContext(
                name=candidate_name,
                summary=candidate_summary,
                skills=candidate_skills[:25],
            )

            # 4. Relevant Projects (from Optimized Resume projects)
            relevant_projects: List[MailingProjectContext] = []
            opt_projects = (
                opt_data.get("projects", [])
                if isinstance(opt_data, dict)
                else []
            )

            if opt_projects:
                for p in opt_projects:
                    if isinstance(p, dict):
                        p_name = p.get("project_name") or p.get("name") or "Project"
                        p_techs = p.get("technologies", [])
                        p_bullets = p.get("bullets", [])
                        relevant_projects.append(
                            MailingProjectContext(
                                name=str(p_name),
                                technologies=[str(t) for t in p_techs],
                                description=[str(b) for b in p_bullets],
                            )
                        )
            else:
                # Fallback to verified profile projects if optimization had no projects
                for p in profile_doc.get("projects", []):
                    p_name = p.get("name", "Project")
                    p_techs = p.get("technologies", [])
                    p_desc = [p.get("description", "")] if p.get("description") else []
                    relevant_projects.append(
                        MailingProjectContext(
                            name=str(p_name),
                            technologies=[str(t) for t in p_techs],
                            description=p_desc,
                        )
                    )

            # 5. Recipient Context
            recipient_context = MailingRecipientContext(
                name=recipient_name.strip() if recipient_name and recipient_name.strip() else None,
                email=recipient_email.strip() if recipient_email and recipient_email.strip() else None,
                role=recipient_role.strip() if recipient_role and recipient_role.strip() else None,
            )

            return MailingInput(
                job=job_context,
                jd_context=jd_context,
                candidate=candidate_context,
                relevant_projects=relevant_projects[:5],
                recipient=recipient_context,
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Mailing input preparation failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Mailing input preparation failed: {str(e)}",
            )
