"""
optimized_resume_transformer.py — Maps OptimizedResumeData (Phase 5 schema)
into a flat ResumeRenderData dict used by job_resume_renderer.py.

Compression is applied here by slicing and truncating based on CompressionLevel config.
The input OptimizedResumeData object is NEVER mutated.
"""
import copy
from typing import Any, Dict, List

from app.resume.compression import CompressionLevel
from app.schemas.optimization_schema import (
    OptimizedResumeData,
    OptimizedExperience,
    OptimizedInternship,
    OptimizedProject,
    OptimizedSkillGroup,
)


def _apply_bullet_limit(bullets: List[str], max_bullets: int) -> List[str]:
    """Return bullets list capped at max_bullets. 0 means unlimited."""
    if max_bullets > 0 and len(bullets) > max_bullets:
        return bullets[:max_bullets]
    return bullets


def _truncate_summary(summary: str, max_chars: int) -> str:
    """Truncate summary text to max_chars, preserving word boundaries."""
    if max_chars <= 0 or len(summary) <= max_chars:
        return summary
    truncated = summary[:max_chars].rsplit(" ", 1)[0]
    return truncated.rstrip(".,;:") + "."


def transform_optimized_to_render_data(
    optimized: OptimizedResumeData,
    user_email: str,
    compression: CompressionLevel,
) -> Dict[str, Any]:
    """
    Transform OptimizedResumeData into a ResumeRenderData dict for the LaTeX renderer.

    Args:
        optimized: The Phase 5 optimization snapshot (not mutated).
        user_email: Authenticated user's email address.
        compression: Compression level configuration to apply.

    Returns:
        A plain dict matching the structure expected by job_resume_renderer.py.
    """
    personal = optimized.personal_details or {}

    # ── Header ────────────────────────────────────────────────────────────────
    header = {
        "full_name": personal.get("full_name", ""),
        "email": user_email,
        "phone": personal.get("phone", ""),
        "portfolio_url": personal.get("portfolio_url", ""),
        "linkedin_url": personal.get("linkedin_url", ""),
        "github_url": personal.get("github_url", ""),
    }

    # ── Summary ───────────────────────────────────────────────────────────────
    summary = _truncate_summary(optimized.summary or "", compression.summary_max_chars)

    # ── Education (always included, never compressed) ──────────────────────────
    education = copy.deepcopy(optimized.education)

    # ── Experience ────────────────────────────────────────────────────────────
    experience: List[Dict[str, Any]] = []
    for exp in optimized.experience:
        bullets = _apply_bullet_limit(exp.bullets, compression.max_exp_bullets)
        experience.append({
            "company": exp.company,
            "role": exp.role,
            "location": exp.location,
            "start_date": exp.start_date or "",
            "end_date": exp.end_date or "",
            "is_current": exp.is_current,
            "responsibilities": bullets,
            "technologies": exp.technologies,
            "achievements": [],
        })

    # ── Internships ───────────────────────────────────────────────────────────
    internships: List[Dict[str, Any]] = []
    for intern in optimized.internships:
        bullets = _apply_bullet_limit(intern.bullets, compression.max_internship_bullets)
        internships.append({
            "company": intern.company,
            "role": intern.role,
            "location": intern.location,
            "start_date": intern.start_date or "",
            "end_date": intern.end_date or "",
            "is_current": intern.is_current,
            "responsibilities": bullets,
            "technologies": intern.technologies,
            "achievements": [],
        })

    # ── Projects (sorted by relevance_score desc, then capped) ────────────────
    sorted_projects = sorted(
        optimized.projects,
        key=lambda p: p.relevance_score,
        reverse=True,
    )
    if compression.max_projects > 0:
        sorted_projects = sorted_projects[: compression.max_projects]

    projects: List[Dict[str, Any]] = []
    for proj in sorted_projects:
        bullets = _apply_bullet_limit(proj.bullets, compression.max_project_bullets)
        projects.append({
            "name": proj.project_name,
            "description": "",
            "technologies": proj.technologies,
            "features": bullets,
            "project_url": proj.project_url,
            "github_url": proj.github_url,
            "repository_url": proj.repository_url,
        })

    # ── Skills ────────────────────────────────────────────────────────────────
    skills: List[Dict[str, Any]] = []
    for group in optimized.skills:
        for skill_name in group.skills:
            skills.append({
                "category": group.category,
                "name": skill_name,
            })

    # ── Certifications ────────────────────────────────────────────────────────
    certifications: List[Dict[str, Any]] = []
    if compression.include_certifications:
        certifications = copy.deepcopy(optimized.certifications)

    return {
        "margin_top": compression.margin_top,
        "margin_bottom": compression.margin_bottom,
        "margin_left": compression.margin_left,
        "margin_right": compression.margin_right,
        "section_before_spacing": compression.section_before_spacing,
        "header": header,
        "summary": summary,
        "education": education,
        "experience": experience,
        "internships": internships,
        "projects": projects,
        "skills": skills,
        "certifications": certifications,
        "section_order": getattr(optimized, "section_order", None),
    }
