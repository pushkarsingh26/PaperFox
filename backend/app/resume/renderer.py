import os
import re
from typing import Any, Dict, List, Optional
from app.resume.escaping import escape_latex, format_latex_url, strip_latex_bold
from app.schemas.profile import DEFAULT_SECTION_ORDER

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "templates", "base_resume.tex")


def render_header(header: Dict[str, Any]) -> tuple[str, str]:
    full_name = escape_latex(header.get("full_name", ""))

    parts = []
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
    if not summary or not summary.strip():
        return ""
    lines = ["\\section{Professional Summary}", "\\small"]
    lines.append(escape_latex(summary.strip()) + " \\par")
    lines.append("\\vspace{1pt}")
    return "\n".join(lines)


def render_education(education_list: List[Dict[str, Any]]) -> str:
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
    if not items:
        return ""

    lines = [f"\\section{{{title}}}"]
    for item in items:
        comp = escape_latex(item.get("company", ""))
        role = escape_latex(item.get("role", ""))
        loc = escape_latex(item.get("location", ""))
        start = escape_latex(item.get("start_date", ""))
        end = "Present" if item.get("is_current") else escape_latex(item.get("end_date", ""))
        desc = escape_latex(item.get("description", ""))
        resps = item.get("responsibilities", [])
        techs = item.get("technologies", [])
        achievements = item.get("achievements", [])

        dates = f"{start} -- {end}" if start else end
        loc_str = f" \\hfill {loc}" if loc else ""

        lines.append(f"\\noindent \\textbf{{{role}}} -- \\textbf{{{comp}}}{loc_str} \\\\")
        lines.append(f"\\textit{{\\small {dates}}} \\par")

        if desc:
            lines.append(f"{desc} \\par")

        if resps or achievements or techs:
            lines.append("\\vspace{-2pt}")
            lines.append("\\begin{itemize}")
            for r in resps:
                clean_r = strip_latex_bold(r)
                lines.append(f"  \\item \\small {escape_latex(clean_r)}")
            for a in achievements:
                clean_a = strip_latex_bold(a)
                lines.append(f"  \\item \\small \\textbf{{Achievement:}} {escape_latex(clean_a)}")
            if techs:
                tech_str = ", ".join([escape_latex(t) for t in techs])
                lines.append(f"  \\item \\small \\textit{{{tech_str}}}")
            lines.append("\\end{itemize}")
        lines.append("\\vspace{2pt}")

    return "\n".join(lines)


def render_projects(projects: List[Dict[str, Any]]) -> str:
    if not projects:
        return ""

    lines = ["\\section{Projects}"]
    for proj in projects:
        name = escape_latex(proj.get("name", ""))
        desc = escape_latex(proj.get("description", ""))
        techs = proj.get("technologies", [])
        features = proj.get("features", [])

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

        if desc and not features:
            clean_desc = strip_latex_bold(desc)
            lines.append(f"{clean_desc} \\par")

        if features:
            lines.append("\\begin{itemize}")
            for feat in features:
                clean_feat = strip_latex_bold(feat)
                lines.append(f"  \\item \\small {escape_latex(clean_feat)}")
            lines.append("\\end{itemize}")

        lines.append("\\vspace{2pt}")

    return "\n".join(lines)


def render_skills(skills: List[Dict[str, Any]]) -> str:
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


def render_latex_resume(resume_data: Dict[str, Any]) -> str:
    """
    Renders ResumeData dictionary into a valid, complete LaTeX document.
    Deterministic assembly obeying user's section_order preference.
    """
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Base LaTeX template not found at {TEMPLATE_PATH}")

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = f.read()

    full_name, contact_line = render_header(resume_data.get("header", {}))
    summary_sec = render_summary(resume_data.get("summary", ""))
    edu_sec = render_education(resume_data.get("education", []))
    exp_sec = render_experience_items("Work Experience", resume_data.get("experience", []))
    int_sec = render_experience_items("Internships", resume_data.get("internships", []))
    proj_sec = render_projects(resume_data.get("projects", []))
    skills_sec = render_skills(resume_data.get("skills", []))
    certs_sec = render_certifications(resume_data.get("certifications", []))

    # Build section map
    section_map = {
        "summary": summary_sec,
        "education": edu_sec,
        "experience": exp_sec or int_sec,
        "internships": int_sec,
        "projects": proj_sec,
        "skills": skills_sec,
        "certifications": certs_sec,
    }
    # If both experience and internships exist and experience is chosen:
    if exp_sec and int_sec:
        section_map["experience"] = f"{exp_sec}\n\n{int_sec}"

    section_order = resume_data.get("section_order") or DEFAULT_SECTION_ORDER
    order = [s for s in section_order if s in section_map]
    for def_sec in DEFAULT_SECTION_ORDER:
        if def_sec not in order:
            order.append(def_sec)

    ordered_body_sections = []
    seen = set()
    for s in order:
        if s not in seen:
            seen.add(s)
            content = section_map.get(s, "").strip()
            if content:
                ordered_body_sections.append(content)

    body_sections_str = "\n\n".join(ordered_body_sections)

    if "{{BODY_SECTIONS}}" in template:
        rendered = (
            template.replace("{{FULL_NAME}}", full_name)
            .replace("{{CONTACT_LINE}}", contact_line)
            .replace("{{BODY_SECTIONS}}", body_sections_str)
        )
    else:
        rendered = (
            template.replace("{{FULL_NAME}}", full_name)
            .replace("{{CONTACT_LINE}}", contact_line)
            .replace("{{EDUCATION_SECTION}}", edu_sec)
            .replace("{{EXPERIENCE_SECTION}}", exp_sec)
            .replace("{{INTERNSHIPS_SECTION}}", int_sec)
            .replace("{{PROJECTS_SECTION}}", proj_sec)
            .replace("{{SKILLS_SECTION}}", skills_sec)
            .replace("{{CERTIFICATIONS_SECTION}}", certs_sec)
        )

    return rendered
