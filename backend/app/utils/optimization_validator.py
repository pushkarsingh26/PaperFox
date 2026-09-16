import re
from typing import Any, Dict, List, Set, Optional
from app.schemas.optimization_schema import OptimizedResumeData, StructuredProjectEvidence


def _normalize(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]", "", s).lower()


def _collect_candidate_fact_tokens(
    original_profile: Dict[str, Any],
    structured_evidence_map: Optional[Dict[str, StructuredProjectEvidence]] = None
) -> Set[str]:
    """
    Collects normalized tokens and string representations of all verified candidate facts:
    skills, technologies, frameworks, APIs, databases, models, deployment tools, etc.
    """
    facts: Set[str] = set()

    def add_fact(val: Any):
        if not val:
            return
        if isinstance(val, str):
            cleaned = val.strip()
            if cleaned:
                facts.add(cleaned.lower())
                facts.add(_normalize(cleaned))
        elif isinstance(val, list):
            for item in val:
                add_fact(item)

    # 1. Direct candidate skills
    for s in original_profile.get("skills", []):
        add_fact(s.get("name"))

    # 2. Work Experience
    for exp in original_profile.get("experience", []):
        add_fact(exp.get("company"))
        add_fact(exp.get("role"))
        add_fact(exp.get("technologies"))
        add_fact(exp.get("responsibilities"))
        add_fact(exp.get("achievements"))
        add_fact(exp.get("description"))

    # 3. Internships
    for intern in original_profile.get("internships", []):
        add_fact(intern.get("company"))
        add_fact(intern.get("role"))
        add_fact(intern.get("technologies"))
        add_fact(intern.get("responsibilities"))
        add_fact(intern.get("achievements"))
        add_fact(intern.get("description"))

    # 4. Education
    for edu in original_profile.get("education", []):
        add_fact(edu.get("institution"))
        add_fact(edu.get("degree"))
        add_fact(edu.get("field_of_study"))

    # 5. Projects
    for proj in original_profile.get("projects", []):
        add_fact(proj.get("name"))
        add_fact(proj.get("technologies"))
        add_fact(proj.get("features"))
        add_fact(proj.get("responsibilities"))
        add_fact(proj.get("achievements"))
        add_fact(proj.get("description"))
        add_fact(proj.get("ai_analysis_text"))

    # 6. Structured Project Evidence if present
    if structured_evidence_map:
        for ev in structured_evidence_map.values():
            if isinstance(ev, StructuredProjectEvidence):
                add_fact(ev.technologies)
                add_fact(ev.frameworks)
                add_fact(ev.apis)
                add_fact(ev.models)
                add_fact(ev.databases)
                add_fact(ev.deployment)
                add_fact(ev.features)
                add_fact(ev.technical_details)
                add_fact(ev.engineering_decisions)
                add_fact(ev.architecture)

    # 7. Certifications
    for cert in original_profile.get("certifications", []):
        add_fact(cert.get("name"))
        add_fact(cert.get("issuer"))

    return facts


