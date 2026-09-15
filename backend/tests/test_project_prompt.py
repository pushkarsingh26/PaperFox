import pytest
from app.schemas.profile import ProjectSchema, ProfileCreate, PersonalDetails
from app.utils.prompt_generator import generate_universal_project_prompt


def test_project_schema_description_source_default():
    proj = ProjectSchema(name="PaperFox")
    assert proj.description_source == "self"
    assert proj.ai_analysis_text is None


def test_project_schema_description_source_custom():
    proj_self = ProjectSchema(name="PaperFox", description_source="SELF")
    assert proj_self.description_source == "self"

    proj_ai = ProjectSchema(name="PaperFox", description_source="ai", ai_analysis_text="Raw plain text analysis")
    assert proj_ai.description_source == "ai"
    assert proj_ai.ai_analysis_text == "Raw plain text analysis"


def test_project_schema_invalid_description_source():
    with pytest.raises(ValueError):
        ProjectSchema(name="PaperFox", description_source="invalid_source")


def test_prompt_generator_contains_required_rules_and_fields():
    project_data = {
        "name": "PaperFox Resume Engine",
        "description": "Multi-provider AI resume optimization platform",
        "technologies": ["Next.js", "FastAPI", "MongoDB", "Python"],
        "github_url": "https://github.com/user/paperfox",
        "features": ["JD analysis", "LaTeX PDF rendering"],
        "responsibilities": ["Full-stack architecture", "API design"]
    }

    prompt = generate_universal_project_prompt(project_data)

    # 1. Project name included
    assert "PaperFox Resume Engine" in prompt

    # 2. Known context included
    assert "Multi-provider AI resume optimization platform" in prompt
    assert "Next.js, FastAPI, MongoDB, Python" in prompt
    assert "https://github.com/user/paperfox" in prompt

    # 3. Universal and vendor neutral (no hardcoded Antigravity or product requirement)
    assert "Antigravity" not in prompt
    assert "PROJECT CODEBASE ANALYSIS REQUEST" in prompt

    # 4. Asks coding AI to inspect actual codebase
    assert "Inspect the actual project/codebase available in your current workspace" in prompt

    # 5. Anti-hallucination / factual grounding rules
    assert "Do not fabricate technologies" in prompt
    assert "Do not fabricate architecture" in prompt
    assert "Do not fabricate APIs" in prompt

    # 6. Explicit plain text output requirement
    assert "Return PLAIN TEXT ONLY" in prompt
    assert "Do NOT return:" in prompt
