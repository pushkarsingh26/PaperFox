"""
job_resume_renderer.py — Renders OptimizedResumeData render dicts into a complete
LaTeX source string using the job_resume.tex template.

All section render functions consume plain Python dicts (not Pydantic models) so
they are decoupled from schema changes and easily testable in isolation.
"""
import os
import re
from typing import Any, Dict, List

from app.resume.escaping import escape_latex, format_latex_url, strip_latex_bold

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

    contact_line = " $\\bullet$ ".join(parts)
    return full_name, contact_line


def render_summary(summary: str) -> str:
    """Render the professional summary section."""
    if not summary or not summary.strip():
        return ""
    lines = ["\\section{Professional Summary}", "\\small"]
    lines.append(escape_latex(summary.strip()) + " \\par")
    lines.append("\\vspace{1pt}")
    return "\n".join(lines)


def render_education(education_list: List[Dict[str, Any]]) -> str:
    """Render the Education section matching reference compact two-line structure."""
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
        deg_field = f"{degree} in {field}" if (degree and field) else (degree or field)

        lines.append(f"\\noindent \\textbf{{{inst}}}{loc_str} \\\\")
        lines.append(
            f"\\textit{{\\small {deg_field}}}{grade_str} \\hfill \\textit{{\\small {dates}}} \\par"
        )

    lines.append("\\vspace{1pt}")
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
        lines.append(f"\\textit{{\\small {dates}}} \\par")

        bullet_items = responsibilities + achievements
        if bullet_items or techs:
            lines.append("\\vspace{-2pt}")
            lines.append("\\begin{itemize}")
            for bullet in bullet_items:
                clean_bullet = strip_latex_bold(bullet)
                lines.append(f"  \\item \\small {escape_latex(clean_bullet)}")
            if techs:
                tech_str = ", ".join([escape_latex(t) for t in techs])
                lines.append(f"  \\item \\small \\textit{{{tech_str}}}")
            lines.append("\\end{itemize}")
        lines.append("\\vspace{2pt}")

    return "\n".join(lines)


def render_projects(projects: List[Dict[str, Any]]) -> str:
    """Render the Projects section from optimized project render dicts matching Pushkar reference format."""
    if not projects:
        return ""

    lines = ["\\section{Projects}"]
    for proj in projects:
        name = escape_latex(proj.get("name", ""))
        techs = proj.get("technologies", [])
        features = proj.get("features", [])   # optimized bullets

        repo_url = proj.get("github_url") or proj.get("repository_url")
        demo_url = proj.get("project_url")

        code_link = ""
        if repo_url:
            code_link = format_latex_url(repo_url, "Code")
            if demo_url and demo_url.strip() != repo_url.strip():
                code_link += f" $\\bullet$ {format_latex_url(demo_url, 'Demo')}"
        elif demo_url:
            code_link = format_latex_url(demo_url, "Demo")

        if code_link:
            lines.append(f"\\noindent \\textbf{{{name}}} \\hfill {{{code_link}}} \\\\")
        else:
            lines.append(f"\\noindent \\textbf{{{name}}} \\\\")

        if techs:
            tech_str = ", ".join([escape_latex(t) for t in techs])
            lines.append(f"\\textit{{\\small {tech_str}}} \\par")
            lines.append("\\vspace{-2pt}")

        if features:
            lines.append("\\begin{itemize}")
            for feat in features:
                clean_feat = strip_latex_bold(feat)
                lines.append(f"  \\item \\small {escape_latex(clean_feat)}")
            lines.append("\\end{itemize}")

        lines.append("\\vspace{2pt}")

    return "\n".join(lines)


def render_skills(skills: List[Dict[str, Any]]) -> str:
    """Render Technical Skills section as compact category lines matching reference layout."""
    if not skills:
        return ""

    categories: Dict[str, List[str]] = {}
    for s in skills:
        cat = s.get("category", "Other")
        name = escape_latex(s.get("name", ""))
        categories.setdefault(cat, []).append(name)

    lines = ["\\section{Technical Skills}", "\\small"]
    cat_lines: List[str] = []
    for cat, item_list in categories.items():
        cat_escaped = escape_latex(cat)
        skills_str = ", ".join(item_list)
        cat_lines.append(f"\\textbf{{{cat_escaped}:}} {skills_str}")

    if cat_lines:
        lines.append("\\noindent " + " \\\\\n".join(cat_lines))
    lines.append("\\par\\vspace{1pt}")

    return "\n".join(lines)


def render_certifications(certifications: List[Dict[str, Any]]) -> str:
    """Render Certifications section displaying only Issuer, Name, and Year without credential IDs or URLs."""
    if not certifications:
        return ""

    lines = ["\\section{Certifications}", "\\small"]
    cert_lines: List[str] = []
    for cert in certifications:
        name = escape_latex(cert.get("name", ""))
        issuer = escape_latex(cert.get("issuer", ""))
        raw_date = str(cert.get("issue_date") or cert.get("year") or cert.get("date") or "").strip()

        # Extract 4-digit year if present (e.g. "2026-03-01" -> "2026", "March 2026" -> "2026")
        year_match = re.search(r"\b(19\d\d|20\d\d)\b", raw_date)
        year_str = escape_latex(year_match.group(1)) if year_match else escape_latex(raw_date)
        date_str = f" ({year_str})" if year_str else ""

        if issuer:
            cert_lines.append(f"\\textbf{{{issuer}:}} {name}{date_str}")
        else:
            cert_lines.append(f"\\textbf{{{name}}}{date_str}")

    if cert_lines:
        lines.append("\\noindent " + " \\\\\n".join(cert_lines))
    lines.append("\\par\\vspace{1pt}")

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
    margin_top = f"{float(render_data.get('margin_top', 0.38)):.2f}"
    margin_bottom = f"{float(render_data.get('margin_bottom', 0.38)):.2f}"
    margin_left = f"{float(render_data.get('margin_left', 0.40)):.2f}"
    margin_right = f"{float(render_data.get('margin_right', 0.40)):.2f}"
    section_spacing = str(render_data.get("section_before_spacing", 7))

    section_map = {
        "summary": summary_sec,
        "education": edu_sec,
        "experience": exp_sec or int_sec,
        "internships": int_sec,
        "projects": proj_sec,
        "skills": skills_sec,
        "certifications": certs_sec,
    }
    if exp_sec and int_sec:
        section_map["experience"] = f"{exp_sec}\n\n{int_sec}"

    default_job_order = ["summary", "skills", "projects", "experience", "education", "certifications"]
    section_order = render_data.get("section_order") or default_job_order
    order = [s for s in section_order if s in section_map]
    for def_sec in default_job_order:
        if def_sec not in order:
            order.append(def_sec)

    ordered_body = []
    seen = set()
    for s in order:
        if s not in seen:
            seen.add(s)
            c = section_map.get(s, "").strip()
            if c:
                ordered_body.append(c)
    body_sections_str = "\n\n".join(ordered_body)

    if "{{BODY_SECTIONS}}" in template:
        rendered = (
            template
            .replace("{{FULL_NAME}}", full_name)
            .replace("{{CONTACT_LINE}}", contact_line)
            .replace("{{BODY_SECTIONS}}", body_sections_str)
            .replace("{{MARGIN_TOP}}", margin_top)
            .replace("{{MARGIN_BOTTOM}}", margin_bottom)
            .replace("{{MARGIN_LEFT}}", margin_left)
            .replace("{{MARGIN_RIGHT}}", margin_right)
            .replace("{{SECTION_BEFORE_SPACING}}", section_spacing)
        )
    else:
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
