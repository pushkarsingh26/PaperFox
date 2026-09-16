import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.schemas.job import JobRequirements, SuggestedMissingSkill
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

SKILL_NORMALIZATIONS = {
    "sckit-learn": "Scikit-learn",
    "scikit learn": "Scikit-learn",
    "scikitlearn": "Scikit-learn",
    "sklearn": "Scikit-learn",
    "llamma": "Llama",
    "llama": "Llama",
    "llama2": "Llama 2",
    "llama 2": "Llama 2",
    "llama3": "Llama 3",
    "llama 3": "Llama 3",
    "generativeai": "Generative AI",
    "generative-ai": "Generative AI",
    "generative ai": "Generative AI",
    "genai": "Generative AI",
    "gen ai": "Generative AI",
    "langchain": "LangChain",
    "fastapi": "FastAPI",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "elasticsearch": "Elasticsearch",
    "faiss": "FAISS",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "Google Cloud",
    "google cloud platform": "Google Cloud",
    "google cloud": "Google Cloud",
    "azure": "Azure",
    "microsoft azure": "Azure",
    "git": "Git",
    "github": "GitHub",
    "github actions": "GitHub Actions",
    "rest": "REST APIs",
    "rest api": "REST APIs",
    "rest apis": "REST APIs",
    "restful": "REST APIs",
    "restful api": "REST APIs",
    "restful apis": "REST APIs",
    "rag": "RAG",
    "retrieval-augmented generation": "RAG",
    "retrieval augmented generation": "RAG",
    "llm": "LLMs",
    "llms": "LLMs",
    "large language models": "LLMs",
    "nlp": "NLP",
    "natural language processing": "NLP",
    "deep learning": "Deep Learning",
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "node": "Node.js",
    "typescript": "TypeScript",
    "javascript": "JavaScript",
    "python": "Python",
    "sql": "SQL",
    "nosql": "NoSQL",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
}


def normalize_skill(skill: str) -> str:
    """Normalizes skill names to canonical casing and resolves common abbreviations/synonyms."""
    if not skill or not skill.strip():
        return ""
    cleaned = skill.strip()
    return SKILL_NORMALIZATIONS.get(cleaned.lower(), cleaned)


