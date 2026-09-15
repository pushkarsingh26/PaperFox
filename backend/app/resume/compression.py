"""
compression.py — Stateless incremental compression strategy for one-page PDF enforcement.

Compression is applied purely deterministically at the render/transform level.
No AI is involved. Each level progressively reduces content density while
prioritizing job-relevant content (highest relevance_score projects first).
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class CompressionLevel:
    """Immutable configuration for a single compression pass."""
    level: int
    margin_top: float        # inches
    margin_bottom: float     # inches
    margin_left: float       # inches
    margin_right: float      # inches
    section_before_spacing: int   # pt before section header
    max_project_bullets: int      # max bullet points per project
    max_exp_bullets: int          # max bullet points per experience item
    max_internship_bullets: int   # max bullet points per internship item
    max_projects: int             # max number of projects to include (0 = all)
    include_certifications: bool  # whether to include certifications section
    summary_max_chars: int        # truncate summary if longer than this (0 = no limit)


_LEVELS: list[CompressionLevel] = [
    # Level 0 — Full fidelity, standard margins
    CompressionLevel(
        level=0,
        margin_top=0.50, margin_bottom=0.50, margin_left=0.50, margin_right=0.50,
        section_before_spacing=7,
        max_project_bullets=0,   # 0 = unlimited
        max_exp_bullets=0,
        max_internship_bullets=0,
        max_projects=0,
        include_certifications=True,
        summary_max_chars=0,
    ),
    # Level 1 — Slightly tighter margins + spacing
    CompressionLevel(
        level=1,
        margin_top=0.45, margin_bottom=0.45, margin_left=0.48, margin_right=0.48,
        section_before_spacing=5,
        max_project_bullets=0,
        max_exp_bullets=0,
        max_internship_bullets=0,
        max_projects=0,
        include_certifications=True,
        summary_max_chars=0,
    ),
    # Level 2 — Tight margins + cap project bullets
    CompressionLevel(
        level=2,
        margin_top=0.42, margin_bottom=0.42, margin_left=0.45, margin_right=0.45,
        section_before_spacing=4,
        max_project_bullets=3,
        max_exp_bullets=0,
        max_internship_bullets=0,
        max_projects=0,
        include_certifications=True,
        summary_max_chars=0,
    ),
    # Level 3 — Cap all experience/internship bullets
    CompressionLevel(
        level=3,
        margin_top=0.40, margin_bottom=0.40, margin_left=0.43, margin_right=0.43,
        section_before_spacing=4,
        max_project_bullets=3,
        max_exp_bullets=3,
        max_internship_bullets=3,
        max_projects=0,
        include_certifications=True,
        summary_max_chars=0,
    ),
    # Level 4 — Limit to top-3 projects by relevance score
    CompressionLevel(
        level=4,
        margin_top=0.38, margin_bottom=0.38, margin_left=0.42, margin_right=0.42,
        section_before_spacing=3,
        max_project_bullets=3,
        max_exp_bullets=3,
        max_internship_bullets=3,
        max_projects=3,
        include_certifications=True,
        summary_max_chars=0,
    ),
    # Level 5 — Maximum compression: top-2 projects, drop certifications
    CompressionLevel(
        level=5,
        margin_top=0.36, margin_bottom=0.36, margin_left=0.40, margin_right=0.40,
        section_before_spacing=3,
        max_project_bullets=2,
        max_exp_bullets=3,
        max_internship_bullets=2,
        max_projects=2,
        include_certifications=False,
        summary_max_chars=350,
    ),
]

MAX_COMPRESSION_LEVEL: int = len(_LEVELS) - 1


def get_compression_level(level: int) -> CompressionLevel:
    """
    Returns the compression configuration for a given level (0–MAX_COMPRESSION_LEVEL).
    Clamps to MAX_COMPRESSION_LEVEL if level exceeds the defined range.
    """
    clamped = max(0, min(level, MAX_COMPRESSION_LEVEL))
    return _LEVELS[clamped]