def validate_optimized_data(
    original_profile: Dict[str, Any],
    structured_evidence_map: Optional[Dict[str, StructuredProjectEvidence]],
    optimized_data: OptimizedResumeData,
    job_requirements: Optional[Dict[str, Any]] = None,
    approved_additional_skills: Optional[List[str]] = None
) -> None:
    """
    Deterministically validates that AI optimization output does NOT violate factual grounding rules.
    Allows candidate-confirmed job skills in Technical Skills, but strictly forbids fabricating
    project technologies or project experience bullets for confirmed skills without evidence.
    Raises ValueError if validation fails.
    """
    candidate_skills = {
        _normalize(s["name"]): s["name"] for s in original_profile.get("skills", []) if s.get("name")
    }
    candidate_fact_tokens = _collect_candidate_fact_tokens(original_profile, structured_evidence_map)
    approved_set = {_normalize(s) for s in (approved_additional_skills or []) if s}
    approved_lower = {s.lower().strip() for s in (approved_additional_skills or []) if s}

    # 1. Validate Skills (Verified Candidate Profile skills + Candidate-Confirmed Job Skills)
    for group in optimized_data.skills:
        for sk in group.skills:
            norm_sk = _normalize(sk)
            # Candidate-confirmed job skills are authorized for Technical Skills
            if norm_sk in approved_set or sk.lower().strip() in approved_lower:
                continue
            if norm_sk not in candidate_skills:
                # Also check if it's explicitly present in candidate fact tokens
                if norm_sk not in candidate_fact_tokens and sk.lower() not in candidate_fact_tokens:
                    raise ValueError(
                        f"Factual Validation Failure: Skill '{sk}' is not present in candidate profile, project evidence, or confirmed job skills."
                    )

    # 2. Validate Education Immutability
    orig_edu = original_profile.get("education", [])
    if len(optimized_data.education) != len(orig_edu):
        raise ValueError(
            f"Factual Validation Failure: Education count mismatch ({len(optimized_data.education)} vs {len(orig_edu)})."
        )

    for opt_e, orig_e in zip(optimized_data.education, orig_edu):
        if _normalize(opt_e.get("institution", "")) != _normalize(orig_e.get("institution", "")):
            raise ValueError(f"Factual Validation Failure: Education institution modified ({opt_e.get('institution')} vs {orig_e.get('institution')}).")
        if _normalize(opt_e.get("degree", "")) != _normalize(orig_e.get("degree", "")):
            raise ValueError(f"Factual Validation Failure: Education degree modified ({opt_e.get('degree')} vs {orig_e.get('degree')}).")

    # 3. Validate Work Experience Immutability (Employer, Title, Dates)
    orig_exp = original_profile.get("experience", [])
    for opt_exp in optimized_data.experience:
        matching = [
            e for e in orig_exp if _normalize(e.get("company", "")) == _normalize(opt_exp.company)
        ]
        if not matching:
            raise ValueError(f"Factual Validation Failure: Unknown employer '{opt_exp.company}' in optimized experience.")
        orig_match = matching[0]
        if _normalize(opt_exp.role) != _normalize(orig_match.get("role", "")):
            raise ValueError(f"Factual Validation Failure: Job title altered for employer '{opt_exp.company}' ({opt_exp.role} vs {orig_match.get('role')}).")

    # 4. Validate Internships Immutability
    orig_intern = original_profile.get("internships", [])
    for opt_int in optimized_data.internships:
        matching = [
            i for i in orig_intern if _normalize(i.get("company", "")) == _normalize(opt_int.company)
        ]
        if not matching:
            raise ValueError(f"Factual Validation Failure: Unknown internship employer '{opt_int.company}'.")

    # 5. Validate Certifications Immutability
    orig_certs = {
        _normalize(c["name"]): c for c in original_profile.get("certifications", []) if c.get("name")
    }
    for opt_cert in optimized_data.certifications:
        norm_cert_name = _normalize(opt_cert.get("name", ""))
        if norm_cert_name not in orig_certs:
            raise ValueError(f"Factual Validation Failure: Fabricated certification '{opt_cert.get('name')}'.")

    # 6. Validate Project Technologies (Strictly Grounded in Profile / Structured Evidence only)
    for opt_proj in optimized_data.projects:
        for tech in opt_proj.technologies:
            norm_tech = _normalize(tech)
            if norm_tech not in candidate_fact_tokens and tech.lower() not in candidate_fact_tokens:
                raise ValueError(
                    f"Factual Validation Failure: Project technology '{tech}' in project '{opt_proj.project_name}' was not found in candidate source profile or evidence."
                )

    # 6b. Validate that confirmed-only skills do not fabricate project bullet claims without evidence
    confirmed_only = [
        s.strip() for s in (approved_additional_skills or [])
        if _normalize(s) not in candidate_fact_tokens and s.lower().strip() not in candidate_fact_tokens
    ]
    for opt_proj in optimized_data.projects:
        for bullet in opt_proj.bullets:
            for unevidenced_skill in confirmed_only:
                if len(unevidenced_skill) > 2:
                    pattern = rf"\b{re.escape(unevidenced_skill)}\b"
                    if re.search(pattern, bullet, flags=re.IGNORECASE):
                        raise ValueError(
                            f"Factual Validation Failure: Confirmed skill '{unevidenced_skill}' cannot be used in project bullet without evidence: '{bullet}'"
                        )

    # 7. Keyword Alignment Validation
    for unsupported in optimized_data.keyword_alignment.unsupported_jd_keywords:
        norm_unsupported = _normalize(unsupported)
        # If candidate explicitly confirmed this skill for this job, it's allowed in skills list
        if norm_unsupported in approved_set or unsupported.lower().strip() in approved_lower:
            continue
        for group in optimized_data.skills:
            for sk in group.skills:
                if _normalize(sk) == norm_unsupported:
                    raise ValueError(f"Factual Validation Failure: Unsupported JD keyword '{unsupported}' was placed in skills list.")