def sanitize_project_bullets(bullets: List[str], tech_stack: Optional[List[str]] = None) -> List[str]:
    """
    Cleans project bullets:
    - Strips markdown bolding
    - Eliminates generic AI buzzwords (AI-powered, intelligent, robust, etc.)
    - Removes redundant technology repetitions across bullets within the same project
    - Ensures clean capitalization and punctuation
    """
    cleaned_bullets: List[str] = []
    used_techs = set()
    effective_techs = tech_stack or []
    buzzwords = [
        r"\bAI-powered\b", r"\bGenAI-powered\b", r"\bintelligent\b", r"\bsophisticated\b",
        r"\brobust\b", r"\badvanced\b", r"\bscalable\b", r"\binnovative\b",
        r"\bcutting-edge\b", r"\bseamless\b", r"\bpowerful\b"
    ]

    for b in bullets:
        text = b.strip()
        if not text:
            continue

        # 1. Remove markdown bolding
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
        text = re.sub(r"\*([^*]+)\*", r"\1", text)

        # 2. Strip generic buzzwords
        for bw in buzzwords:
            text = re.sub(bw, "", text, flags=re.IGNORECASE)

        # 3. Clean up double spaces or awkward punctuation from removed words
        text = re.sub(r"\s+", " ", text).strip()
        text = re.sub(r"\s+([,.;])", r"\1", text)

        # 4. Check for repeated technology mentions across bullets
        for t in effective_techs:
            if len(t) > 3:
                pattern = rf"\b{re.escape(t)}\b"
                if re.search(pattern, text, flags=re.IGNORECASE):
                    t_lower = t.lower()
                    if t_lower in used_techs:
                        # Remove redundant "using/with [Tech]" phrases in subsequent bullets
                        text = re.sub(rf"\b(?:using|with)\s+{re.escape(t)}\b", "", text, flags=re.IGNORECASE)
                        text = re.sub(r"\s+", " ", text).strip()
                        text = re.sub(r"\s+([,.;])", r"\1", text)
                    else:
                        used_techs.add(t_lower)

        # Ensure starts with capital letter and ends with period
        if text:
            text = text[0].upper() + text[1:]
            if not text.endswith("."):
                text = text + "."
            cleaned_bullets.append(text)

    return cleaned_bullets


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
        structured_evidence_map: Optional[Dict[str, StructuredProjectEvidence]] = None,
        approved_additional_skills: Optional[List[str]] = None
    ) -> str:
        """Generates a job-specific professional summary strictly grounded in candidate facts and confirmed skills."""
        personal = candidate_profile.get("personal_details", {})
        cand_name = personal.get("full_name", "")
        verified_skills = [s.get("name", "") for s in candidate_profile.get("skills", []) if s.get("name")]
        confirmed_skills = [s.strip() for s in (approved_additional_skills or []) if s and s.strip()]

        all_skills_list = verified_skills + [s for s in confirmed_skills if s.lower() not in [v.lower() for v in verified_skills]]
        skills_str = ", ".join(all_skills_list)
        confirmed_skills_str = ", ".join(confirmed_skills)

        # Summarize key project context (prioritizing concrete technical implementations)
        proj_summaries = []
        for p in candidate_profile.get("projects", []):
            name = p.get("name", "")
            techs = ", ".join(p.get("technologies", []))
            desc = p.get("description", "")
            ev = structured_evidence_map.get(name) if structured_evidence_map else None
            ev_str = f" Evidence: {', '.join(ev.technologies + ev.frameworks)}" if ev else ""
            proj_summaries.append(f"- {name}: {desc} (Tech: {techs}{ev_str})")
        proj_context = "\n".join(proj_summaries)

        system_prompt = "You are PaperFox Resume Optimizer, an expert executive technical resume writer."
        prompt = f"""
Generate a concise, high-impact Professional Summary (approximately 3 to 4 lines, 2 to 3 sentences) tailored specifically for the target role.

TARGET ROLE INFORMATION:
Title: {job_requirements.title or 'Software Engineer'}
Required Skills: {', '.join(job_requirements.required_skills)}
Technologies: {', '.join(job_requirements.technologies_frameworks)}
AI/ML Requirements: {', '.join(job_requirements.ai_ml_requirements)}

CANDIDATE VERIFIED EVIDENCE:
Core Verified Skills: {', '.join(verified_skills)}
Confirmed Job-Specific Skills: {confirmed_skills_str if confirmed_skills_str else 'None'}
Candidate Type: {candidate_profile.get('candidate_type', 'experienced')}
Key Projects & Evidence:
{proj_context}

CRITICAL RULES:
1. NEVER WRITE THE CANDIDATE'S NAME. Do not include any person's name anywhere in the summary.
2. NEVER WRITE IN THE THIRD PERSON. Absolutely NO "He is", "She is", "The candidate is", "[Name] is", etc.
3. DO NOT USE AWKWARD PHRASES such as "fresh Junior AI Engineer", "enthusiastic beginner", or "aspiring developer".
4. WRITE IN CONCISE, PROFESSIONAL RESUME LANGUAGE with implied first-person (e.g., "Software Engineer specializing in...", "AI Engineer with hands-on experience building...").
5. TARGET APPROXIMATELY 3-4 LINES (2-3 punchy, high-signal sentences).
6. COMMUNICATE:
   - Candidate positioning (e.g., technical domain / engineering focus)
   - Core relevant technical capabilities aligned with the role
   - Relevant AI/backend/domain expertise grounded in actual projects
   - Strongest evidence-backed technical specialization
7. GROUNDING & TRUTH:
   - Ground every statement strictly in the candidate's verified skills, project implementations, and confirmed skills.
   - Do NOT introduce technologies, metrics, deployment claims, or responsibilities unless supported by candidate evidence.
   - Do not dump the entire candidate profile; select only the most relevant verified elements.
8. PLAIN TEXT ONLY: Absolutely NO markdown bolding (**word**), double asterisks, or LaTeX commands.

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
            raw_summary = res["data"]["summary"].strip()

            # Deterministic sanitization
            cleaned_summary = raw_summary
            # Remove markdown bolding/italics
            cleaned_summary = re.sub(r"\*\*([^*]+)\*\*", r"\1", cleaned_summary)
            cleaned_summary = re.sub(r"\*([^*]+)\*", r"\1", cleaned_summary)

            # Strip awkward phrases
            cleaned_summary = re.sub(r"\bfresh\s+Junior\b", "Junior", cleaned_summary, flags=re.IGNORECASE)

            # Strip candidate name if present
            if cand_name and cand_name.strip():
                name_pattern = re.escape(cand_name.strip())
                cleaned_summary = re.sub(rf"^{name_pattern}\s+(?:is\s+(?:a|an)\s+|is\s+)", "", cleaned_summary, flags=re.IGNORECASE)
                first_name = cand_name.strip().split()[0]
                if len(first_name) > 2:
                    cleaned_summary = re.sub(rf"^{re.escape(first_name)}\s+(?:is\s+(?:a|an)\s+|is\s+)", "", cleaned_summary, flags=re.IGNORECASE)

            # Strip any generic third person starts: e.g. "He is an AI Engineer...", "The candidate is a..."
            cleaned_summary = re.sub(r"^(?:(?:He|She|The candidate)\s+(?:is\s+(?:a|an)\s+|is\s+))", "", cleaned_summary, flags=re.IGNORECASE)
            cleaned_summary = re.sub(r"^(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:is\s+(?:a|an)\s+|is\s+))", "", cleaned_summary)

            # Capitalize first letter
            if cleaned_summary:
                cleaned_summary = cleaned_summary[0].upper() + cleaned_summary[1:]

            return cleaned_summary.strip()
        except Exception as e:
            logger.warning(f"Summary optimization failed: {str(e)}. Using fallback profile summary.")
            fallback_tech = skills_str[:90] if skills_str else "AI engineering and backend architectures"
            role_target = job_requirements.title or "engineering roles"
            return f"Software Engineer specializing in {fallback_tech}, with hands-on experience designing and building scalable systems and intelligent applications tailored for {role_target}."

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

            system_prompt = "You are PaperFox Resume Optimizer, an elite technical resume engineer who maximizes engineering information density while eliminating repetition."
            prompt = f"""
