from typing import Any, Dict


def transform_profile_to_resume_data(
    profile_dict: Dict[str, Any], user_email: str
) -> Dict[str, Any]:
    """
    Transforms MongoDB candidate profile document and account email into a normalized
    ResumeData dictionary ready for LaTeX rendering.
    Guarantees that input profile remains 100% immutable.
    """
    personal = profile_dict.get("personal_details", {})
    candidate_type = profile_dict.get("candidate_type", "fresher")

    resume_data = {
        "header": {
            "full_name": personal.get("full_name", ""),
            "email": user_email,
            "phone": personal.get("phone", ""),
            "portfolio_url": personal.get("portfolio_url", ""),
            "linkedin_url": personal.get("linkedin_url", ""),
            "github_url": personal.get("github_url", ""),
        },
        "candidate_type": candidate_type,
        "summary": "",
        "education": profile_dict.get("education", []),
        "internships": profile_dict.get("internships", []),
        "experience": profile_dict.get("experience", []),
        "projects": profile_dict.get("projects", []),
        "skills": profile_dict.get("skills", []),
        "certifications": profile_dict.get("certifications", []),
    }

    return resume_data
