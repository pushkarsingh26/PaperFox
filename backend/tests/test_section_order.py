import pytest
from pydantic import ValidationError
from app.schemas.profile import (
    ProfileCreate,
    ProfileUpdate,
    ProjectSchema,
    SUPPORTED_RESUME_SECTIONS,
    DEFAULT_SECTION_ORDER,
    normalize_technologies,
    validate_section_order_list,
)
from app.resume.transformer import transform_profile_to_resume_data
from app.resume.renderer import render_latex_resume
from app.resume.job_resume_renderer import render_job_latex_resume


def test_technologies_normalization():
    # Comma separation and spaces
    assert normalize_technologies("Python, FastAPI, MongoDB, LangChain, Next.js") == [
        "Python",
        "FastAPI",
        "MongoDB",
        "LangChain",
        "Next.js",
    ]
    # Spaces around commas, double commas, trailing comma
    assert normalize_technologies("Python,  FastAPI , MongoDB,, LangChain,") == [
        "Python",
        "FastAPI",
        "MongoDB",
        "LangChain",
    ]
    # Deduplication case-insensitively while preserving first casing
    assert normalize_technologies("Python, python, FastAPI, FASTAPI, MongoDB") == [
        "Python",
        "FastAPI",
        "MongoDB",
    ]
    # Empty string or None
    assert normalize_technologies("") == []
    assert normalize_technologies(None) == []
    # List of strings with embedded commas
    assert normalize_technologies(["Python, FastAPI", "MongoDB", "  Docker  "]) == [
        "Python",
        "FastAPI",
        "MongoDB",
        "Docker",
    ]


def test_project_schema_technologies_cleaning():
    proj = ProjectSchema(
        name="PaperFox",
        technologies="Python,  FastAPI , MongoDB,, LangChain, python",
    )
    assert proj.technologies == ["Python", "FastAPI", "MongoDB", "LangChain"]


def test_section_order_validator():
    # Valid ordering
    valid = ["summary", "skills", "projects", "education", "certifications", "experience"]
    assert validate_section_order_list(valid) == valid

    # Case normalization
    assert validate_section_order_list(["SKILLS", "PROJECTS", "EDUCATION"]) == [
        "skills",
        "projects",
        "education",
    ]

    # Rejection of unknown section
    with pytest.raises(ValueError, match="Unknown section"):
        validate_section_order_list(["skills", "hobbies"])

    # Rejection of duplicates
    with pytest.raises(ValueError, match="Duplicate section"):
        validate_section_order_list(["skills", "projects", "skills"])


def test_profile_create_with_section_order():
    profile = ProfileCreate(
        personal_details={
            "full_name": "Jane Fox",
            "github_url": "https://github.com/janefox",
            "linkedin_url": "https://linkedin.com/in/janefox",
        },
        section_order=["skills", "projects", "education", "certifications", "experience"],
    )
    assert str(profile.personal_details.github_url) == "https://github.com/janefox"
    assert str(profile.personal_details.linkedin_url) == "https://linkedin.com/in/janefox"
    assert profile.section_order == [
        "skills",
        "projects",
        "education",
        "certifications",
        "experience",
    ]


def test_base_resume_custom_section_ordering():
    profile_dict = {
        "personal_details": {
            "full_name": "Jane Fox",
            "phone": "555-1234",
            "github_url": "https://github.com/janefox",
            "linkedin_url": "https://linkedin.com/in/janefox",
        },
        "candidate_type": "experienced",
        "education": [
            {
                "institution": "Stanford University",
                "degree": "B.S.",
                "field_of_study": "Computer Science",
                "start_date": "2018",
                "end_date": "2022",
            }
        ],
        "experience": [
            {
                "company": "Tech Corp",
                "role": "Software Engineer",
                "start_date": "2022",
                "end_date": "Present",
                "is_current": True,
                "responsibilities": ["Built core microservices"],
            }
        ],
        "projects": [
            {
                "name": "PaperFox Resume Platform",
                "description": "ATS resume builder",
                "technologies": ["Python", "FastAPI", "React"],
            }
        ],
        "skills": [
            {"name": "Python", "category": "Languages"},
            {"name": "FastAPI", "category": "Frameworks"},
        ],
        "certifications": [
            {"name": "AWS Certified Developer", "issuer": "Amazon Web Services"}
        ],
        # Custom order: Skills first, then Projects, then Experience, then Education, then Certifications
        "section_order": ["skills", "projects", "experience", "education", "certifications"],
    }

    resume_data = transform_profile_to_resume_data(profile_dict, "jane@example.com")
    assert resume_data["section_order"] == [
        "skills",
        "projects",
        "experience",
        "education",
        "certifications",
    ]
    assert resume_data["header"]["github_url"] == "https://github.com/janefox"
    assert resume_data["header"]["linkedin_url"] == "https://linkedin.com/in/janefox"

    latex = render_latex_resume(resume_data)

    # Verify header contains GitHub and LinkedIn
    assert "GitHub" in latex
    assert "LinkedIn" in latex

    # Verify section sequence in generated LaTeX
    skills_idx = latex.find("\\section{Technical Skills}")
    proj_idx = latex.find("\\section{Projects}")
    exp_idx = latex.find("\\section{Work Experience}")
    edu_idx = latex.find("\\section{Education}")
    cert_idx = latex.find("\\section{Certifications}")

    assert skills_idx != -1
    assert proj_idx != -1
    assert exp_idx != -1
    assert edu_idx != -1
    assert cert_idx != -1

    assert skills_idx < proj_idx < exp_idx < edu_idx < cert_idx


def test_job_resume_custom_section_ordering():
    render_data = {
        "header": {
            "full_name": "Jane Fox",
            "email": "jane@example.com",
            "phone": "555-1234",
            "github_url": "https://github.com/janefox",
            "linkedin_url": "https://linkedin.com/in/janefox",
        },
        "summary": "Experienced full-stack engineer.",
        "education": [
            {
                "institution": "Stanford University",
                "degree": "B.S.",
                "field_of_study": "Computer Science",
            }
        ],
        "experience": [
            {
                "company": "Tech Corp",
                "role": "Software Engineer",
                "responsibilities": ["Built core services"],
            }
        ],
        "projects": [
            {
                "name": "PaperFox",
                "technologies": ["Python", "React"],
                "features": ["Feature A"],
            }
        ],
        "skills": [
            {"category": "Languages", "name": "Python"},
            {"category": "Frameworks", "name": "FastAPI"},
        ],
        "certifications": [
            {"name": "AWS Certified", "issuer": "AWS"}
        ],
        "section_order": ["summary", "projects", "skills", "education", "experience", "certifications"],
    }

    latex = render_job_latex_resume(render_data)

    sum_idx = latex.find("\\section{Summary}")
    proj_idx = latex.find("\\section{Projects}")
    skills_idx = latex.find("\\section{Technical Skills}")
    edu_idx = latex.find("\\section{Education}")
    exp_idx = latex.find("\\section{Work Experience}")
    cert_idx = latex.find("\\section{Certifications}")

    assert sum_idx < proj_idx < skills_idx < edu_idx < exp_idx < cert_idx