Optimize project bullets for the target job requirements strictly grounded in candidate verified facts.

TARGET JOB REQUIREMENTS:
Title: {job_requirements.title}
Required Skills: {', '.join(job_requirements.required_skills)}
Key Technologies: {', '.join(job_requirements.technologies_frameworks)}
Important Keywords: {', '.join(job_requirements.important_keywords)}

CANDIDATE PROJECT:
Name: {p_name}
Manual Description: {p_desc}
Technologies: {', '.join(p_techs)}
Features: {', '.join(proj.get('features', []))}
Responsibilities: {', '.join(proj.get('responsibilities', []))}
{ev_context}

PROJECT BULLET ARCHITECTURE RULES:
1. DISTRIBUTE EVIDENCE ACROSS 4 DISTINCT DIMENSIONS:
   - Bullet 1 (ARCHITECTURE / PURPOSE): What the system does, core architecture, and overall engineering purpose.
   - Bullet 2 (LOGIC / RETRIEVAL / ALGORITHMS): How model/retrieval/agent/algorithmic logic functions (e.g. semantic indexing, vector search, embeddings, parsing, orchestration).
   - Bullet 3 (BACKEND / INFRASTRUCTURE): Backend services, APIs, databases, data persistence, and schemas (e.g. REST endpoints, SQLAlchemy, PostgreSQL, async pipelines).
   - Bullet 4 (PERFORMANCE / RELIABILITY / RESULTS): Evaluation, streaming, concurrency, reliability, throughput, or deployment (e.g. SSE streaming, error recovery, limits).
   Only include dimensions supported by the candidate's verified evidence above.

2. ZERO REDUNDANCY & NO REPEATING TECHNOLOGIES:
   - The technology stack ({', '.join(p_techs)}) is ALREADY displayed directly beneath the project title on the resume.
   - Do NOT repeat the same technology (e.g. FastAPI, LangChain, RAG) across multiple bullets.
   - Mention a technology inside a bullet ONLY when it provides meaningful engineering context for that specific bullet.
   - NEVER write redundant tautologies like "Built a FastAPI application using FastAPI" or "Implemented LangChain RAG using LangChain".

3. ZERO GENERIC AI BUZZWORDS:
   - Absolutely FORBIDDEN words: "AI-powered", "GenAI-powered", "intelligent", "sophisticated", "robust", "advanced", "scalable", "innovative", "cutting-edge", "seamless", "powerful".
   - Use concrete technical facts and mechanisms instead of marketing adjectives.

