"""
job_resume_renderer.py — Renders OptimizedResumeData render dicts into a complete
LaTeX source string using the job_resume.tex template.

All section render functions consume plain Python dicts (not Pydantic models) so
they are decoupled from schema changes and easily testable in isolation.
"""
import os
from typing import Any, Dict, List

from app.resume.escaping import escape_latex, format_latex_url

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "templates", "job_resume.tex")


# ──────────────────────────────────────────────────────────────────────────────
# Section renderers
# ──────────────────────────────────────────────────────────────────────────────

def render_header(header: Dict[str, Any]) -> tuple[str, str]:
    """Render the name and contact line for the resume header."""
    full_name = escape_latex(header.get("full_name", ""))

    parts: List[str] = []
    if header.get("phone"):
        parts.append(escape_latex(header["phone"]))
    if header.get("email"):
        parts.append(format_latex_url(f"mailto:{header['email']}", header["email"]))
    if header.get("linkedin_url"):
        parts.append(format_latex_url(header["linkedin_url"], "LinkedIn"))
    if header.get("github_url"):
        parts.append(format_latex_url(header["github_url"], "GitHub"))
    if header.get("portfolio_url"):
        parts.append(format_latex_url(header["portfolio_url"], "Portfolio"))

    contact_line = " \\ \\textbullet\\ \\ ".join(parts)
    return full_name, contact_line


def render_summary(summary: str) -> str:
    """Render the professional summary section."""
    if not summary or not summary.strip():
        return ""
    lines = ["\\section{Summary}"]
    lines.append(escape_latex(summary.strip()))
    lines.append("\\vspace{2pt}")
    return "\n".join(lines)


def render_education(education_list: List[Dict[str, Any]]) -> str:
    """Render the Education section."""
    if not education_list:
        return ""

    lines = ["\\section{Education}"]
    for edu in education_list:
        inst = escape_latex(edu.get("institution", ""))
        degree = escape_latex(edu.get("degree", ""))
        field = escape_latex(edu.get("field_of_study", ""))
        loc = escape_latex(edu.get("location", ""))
        start = escape_latex(edu.get("start_date", ""))
        end = escape_latex(edu.get("end_date", "Present"))
        grade = escape_latex(edu.get("grade", ""))

        dates = f"{start} -- {end}" if start else end
        loc_str = f" \\hfill {loc}" if loc else ""
        grade_str = f" (GPA/Grade: {grade})" if grade else ""

        lines.append(f"\\noindent \\textbf{{{inst}}}{loc_str} \\\\")
        lines.append(
            f"\\textit{{{degree} in {field}}}{grade_str} \\hfill \\textit{{{dates}}} \\\\[2pt]"
        )

    return "\n".join(lines)


def render_experience_items(title: str, items: List[Dict[str, Any]]) -> str:
    """Render Work Experience or Internships section from optimized bullets."""
    if not items:
        return ""

    lines = [f"\\section{{{title}}}"]
    for item in items:
        comp = escape_latex(item.get("company", ""))
        role = escape_latex(item.get("role", ""))
        loc = escape_latex(item.get("location", "") or "")
        start = escape_latex(item.get("start_date", "") or "")
        end = "Present" if item.get("is_current") else escape_latex(item.get("end_date", "") or "")
        responsibilities = item.get("responsibilities", [])
        achievements = item.get("achievements", [])
        techs = item.get("technologies", [])

        dates = f"{start} -- {end}" if start else end
        loc_str = f" \\hfill {loc}" if loc else ""

        lines.append(f"\\noindent \\textbf{{{role}}} -- \\textbf{{{comp}}}{loc_str} \\\\")
        lines.append(f"\\textit{{{dates}}} \\\\[1pt]")

        bullet_items = responsibilities + achievements
        if bullet_items or techs:
            lines.append("\\begin{itemize}")
            for bullet in bullet_items:
                lines.append(f"  \\item {escape_latex(bullet)}")
            if techs:
                tech_str = ", ".join([escape_latex(t) for t in techs])
                lines.append(f"  \\item \\textbf{{Technologies:}} {tech_str}")
            lines.append("\\end{itemize}")
        lines.append("\\vspace{3pt}")

    return "\n".join(lines)


