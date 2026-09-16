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
    # Level 0 — Full fidelity, reference A4 page density
    CompressionLevel(
        level=0,
        margin_top=0.38, margin_bottom=0.38, margin_left=0.40, margin_right=0.40,
        section_before_spacing=4,
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
        margin_top=0.36, margin_bottom=0.36, margin_left=0.38, margin_right=0.38,
        section_before_spacing=3,
        max_project_bullets=0,
        max_exp_bullets=0,
        max_internship_bullets=0,
        max_projects=0,
        include_certifications=True,
        summary_max_chars=0,
    ),
    # Level 2 — Tight margins + cap project bullets to 3
    CompressionLevel(
        level=2,
        margin_top=0.35, margin_bottom=0.35, margin_left=0.38, margin_right=0.38,
        section_before_spacing=3,
        max_project_bullets=3,
        max_exp_bullets=0,
        max_internship_bullets=0,
        max_projects=0,
        include_certifications=True,
        summary_max_chars=0,
    ),
    # Level 3 — Cap all experience/internship bullets + summary limit
    CompressionLevel(
        level=3,
        margin_top=0.34, margin_bottom=0.34, margin_left=0.36, margin_right=0.36,
        section_before_spacing=2,
        max_project_bullets=3,
        max_exp_bullets=3,
        max_internship_bullets=3,
        max_projects=0,
        include_certifications=True,
        summary_max_chars=400,
    ),
    # Level 4 — Limit to top-3 projects by relevance score
    CompressionLevel(
        level=4,
        margin_top=0.32, margin_bottom=0.32, margin_left=0.35, margin_right=0.35,
        section_before_spacing=2,
        max_project_bullets=3,
        max_exp_bullets=3,
        max_internship_bullets=3,
        max_projects=3,
        include_certifications=True,
        summary_max_chars=350,
    ),
    # Level 5 — Maximum compression: top-2 projects, summary cap 300
    CompressionLevel(
        level=5,
        margin_top=0.30, margin_bottom=0.30, margin_left=0.34, margin_right=0.34,
        section_before_spacing=2,
        max_project_bullets=2,
        max_exp_bullets=2,
        max_internship_bullets=2,
        max_projects=2,
        include_certifications=False,
        summary_max_chars=300,
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