4. VARY BULLET OPENING VERBS NATURALLY:
   - Do NOT mechanically start bullets with "Built... Developed... Implemented... Engineered...".
   - Select verbs based on the actual technical action: Designed, Implemented, Integrated, Developed, Created, Automated, Optimized, Streamed, Persisted, Orchestrated, Configured, Evaluated, Architected.

5. PRESERVE CONCRETE VERIFIED DETAILS:
   - Preserve verified technical specifics from the evidence (e.g. SSE, FAISS, SentenceTransformers, all-MiniLM-L6-v2, PostgreSQL, SQLAlchemy, REST endpoints, concrete metrics).
   - Do NOT invent metrics, deployment platforms, or features not in the evidence.

6. ABSOLUTELY NO BOLDING:
   - Do NOT use markdown bold (**word**), double asterisks, or LaTeX \\textbf{{}}. Plain normal-weight text only.

Return JSON schema:
{{
  "relevance_score": 0.9,
  "relevance_reasons": ["Short technical alignment reason"],
  "matched_requirements": ["Matched skills"],
  "bullets": [
    "Distinct bullet 1 (Architecture/Purpose)",
    "Distinct bullet 2 (Retrieval/Model logic)",
    "Distinct bullet 3 (Backend/Database/Infrastructure)",
    "Distinct bullet 4 (Performance/Streaming/Reliability)"
  ]
}}
"""
            schema = {
                "type": "object",
                "properties": {
                    "relevance_score": {"type": "number"},
                    "relevance_reasons": {"type": "array", "items": {"type": "string"}},
                    "matched_requirements": {"type": "array", "items": {"type": "string"}},
                    "bullets": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["relevance_score", "bullets"]
            }

            try:
                res = await self.router.generate_structured_json(prompt=prompt, schema=schema, system_prompt=system_prompt)
                data = res["data"]

                # Preserve full verified project technology stack, ordering JD-matching technologies first
                verified_techs_map = {}
                for t in p_techs:
                    if t and t.strip():
                        verified_techs_map[t.strip().lower()] = t.strip()
                if ev:
                    for t in (ev.technologies + ev.frameworks + ev.databases + ev.deployment + ev.apis + ev.models):
                        if t and t.strip() and t.strip().lower() not in verified_techs_map:
                            verified_techs_map[t.strip().lower()] = t.strip()

                jd_tech_keywords = set([
                    k.lower() for k in (
                        job_requirements.technologies_frameworks +
                        job_requirements.required_skills +
                        job_requirements.important_keywords
                    ) if k
                ])

                matched_techs = [t for k, t in verified_techs_map.items() if k in jd_tech_keywords]
                unmatched_techs = [t for k, t in verified_techs_map.items() if k not in jd_tech_keywords]
                final_techs = matched_techs + unmatched_techs
                if not final_techs:
                    final_techs = p_techs

                raw_bullets = data.get("bullets", [p_desc] if p_desc else ["Implemented software solution."])
                clean_bullets = sanitize_project_bullets(raw_bullets, final_techs)

                optimized_projects.append(
                    OptimizedProject(
                        project_id=p_id,
                        project_name=p_name,
                        relevance_score=float(data.get("relevance_score", 1.0)),
                        relevance_reasons=data.get("relevance_reasons", []),
                        matched_requirements=data.get("matched_requirements", []),
                        technologies=final_techs,
                        bullets=clean_bullets if clean_bullets else raw_bullets,
                        project_url=proj.get("project_url"),
                        github_url=proj.get("github_url"),
                        repository_url=proj.get("repository_url")
                    )
                )
            except Exception as e:
                logger.warning(f"Project optimization failed for '{p_name}': {str(e)}. Using original data.")
                clean_fallback = sanitize_project_bullets([p_desc] if p_desc else ["Implemented core project features."], p_techs)
                optimized_projects.append(
                    OptimizedProject(
                        project_id=p_id,
                        project_name=p_name,
                        relevance_score=1.0,
                        relevance_reasons=["Baseline project relevance"],
                        matched_requirements=[],
                        technologies=p_techs,
                        bullets=clean_fallback if clean_fallback else [p_desc],
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
        structured_evidence_map: Optional[Dict[str, StructuredProjectEvidence]] = None,
        approved_additional_skills: Optional[List[str]] = None
    ) -> List[OptimizedSkillGroup]:
        """
        Prioritizes candidate's actual skills into categorized skill groups.
        Includes candidate-approved additional missing skills if provided.
        """
        cand_skills = list(candidate_profile.get("skills", []))
        if approved_additional_skills:
            existing_names = set([s.get("name", "").strip().lower() for s in cand_skills if s.get("name")])
            for app_skill in approved_additional_skills:
                if app_skill and app_skill.strip() and app_skill.strip().lower() not in existing_names:
                    cand_skills.append({"category": "Developer Tools" if "git" in app_skill.lower() else "Technical Skills", "name": app_skill.strip()})
                    existing_names.add(app_skill.strip().lower())

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
            raw_name = s.get("name", "").strip()
            if not raw_name:
                continue
            name = normalize_skill(raw_name)
            category = s.get("category", "Other").strip()
            if category not in groups_dict:
                groups_dict[category] = []
            if name not in groups_dict[category]:
                groups_dict[category].append(name)

        result_groups: List[OptimizedSkillGroup] = []
        for cat, skills in groups_dict.items():
            # Sort skills in category: JD matches first, then alphabetical
            matched = [sk for sk in skills if sk.lower() in jd_skills_lower]
            unmatched = [sk for sk in skills if sk.lower() not in jd_skills_lower]
            ordered_skills = matched + unmatched
            result_groups.append(OptimizedSkillGroup(category=cat, skills=ordered_skills))

        return result_groups

    async def analyze_critical_missing_skills(
        self,
        candidate_profile: Dict[str, Any],
        job_requirements: JobRequirements,
        structured_evidence_map: Optional[Dict[str, StructuredProjectEvidence]] = None
    ) -> List[SuggestedMissingSkill]:
        """
        Calculates normalized missing skills (JD Skills MINUS Verified Candidate Skills)
        and uses AI strictly to categorize each missing skill into the candidate's existing skill headings.
        Does NOT filter by importance or decide which skills the candidate must add.
        The candidate decides.
        """
        # 1. Collect all normalized verified candidate facts
        cand_facts_normalized = set()
        for sk in candidate_profile.get("skills", []):
            if sk.get("name"):
                cand_facts_normalized.add(normalize_skill(sk["name"]).lower())
        for exp in candidate_profile.get("experience", []) + candidate_profile.get("internships", []):
            for t in exp.get("technologies", []):
                cand_facts_normalized.add(normalize_skill(t).lower())
        for proj in candidate_profile.get("projects", []):
            for t in proj.get("technologies", []):
                cand_facts_normalized.add(normalize_skill(t).lower())
        if structured_evidence_map:
            for ev in structured_evidence_map.values():
                for t in (ev.technologies + ev.frameworks + ev.databases + ev.deployment + ev.apis + ev.models):
                    cand_facts_normalized.add(normalize_skill(t).lower())

        # 2. Extract existing skill categories from candidate profile dynamically
        profile_categories = []
        for s in candidate_profile.get("skills", []):
            cat = s.get("category", "").strip()
            if cat and cat not in profile_categories:
                profile_categories.append(cat)
        if not profile_categories:
            profile_categories = [
                "Programming / Languages", "AI & Machine Learning", "Frameworks & Libraries",
                "Databases", "Developer Tools"
            ]

        # 3. Collect and normalize all JD skills
        generic_filter = {
            "communication", "teamwork", "problem solving", "leadership", "fast learner",
            "agile", "scrum", "collaboration", "analytical skills", "critical thinking",
            "work ethic", "attention to detail", "written communication", "verbal communication"
        }

        missing_skills_list: List[str] = []
        seen_normalized = set()

        raw_jd_skills = (
            job_requirements.required_skills +
            job_requirements.programming_languages +
            job_requirements.technologies_frameworks +
            job_requirements.ai_ml_requirements +
            job_requirements.important_keywords
        )

        for sk in raw_jd_skills:
            if not sk or not sk.strip():
                continue
            canonical = normalize_skill(sk.strip())
            c_lower = canonical.lower()
            if c_lower in generic_filter:
                continue
            if c_lower not in cand_facts_normalized and c_lower not in seen_normalized:
                seen_normalized.add(c_lower)
                missing_skills_list.append(canonical)

        if not missing_skills_list:
            return []

        # 4. Use AI ONLY to map missing skills to candidate's existing categories
        system_prompt = "You are PaperFox Skill Categorizer. Your ONLY task is to map missing skills into the candidate's existing skill headings."
        prompt = f"""
