import os
from typing import Any, Dict, List, Optional
from app.resume.escaping import escape_latex, format_latex_url
from app.schemas.profile import DEFAULT_SECTION_ORDER

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "templates", "base_resume.tex")


def render_header(header: Dict[str, Any]) -> tuple[str, str]:
    full_name = escape_latex(header.get("full_name", ""))
    
    parts = []
    if header.get("phone"):
        parts.append(escape_latex(header["phone"]))
    if header.get("email"):
        parts.append(format_latex_url(header["email"], header["email"]))
    if header.get("portfolio_url"):
        parts.append(format_latex_url(header["portfolio_url"], "Portfolio"))
    if header.get("linkedin_url"):
        parts.append(format_latex_url(header["linkedin_url"], "LinkedIn"))
    if header.get("github_url"):
        parts.append(format_latex_url(header["github_url"], "GitHub"))

    contact_line = " \\ \\textbullet\\ \\ ".join(parts)
    return full_name, contact_line


def render_summary(summary: str) -> str:
    if not summary or not summary.strip():
        return ""
    lines = ["\\section{Summary}"]
    lines.append(escape_latex(summary.strip()))
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
        
        lines.append(f"\\noindent \\textbf{{{inst}}}{loc_str} \\\\")
        grade_str = f" (GPA/Grade: {grade})" if grade else ""
        lines.append(f"\\textit{{{degree} in {field}}}{grade_str} \\hfill \\textit{{{dates}}} \\\\[3pt]")

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
        lines.append(f"\\textit{{{dates}}} \\\\[2pt]")

        if desc:
            lines.append(f"{desc} \\\\[2pt]")

        if resps or achievements or techs:
            lines.append("\\begin{itemize}")
            for r in resps:
                lines.append(f"  \\item {escape_latex(r)}")
            for a in achievements:
                lines.append(f"  \\item \\textbf{{Achievement:}} {escape_latex(a)}")
            if techs:
                tech_str = ", ".join([escape_latex(t) for t in techs])
                lines.append(f"  \\item \\textbf{{Technologies:}} {tech_str}")
            lines.append("\\end{itemize}")
        lines.append("\\vspace{4pt}")

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
        
        urls = []
        if proj.get("project_url"):
            urls.append(format_latex_url(proj["project_url"], "Demo"))
        if proj.get("github_url"):
            urls.append(format_latex_url(proj["github_url"], "GitHub"))
        if proj.get("repository_url"):
            urls.append(format_latex_url(proj["repository_url"], "Repository"))

        url_str = f" ( {', '.join(urls)} )" if urls else ""

        lines.append(f"\\noindent \\textbf{{{name}}}{url_str} \\\\")
        if desc:
            lines.append(f"{desc} \\\\[2pt]")

        if techs or features:
            lines.append("\\begin{itemize}")
            if techs:
                tech_str = ", ".join([escape_latex(t) for t in techs])
                lines.append(f"  \\item \\textbf{{Technologies:}} {tech_str}")
            for feat in features:
                lines.append(f"  \\item {escape_latex(feat)}")
            lines.append("\\end{itemize}")
        lines.append("\\vspace{4pt}")

    return "\n".join(lines)


def render_skills(skills: List[Dict[str, Any]]) -> str:
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
    lines.append("\\vspace{4pt}")

    return "\n".join(lines)


def render_certifications(certifications: List[Dict[str, Any]]) -> str:
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
