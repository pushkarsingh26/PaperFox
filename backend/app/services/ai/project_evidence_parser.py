import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from app.schemas.optimization_schema import StructuredProjectEvidence
from app.services.ai.provider_router import ProviderRouter

logger = logging.getLogger(__name__)


class ProjectEvidenceParser:
    """
    Parses plain-text external coding-AI analysis (ai_analysis_text) into a structured JSON schema.
    Uses the multi-provider FREE-model AI router.
    """

    def __init__(self, router: Optional[ProviderRouter] = None):
        self.router = router or ProviderRouter()

    async def parse_analysis_text(self, project_name: str, ai_analysis_text: str) -> StructuredProjectEvidence:
        if not ai_analysis_text or not ai_analysis_text.strip():
            return StructuredProjectEvidence(verified_at=datetime.now(timezone.utc).isoformat())

        system_prompt = "You are PaperFox Evidence Extractor, a factual software architecture parser."
        prompt = f"""
Extract verified technical implementation evidence from the following plain-text project codebase analysis into JSON format.

PROJECT NAME:
{project_name}

RAW PLAIN-TEXT ANALYSIS:
{ai_analysis_text}

TASK:
Categorize the technical details into structured lists.

CRITICAL FACTUAL GROUNDING RULES:
1. Extract ONLY technologies, frameworks, APIs, databases, models, features, architecture patterns, deployment methods, technical details, engineering decisions, and limitations that are explicitly mentioned as PRESENT or VERIFIED in the analysis.
2. If something is explicitly noted as "unverified", "not found", or "missing", do NOT include it in technologies/frameworks/databases/etc. You may list it under "limitations".
3. Do NOT invent or assume any technology that is not mentioned in the plain-text analysis.

Return ONLY a valid JSON object matching this schema:
{{
  "architecture": ["microservices", "monolith", "event-driven"],
  "technologies": ["Python", "TypeScript"],
  "frameworks": ["FastAPI", "React", "Next.js"],
  "apis": ["REST", "GraphQL", "Stripe API"],
  "models": ["gemini-2.5-flash", "BERT"],
  "databases": ["MongoDB", "PostgreSQL", "Redis"],
  "deployment": ["Docker", "AWS ECS", "Vercel"],
  "features": ["User Auth", "PDF Rendering"],
  "technical_details": ["JWT auth flow", "latexmk compilation pipeline"],
  "engineering_decisions": ["Used PyPDF2 for page count calculation"],
  "limitations": ["Kubernetes cluster deployment was unverified"]
}}
"""
        schema = StructuredProjectEvidence.model_json_schema()

        try:
            ai_res = await self.router.generate_structured_json(
                prompt=prompt, schema=schema, system_prompt=system_prompt
            )
            data = ai_res["data"]
            data["verified_at"] = datetime.now(timezone.utc).isoformat()
            return StructuredProjectEvidence(**data)
        except Exception as e:
            logger.error(f"Failed to parse project evidence for '{project_name}': {str(e)}")
            # Fallback to empty evidence with timestamp
            return StructuredProjectEvidence(verified_at=datetime.now(timezone.utc).isoformat())