Categorize each missing skill into one of the candidate's existing skill categories.

CANDIDATE'S EXISTING SKILL CATEGORIES:
{', '.join(profile_categories)}

MISSING SKILLS TO CATEGORIZE:
{', '.join(missing_skills_list)}

RULES:
1. Map each missing skill to the closest matching category from the candidate's existing categories list.
2. If a skill does not fit any existing category, assign it to "Other Relevant Skills".
3. Do NOT invent new categories unless none of the existing categories can apply.
4. Categorize EVERY missing skill in the list. Do NOT omit any skill.
5. Do NOT rate importance or decide if the candidate should add it. Only categorize.

Return JSON schema:
{{
  "categorized_skills": [
    {{
      "skill": "Skill Name",
      "category": "Category Name"
    }}
  ]
}}
"""
        schema = {
            "type": "object",
            "properties": {
                "categorized_skills": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "skill": {"type": "string"},
                            "category": {"type": "string"}
                        },
                        "required": ["skill", "category"]
                    }
                }
            },
            "required": ["categorized_skills"]
        }

        try:
            res = await self.router.generate_structured_json(prompt=prompt, schema=schema, system_prompt=system_prompt)
            items = res["data"].get("categorized_skills", [])
            mapped_dict = {}
            for item in items:
                s_name = normalize_skill(item.get("skill", "").strip())
                cat = item.get("category", "Other Relevant Skills").strip()
                if s_name:
                    mapped_dict[s_name.lower()] = cat

            results: List[SuggestedMissingSkill] = []
            for s in missing_skills_list:
                assigned_cat = mapped_dict.get(s.lower(), profile_categories[0] if profile_categories else "Other Relevant Skills")
                results.append(SuggestedMissingSkill(
                    skill=s,
                    name=s,
                    category=assigned_cat,
                    importance="",
                    reason="",
                    is_critical=False
                ))
            return results
        except Exception as e:
            logger.warning(f"AI skill categorization failed: {str(e)}. Using heuristic categorization.")
            results = []
            for s in missing_skills_list:
                cat = profile_categories[0] if profile_categories else "Other Relevant Skills"
                s_low = s.lower()
                for c in profile_categories:
                    c_low = c.lower()
                    if ("tool" in c_low or "devops" in c_low or "cloud" in c_low) and s_low in ("docker", "kubernetes", "aws", "gcp", "git", "ci/cd"):
                        cat = c
                        break
                    elif "data" in c_low and s_low in ("mongodb", "postgresql", "redis", "mysql", "elasticsearch", "sql"):
                        cat = c
                        break
                    elif ("lang" in c_low or "program" in c_low) and s_low in ("python", "java", "c#", "go", "typescript", "javascript", "c++"):
                        cat = c
                        break
                    elif ("ai" in c_low or "learn" in c_low or "llm" in c_low) and s_low in ("pytorch", "tensorflow", "scikit-learn", "langchain", "llama", "llms"):
                        cat = c
                        break

                results.append(SuggestedMissingSkill(
                    skill=s,
                    name=s,
                    category=cat,
                    importance="",
                    reason="",
                    is_critical=False
                ))
            return results

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
        approved_additional_skills: Optional[List[str]] = None,
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None
    ) -> OptimizedResumeData:
        """
        Executes complete Phase 5 optimization pipeline across modular AI tasks
        and applies deterministic factual validation.
        """
        summary = await self.optimize_summary(
            candidate_profile,
            job_requirements,
            structured_evidence_map,
            approved_additional_skills=approved_additional_skills
        )
        projects = await self.optimize_projects(candidate_profile, job_requirements, structured_evidence_map)
        experience = await self.optimize_experience(candidate_profile, job_requirements)
        internships = await self.optimize_internships(candidate_profile, job_requirements)
        skills = self.prioritize_skills(candidate_profile, job_requirements, structured_evidence_map, approved_additional_skills=approved_additional_skills)
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
            section_order=candidate_profile.get("section_order"),
            keyword_alignment=keyword_alignment,
            optimization_metadata=metadata
        )

        # Deterministic Factual Grounding Validation
        validate_optimized_data(
            original_profile=candidate_profile,
            structured_evidence_map=structured_evidence_map,
            optimized_data=optimized_data,
            job_requirements=job_requirements.model_dump(),
            approved_additional_skills=approved_additional_skills
        )

        return optimized_data
