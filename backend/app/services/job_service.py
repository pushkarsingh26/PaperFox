from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status
from app.repositories.job_repository import JobRepository
from app.schemas.job import (
    JobApplicationCreate,
    JobApplicationResponse,
    JobRequirements
)
from app.services.ai.provider_router import ProviderRouter


class JobService:
    def __init__(self, job_repository: JobRepository, router: Optional[ProviderRouter] = None):
        self.job_repository = job_repository
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

        # Execute Provider Router
        ai_res = await self.router.generate_structured_json(
            prompt=prompt, schema=schema, system_prompt=system_prompt
        )

        # Validate with JobRequirements schema
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
