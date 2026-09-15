from IPython.core import logger
import copy
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status
from app.repositories.job_repository import JobRepository
from app.repositories.profile_repository import ProfileRepository
from app.schemas.job import (
    JobApplicationCreate,
    JobApplicationResponse,
    JobRequirements
)
from app.schemas.optimization_schema import OptimizationResponse, OptimizedResumeData, StructuredProjectEvidence
from app.services.ai.optimizer_service import OptimizerService
from app.services.ai.project_evidence_parser import ProjectEvidenceParser
from app.services.ai.provider_router import ProviderRouter


class JobService:
    def __init__(
        self,
        job_repository: JobRepository,
        profile_repository: Optional[ProfileRepository] = None,
        router: Optional[ProviderRouter] = None
    ):
        self.job_repository = job_repository
        self.profile_repository = profile_repository
        self.router = router or ProviderRouter()

    def _doc_to_response(self, doc: Dict[str, Any]) -> JobApplicationResponse:
        reqs = None
        if doc.get("requirements"):
            try:
                reqs = JobRequirements(**doc["requirements"])
            except Exception:
                reqs = None

        return JobApplicationResponse(
            id=str(doc["_id"]),
            user_id=str(doc["user_id"]),
            company_name=doc["company_name"],
            role_title=doc["role_title"],
            job_description=doc["job_description"],
            job_url=doc.get("job_url"),
            location=doc.get("location"),
            requirements=reqs,
            analysis_provider=doc.get("analysis_provider"),
            analysis_model=doc.get("analysis_model"),
            is_analyzed=doc.get("is_analyzed", False),
            optimization=doc.get("optimization"),
            is_optimized=doc.get("is_optimized", False),
            job_resume_artifact=doc.get("job_resume_artifact"),
            is_resume_generated=doc.get("is_resume_generated", False),
            # Phase 7: application lifecycle
            application_status=doc.get("application_status", "draft"),
            notes=doc.get("notes"),
            status_updated_at=doc.get("status_updated_at"),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"]
        )

    async def create_job(self, user_id: str, job_in: JobApplicationCreate) -> JobApplicationResponse:
        doc = await self.job_repository.create_job(user_id, job_in.model_dump())
        return self._doc_to_response(doc)

    async def get_job(self, user_id: str, job_id: str) -> JobApplicationResponse:
        doc = await self.job_repository.get_by_id(job_id, user_id)
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job application not found")
        return self._doc_to_response(doc)

    async def list_jobs(self, user_id: str) -> List[JobApplicationResponse]:
        docs = await self.job_repository.list_by_user_id(user_id)
        return [self._doc_to_response(d) for d in docs]

    async def delete_job(self, user_id: str, job_id: str) -> bool:
        existing = await self.job_repository.get_by_id(job_id, user_id)
        if not existing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job application not found")
        return await self.job_repository.delete_job(job_id, user_id)

    async def analyze_job(self, user_id: str, job_id: str) -> JobApplicationResponse:
        doc = await self.job_repository.get_by_id(job_id, user_id)
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job application not found")

        system_prompt = "You are PaperFox JD Intelligence, an expert career and resume optimization AI."
        prompt = f"""
Analyze the following Job Description and extract structured information into JSON format.

Return ONLY a valid JSON object matching this schema:
{{
  "title": "Job Title",
  "experience_years_required": number (e.g. 5, or null if unspecified),
  "education_required": "Education or degree requirement",
  "required_skills": ["Mandatory skill 1", "Mandatory skill 2"],
  "preferred_skills": ["Nice-to-have skill 1", "Nice-to-have skill 2"],
  "programming_languages": ["Python", "TypeScript"],
  "technologies_frameworks": ["FastAPI", "React", "Docker", "PostgreSQL"],
  "ai_ml_requirements": ["LLMs", "PyTorch", "LangChain"],
  "responsibilities": ["Core responsibility 1", "Core responsibility 2"],
  "important_keywords": ["ATS Keyword 1", "ATS Keyword 2"]
}}

Rules:
1. Extract ONLY facts present in the Job Description. Do NOT invent skills or tools not mentioned.
2. Separate mandatory skills (required_skills) from nice-to-haves (preferred_skills).

Company: {doc['company_name']}
Role: {doc['role_title']}
Job Description:
{doc['job_description']}
"""
        schema = JobRequirements.model_json_schema()

        ai_res = await self.router.generate_structured_json(
            prompt=prompt, schema=schema, system_prompt=system_prompt
        )

        raw_json = ai_res["data"]
        try:
            reqs = JobRequirements(**raw_json)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI output failed JobRequirements schema validation: {str(e)}"
            )

        update_data = {
            "requirements": reqs.model_dump(),
            "analysis_provider": ai_res["provider"],
            "analysis_model": ai_res["model"],
            "is_analyzed": True
        }

        updated_doc = await self.job_repository.update_job(job_id, user_id, update_data)
        return self._doc_to_response(updated_doc)

    async def optimize_job(self, user_id: str, job_id: str) -> OptimizationResponse:
        doc = await self.job_repository.get_by_id(job_id, user_id)
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job application not found")

        if not doc.get("is_analyzed") or not doc.get("requirements"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job application must be analyzed before running resume optimization."
            )

        if not self.profile_repository:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Profile repository not injected into JobService."
            )

        profile_doc = await self.profile_repository.get_by_user_id(user_id)
        if not profile_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate profile not found. Complete your master profile before running optimization."
            )

        # IMMUTABLE SNAPSHOT: Create deep copy of Master Candidate Profile
        profile_snapshot = copy.deepcopy(profile_doc)
        job_reqs = JobRequirements(**doc["requirements"])

        # Parse Project AI Analysis into Structured Evidence
        # Phase 7 optimization: prefer stored evidence over re-extraction
        evidence_parser = ProjectEvidenceParser(self.router)
        structured_evidence_map: Dict[str, StructuredProjectEvidence] = {}

        for proj in profile_snapshot.get("projects", []):
            p_name = proj.get("name", "Project")

            # 1. Use stored current evidence if available (avoids duplicate AI calls)
            stored_evidence = proj.get("evidence")
            stored_status = proj.get("evidence_status")
            if stored_evidence and stored_status == "current":
                try:
                    ev = StructuredProjectEvidence(**stored_evidence)
                    structured_evidence_map[p_name] = ev
                    continue  # Skip re-extraction
                except Exception:
                    pass  # Fallback to fresh extraction below

            # 2. Fallback: extract from raw ai_analysis_text
            ai_text = proj.get("ai_analysis_text")
            if ai_text and ai_text.strip():
                ev = await evidence_parser.parse_analysis_text(p_name, ai_text)
                structured_evidence_map[p_name] = ev

        optimizer = OptimizerService(self.router)
        try:
            optimized_data = await optimizer.optimize(
                job_id=job_id,
                candidate_profile=profile_snapshot,
                job_requirements=job_reqs,
                structured_evidence_map=structured_evidence_map
            )
        except Exception as e:
            # On failure, preserve existing optimization if present
            err_msg = f"Optimization pipeline failed: {str(e)}"
            if doc.get("optimization"):
                logger.error(f"{err_msg}. Preserving previous valid optimization.")
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=err_msg)

        opt_dump = optimized_data.model_dump()
        update_data = {
            "optimization": opt_dump,
            "is_optimized": True
        }
        await self.job_repository.update_job(job_id, user_id, update_data)

        return OptimizationResponse(
            job_id=job_id,
            company_name=doc["company_name"],
            role_title=doc["role_title"],
            status="completed",
            optimized_resume_data=optimized_data
        )

    async def get_job_optimization(self, user_id: str, job_id: str) -> OptimizationResponse:
        doc = await self.job_repository.get_by_id(job_id, user_id)
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job application not found")

        if not doc.get("optimization"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No resume optimization found for this job application."
            )

        opt_data = OptimizedResumeData(**doc["optimization"])
        return OptimizationResponse(
            job_id=job_id,
            company_name=doc["company_name"],
            role_title=doc["role_title"],
            status=opt_data.optimization_metadata.status,
            optimized_resume_data=opt_data
        )
