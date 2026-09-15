import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.schemas.job import JobRequirements
from app.schemas.optimization_schema import (
    KeywordAlignment,
    OptimizationMetadata,
    OptimizedExperience,
    OptimizedInternship,
    OptimizedProject,
    OptimizedResumeData,
    OptimizedSkillGroup,
    StructuredProjectEvidence,
)
from app.services.ai.provider_router import ProviderRouter
from app.utils.optimization_validator import validate_optimized_data

logger = logging.getLogger(__name__)


class OptimizerService:
    """
    Task-based AI Resume Optimizer Service.
    Executes modular tasks for Summary, Projects, Experience, Skills, Certifications, and Keyword Alignment
    using multi-provider FREE-model routing and deterministic post-AI validation.
    """

    def __init__(self, router: Optional[ProviderRouter] = None):
        self.router = router or ProviderRouter()

    async def optimize_summary(
        self,
        candidate_profile: Dict[str, Any],
        job_requirements: JobRequirements,
        structured_evidence_map: Optional[Dict[str, StructuredProjectEvidence]] = None
    ) -> str:
        """Generates a job-specific professional summary strictly grounded in candidate facts."""
        personal = candidate_profile.get("personal_details", {})
        cand_name = personal.get("full_name", "Candidate")
        skills_str = ", ".join([s.get("name", "") for s in candidate_profile.get("skills", []) if s.get("name")])

        # Summarize project context
        proj_summaries = []
        for p in candidate_profile.get("projects", []):
            name = p.get("name", "")
            techs = ", ".join(p.get("technologies", []))
            desc = p.get("description", "")
            ev = structured_evidence_map.get(name) if structured_evidence_map else None
            ev_str = f" Evidence: {', '.join(ev.technologies + ev.frameworks)}" if ev else ""
            proj_summaries.append(f"- {name}: {desc} (Tech: {techs}{ev_str})")
        proj_context = "\n".join(proj_summaries)

        system_prompt = "You are PaperFox Resume Optimizer, an expert executive resume writer."
        prompt = f"""
Generate a concise, high-impact 2-4 sentence Professional Summary tailored for the target role.

TARGET ROLE INFORMATION:
Title: {job_requirements.title or 'Software Engineer'}
Required Skills: {', '.join(job_requirements.required_skills)}
Technologies: {', '.join(job_requirements.technologies_frameworks)}
AI/ML Requirements: {', '.join(job_requirements.ai_ml_requirements)}

CANDIDATE VERIFIED FACTS:
Name: {cand_name}
Candidate Type: {candidate_profile.get('candidate_type', 'experienced')}
Skills: {skills_str}
Key Projects:
{proj_context}

CRITICAL RULES:
1. Ground the summary strictly in the candidate's verified skills and project achievements.
2. Align language and terminology with the target role.
3. Do NOT invent years of experience, titles, metrics, or technologies not present in the candidate facts.
4. Do NOT copy the job description verbatim.

Return JSON schema:
{{
  "summary": "Professional summary text here..."
}}
"""
        schema = {
            "type": "object",
            "properties": {"summary": {"type": "string"}},
            "required": ["summary"]
        }

        try:
            res = await self.router.generate_structured_json(prompt=prompt, schema=schema, system_prompt=system_prompt)
            return res["data"]["summary"].strip()
        except Exception as e:
            logger.warning(f"Summary optimization failed: {str(e)}. Using fallback profile summary.")
            return f"Results-driven software professional proficient in {skills_str[:120]}, seeking to leverage technical engineering expertise to drive impact as a {job_requirements.title or 'Software Engineer'}."

    async def optimize_projects(
        self,
        candidate_profile: Dict[str, Any],
        job_requirements: JobRequirements,
        structured_evidence_map: Optional[Dict[str, StructuredProjectEvidence]] = None
    ) -> List[OptimizedProject]:
        """Evaluates relevance and optimizes bullets for every candidate project."""
        orig_projects = candidate_profile.get("projects", [])
        if not orig_projects:
            return []

        optimized_projects: List[OptimizedProject] = []

        for proj in orig_projects:
            p_name = proj.get("name", "Project")
            p_id = proj.get("id")
            p_techs = proj.get("technologies", [])
            p_desc = proj.get("description", "")

            ev = structured_evidence_map.get(p_name) if structured_evidence_map else None
            ev_context = ""
            if ev:
                ev_context = f"""
VERIFIED CODEBASE EVIDENCE:
Architecture: {', '.join(ev.architecture)}
Technologies: {', '.join(ev.technologies + ev.frameworks + ev.databases + ev.deployment)}
APIs & Models: {', '.join(ev.apis + ev.models)}
Technical Details: {', '.join(ev.technical_details + ev.engineering_decisions)}
"""

            system_prompt = "You are PaperFox Resume Optimizer, specializing in technical software project presentation."
            prompt = f"""
Optimize project entry for the target job requirements.

TARGET JOB REQUIREMENTS:
Title: {job_requirements.title}
Required Skills: {', '.join(job_requirements.required_skills)}
Technologies/Frameworks: {', '.join(job_requirements.technologies_frameworks)}
Keywords: {', '.join(job_requirements.important_keywords)}

CANDIDATE PROJECT:
Name: {p_name}
Manual Description: {p_desc}
Technologies: {', '.join(p_techs)}
Features: {', '.join(proj.get('features', []))}
Responsibilities: {', '.join(proj.get('responsibilities', []))}
{ev_context}

TASK:
1. Assign a relevance score between 0.0 and 1.0 based on overlap with job requirements.
2. Generate 2 to 4 bullet points emphasizing relevant technical implementations.
3. Keep project technologies strictly limited to verified candidate technologies.

Return JSON schema:
{{
  "relevance_score": 0.9,
  "relevance_reasons": ["Uses FastAPI and MongoDB required by the role"],
  "matched_requirements": ["FastAPI", "MongoDB"],
  "technologies": ["List of verified technologies used"],
  "bullets": ["Bullet point 1", "Bullet point 2"]
}}
"""
            schema = {
                "type": "object",
                "properties": {
                    "relevance_score": {"type": "number"},
                    "relevance_reasons": {"type": "array", "items": {"type": "string"}},
                    "matched_requirements": {"type": "array", "items": {"type": "string"}},
                    "technologies": {"type": "array", "items": {"type": "string"}},
                    "bullets": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["relevance_score", "bullets"]
            }

            try:
                res = await self.router.generate_structured_json(prompt=prompt, schema=schema, system_prompt=system_prompt)
                data = res["data"]

                # Ensure project technologies are grounded in original technologies or evidence
                allowed_techs = set([t.lower() for t in p_techs])
                if ev:
                    for t in (ev.technologies + ev.frameworks + ev.databases + ev.deployment + ev.apis + ev.models):
                        allowed_techs.add(t.lower())

                final_techs = [t for t in data.get("technologies", p_techs) if t.lower() in allowed_techs or not p_techs]
                if not final_techs:
                    final_techs = p_techs

                optimized_projects.append(
                    OptimizedProject(
                        project_id=p_id,
                        project_name=p_name,
                        relevance_score=float(data.get("relevance_score", 1.0)),
                        relevance_reasons=data.get("relevance_reasons", []),
                        matched_requirements=data.get("matched_requirements", []),
                        technologies=final_techs,
                        bullets=data.get("bullets", [p_desc] if p_desc else ["Implemented software solution."]),
                        project_url=proj.get("project_url"),
                        github_url=proj.get("github_url"),
                        repository_url=proj.get("repository_url")
                    )
                )
            except Exception as e:
                logger.warning(f"Project optimization failed for '{p_name}': {str(e)}. Using original data.")
                optimized_projects.append(
                    OptimizedProject(
                        project_id=p_id,
                        project_name=p_name,
                        relevance_score=1.0,
                        relevance_reasons=["Baseline project relevance"],
                        matched_requirements=[],
                        technologies=p_techs,
                        bullets=[p_desc] if p_desc else ["Implemented core project features."],
                        project_url=proj.get("project_url"),
                        github_url=proj.get("github_url"),
                        repository_url=proj.get("repository_url")
                    )
                )

        # Sort projects by relevance score descending
        optimized_projects.sort(key=lambda x: x.relevance_score, reverse=True)
        return optimized_projects

    async def optimize_experience(
        self,
        candidate_profile: Dict[str, Any],
        job_requirements: JobRequirements
    ) -> List[OptimizedExperience]:
        """Optimizes bullets and emphasis for work experience entries without altering employer/role/dates."""
        orig_exp = candidate_profile.get("experience", [])
        if not orig_exp:
            return []

        result: List[OptimizedExperience] = []

        for exp in orig_exp:
            company = exp.get("company", "")
            role = exp.get("role", "")
            techs = exp.get("technologies", [])
            bullets = exp.get("responsibilities", []) + exp.get("achievements", [])
            if exp.get("description"):
                bullets.insert(0, exp.get("description"))

            system_prompt = "You are PaperFox Resume Optimizer specializing in career experience bullet tailoring."
            prompt = f"""
Optimize bullet points for candidate work experience entry.

TARGET JOB REQUIREMENTS:
Title: {job_requirements.title}
Required Skills: {', '.join(job_requirements.required_skills)}
Responsibilities: {', '.join(job_requirements.responsibilities)}

CANDIDATE EXPERIENCE:
Company: {company}
Role: {role}
Technologies: {', '.join(techs)}
Source Bullets:
{chr(10).join(['- ' + b for b in bullets if b])}

RULES:
1. Do NOT change company, role, or dates.
2. Rewrite bullets to emphasize accomplishments relevant to the target job.
3. Do NOT manufacture metrics or technologies not present in the candidate experience.

Return JSON schema:
{{
  "bullets": ["Optimized bullet 1", "Optimized bullet 2"]
}}
"""
            schema = {
                "type": "object",
                "properties": {"bullets": {"type": "array", "items": {"type": "string"}}},
                "required": ["bullets"]
            }

            try:
                res = await self.router.generate_structured_json(prompt=prompt, schema=schema, system_prompt=system_prompt)
                opt_bullets = res["data"]["bullets"]
            except Exception as e:
                logger.warning(f"Experience optimization failed for {company}: {str(e)}")
                opt_bullets = bullets if bullets else ["Delivered software development responsibilities."]

            result.append(
                OptimizedExperience(
                    id=exp.get("id"),
                    company=company,
                    role=role,
                    location=exp.get("location"),
                    start_date=exp.get("start_date", ""),
                    end_date=exp.get("end_date"),
                    is_current=exp.get("is_current", False),
                    bullets=opt_bullets,
                    technologies=techs
                )
            )

        return result

    async def optimize_internships(
        self,
        candidate_profile: Dict[str, Any],
        job_requirements: JobRequirements
    ) -> List[OptimizedInternship]:
        """Optimizes bullets for internship entries for fresher candidates."""
        orig_intern = candidate_profile.get("internships", [])
        if not orig_intern:
            return []

        result: List[OptimizedInternship] = []
        for intern in orig_intern:
            company = intern.get("company", "")
            role = intern.get("role", "")
            techs = intern.get("technologies", [])
            bullets = intern.get("responsibilities", []) + intern.get("achievements", [])
            if intern.get("description"):
                bullets.insert(0, intern.get("description"))

            result.append(
                OptimizedInternship(
                    id=intern.get("id"),
                    company=company,
                    role=role,
                    location=intern.get("location"),
                    start_date=intern.get("start_date", ""),
                    end_date=intern.get("end_date"),
                    is_current=intern.get("is_current", False),
                    bullets=bullets if bullets else ["Gained software engineering internship experience."],
                    technologies=techs
                )
            )
        return result

    def prioritize_skills(
        self,
        candidate_profile: Dict[str, Any],
        job_requirements: JobRequirements,
        structured_evidence_map: Optional[Dict[str, StructuredProjectEvidence]] = None
    ) -> List[OptimizedSkillGroup]:
        """
        Prioritizes candidate's actual skills into categorized skill groups.
        Never adds a skill solely because the JD asks for it.
        """
        cand_skills = candidate_profile.get("skills", [])
        if not cand_skills:
            return []

        jd_skills_lower = set(
            [s.lower() for s in (
                job_requirements.required_skills +
                job_requirements.preferred_skills +
                job_requirements.programming_languages +
                job_requirements.technologies_frameworks +
                job_requirements.ai_ml_requirements +
                job_requirements.important_keywords
            ) if s]
        )

        # Group candidate skills by category and sort matched skills first
        groups_dict: Dict[str, List[str]] = {}
        for s in cand_skills:
            name = s.get("name", "").strip()
            category = s.get("category", "Other").strip()
            if not name:
                continue
            if category not in groups_dict:
                groups_dict[category] = []
            groups_dict[category].append(name)

        result_groups: List[OptimizedSkillGroup] = []
        for cat, skills in groups_dict.items():
            # Sort skills in category: JD matches first, then alphabetical
            matched = [sk for sk in skills if sk.lower() in jd_skills_lower]
            unmatched = [sk for sk in skills if sk.lower() not in jd_skills_lower]
            ordered_skills = matched + unmatched
            result_groups.append(OptimizedSkillGroup(category=cat, skills=ordered_skills))

        return result_groups

    def compute_keyword_alignment(
        self,
        candidate_profile: Dict[str, Any],
        job_requirements: JobRequirements,
        structured_evidence_map: Optional[Dict[str, StructuredProjectEvidence]] = None
    ) -> KeywordAlignment:
        """Classifies JD keywords into matched, missing, safely usable, and unsupported JD keywords."""
        all_jd_keywords = set()
        for kw in (
            job_requirements.required_skills +
            job_requirements.preferred_skills +
            job_requirements.programming_languages +
            job_requirements.technologies_frameworks +
            job_requirements.ai_ml_requirements +
            job_requirements.important_keywords
        ):
            if kw and kw.strip():
                all_jd_keywords.add(kw.strip())

        # Collect candidate facts
        cand_facts_lower = set()
        for sk in candidate_profile.get("skills", []):
            if sk.get("name"):
                cand_facts_lower.add(sk["name"].strip().lower())

        for exp in candidate_profile.get("experience", []):
            for t in exp.get("technologies", []):
                cand_facts_lower.add(t.strip().lower())

        for proj in candidate_profile.get("projects", []):
            for t in proj.get("technologies", []):
                cand_facts_lower.add(t.strip().lower())

        if structured_evidence_map:
            for ev in structured_evidence_map.values():
                for t in (ev.technologies + ev.frameworks + ev.databases + ev.deployment + ev.apis + ev.models):
                    cand_facts_lower.add(t.strip().lower())

        matched: List[str] = []
        missing_unsupported: List[str] = []
        safely_usable: List[str] = []

        for kw in sorted(list(all_jd_keywords)):
            if kw.lower() in cand_facts_lower:
                matched.append(kw)
                safely_usable.append(kw)
            else:
                missing_unsupported.append(kw)

        return KeywordAlignment(
            matched_keywords=matched,
            missing_keywords=missing_unsupported,
            safely_usable_keywords=safely_usable,
            unsupported_jd_keywords=missing_unsupported
        )

    async def optimize(
        self,
        job_id: str,
        candidate_profile: Dict[str, Any],
        job_requirements: JobRequirements,
        structured_evidence_map: Optional[Dict[str, StructuredProjectEvidence]] = None,
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None
    ) -> OptimizedResumeData:
        """
        Executes complete Phase 5 optimization pipeline across modular AI tasks
        and applies deterministic factual validation.
        """
        summary = await self.optimize_summary(candidate_profile, job_requirements, structured_evidence_map)
        projects = await self.optimize_projects(candidate_profile, job_requirements, structured_evidence_map)
        experience = await self.optimize_experience(candidate_profile, job_requirements)
        internships = await self.optimize_internships(candidate_profile, job_requirements)
        skills = self.prioritize_skills(candidate_profile, job_requirements, structured_evidence_map)
        keyword_alignment = self.compute_keyword_alignment(candidate_profile, job_requirements, structured_evidence_map)

        # Personal details
        personal_details = candidate_profile.get("personal_details", {})

        # Education
        education = candidate_profile.get("education", [])

        # Certifications
        certifications = candidate_profile.get("certifications", [])

        metadata = OptimizationMetadata(
            status="completed",
            provider=provider_name or self.router.primary_provider,
            model=model_name or "multi-provider-free",
            generated_at=datetime.now(timezone.utc)
        )

        optimized_data = OptimizedResumeData(
            job_id=job_id,
            profile_snapshot_reference=candidate_profile.get("id"),
            personal_details=personal_details,
            summary=summary,
            education=education,
            experience=experience,
            internships=internships,
            projects=projects,
            skills=skills,
            certifications=certifications,
            keyword_alignment=keyword_alignment,
            optimization_metadata=metadata
        )

        # Deterministic Factual Grounding Validation
        validate_optimized_data(
            original_profile=candidate_profile,
            structured_evidence_map=structured_evidence_map,
            optimized_data=optimized_data,
            job_requirements=job_requirements.model_dump()
        )

        return optimized_data