def render_projects(projects: List[Dict[str, Any]]) -> str:
    """Render the Projects section from optimized project render dicts."""
    if not projects:
        return ""

    lines = ["\\section{Projects}"]
    for proj in projects:
        name = escape_latex(proj.get("name", ""))
        techs = proj.get("technologies", [])
        features = proj.get("features", [])   # optimized bullets

        urls: List[str] = []
        if proj.get("project_url"):
            urls.append(format_latex_url(proj["project_url"], "Demo"))
        if proj.get("github_url"):
            urls.append(format_latex_url(proj["github_url"], "GitHub"))
        if proj.get("repository_url"):
            urls.append(format_latex_url(proj["repository_url"], "Repository"))

        url_str = f" ( {', '.join(urls)} )" if urls else ""
        lines.append(f"\\noindent \\textbf{{{name}}}{url_str} \\\\")

        if techs or features:
            lines.append("\\begin{itemize}")
            if techs:
                tech_str = ", ".join([escape_latex(t) for t in techs])
                lines.append(f"  \\item \\textbf{{Technologies:}} {tech_str}")
            for feat in features:
                lines.append(f"  \\item {escape_latex(feat)}")
            lines.append("\\end{itemize}")
        lines.append("\\vspace{3pt}")

    return "\n".join(lines)


def render_skills(skills: List[Dict[str, Any]]) -> str:
    """Render Technical Skills section from flat {category, name} skill dicts."""
    if not skills:
        return ""

    categories: Dict[str, List[str]] = {}
    for s in skills:
        cat = s.get("category", "Other")
        name = escape_latex(s.get("name", ""))
        categories.setdefault(cat, []).append(name)

    lines = ["\\section{Technical Skills}"]
    lines.append("\\begin{itemize}")
    for cat, item_list in categories.items():
        cat_escaped = escape_latex(cat)
        skills_str = ", ".join(item_list)
        lines.append(f"  \\item \\textbf{{{cat_escaped}:}} {skills_str}")
    lines.append("\\end{itemize}")
    lines.append("\\vspace{3pt}")

    return "\n".join(lines)


def render_certifications(certifications: List[Dict[str, Any]]) -> str:
    """Render Certifications section."""
    if not certifications:
        return ""

    lines = ["\\section{Certifications}"]
    lines.append("\\begin{itemize}")
    for cert in certifications:
        name = escape_latex(cert.get("name", ""))
        issuer = escape_latex(cert.get("issuer", ""))
        date = escape_latex(cert.get("issue_date", ""))
        url = cert.get("credential_url")

        date_str = f" ({date})" if date else ""
        url_str = f" -- {format_latex_url(url, 'Credential')}" if url else ""

        lines.append(f"  \\item \\textbf{{{name}}} -- {issuer}{date_str}{url_str}")
    lines.append("\\end{itemize}")

    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
# Top-level render function
# ──────────────────────────────────────────────────────────────────────────────

def render_job_latex_resume(render_data: Dict[str, Any]) -> str:
    """
    Render a complete LaTeX source string from a ResumeRenderData dict.

    Args:
        render_data: Output of optimized_resume_transformer.transform_optimized_to_render_data().

    Returns:
        A complete LaTeX document string ready for pdflatex/xelatex compilation.

    Raises:
        FileNotFoundError: If the job_resume.tex template is missing.
    """
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"LaTeX template not found: {TEMPLATE_PATH}")

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = f.read()

    full_name, contact_line = render_header(render_data.get("header", {}))
    summary_sec = render_summary(render_data.get("summary", ""))
    edu_sec = render_education(render_data.get("education", []))
    exp_sec = render_experience_items("Work Experience", render_data.get("experience", []))
    int_sec = render_experience_items("Internships", render_data.get("internships", []))
    proj_sec = render_projects(render_data.get("projects", []))
    skills_sec = render_skills(render_data.get("skills", []))
    certs_sec = render_certifications(render_data.get("certifications", []))

    # Margin and spacing values from compression level config
    margin_top = str(render_data.get("margin_top", 0.50))
    margin_bottom = str(render_data.get("margin_bottom", 0.50))
    margin_left = str(render_data.get("margin_left", 0.50))
    margin_right = str(render_data.get("margin_right", 0.50))
    section_spacing = str(render_data.get("section_before_spacing", 7))

    rendered = (
        template
        .replace("{{FULL_NAME}}", full_name)
        .replace("{{CONTACT_LINE}}", contact_line)
        .replace("{{SUMMARY_SECTION}}", summary_sec)
        .replace("{{EDUCATION_SECTION}}", edu_sec)
        .replace("{{EXPERIENCE_SECTION}}", exp_sec)
        .replace("{{INTERNSHIPS_SECTION}}", int_sec)
        .replace("{{PROJECTS_SECTION}}", proj_sec)
        .replace("{{SKILLS_SECTION}}", skills_sec)
        .replace("{{CERTIFICATIONS_SECTION}}", certs_sec)
        .replace("{{MARGIN_TOP}}", margin_top)
        .replace("{{MARGIN_BOTTOM}}", margin_bottom)
        .replace("{{MARGIN_LEFT}}", margin_left)
        .replace("{{MARGIN_RIGHT}}", margin_right)
        .replace("{{SECTION_BEFORE_SPACING}}", section_spacing)
    )

    return rendered
