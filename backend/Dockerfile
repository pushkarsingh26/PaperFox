# ──────────────────────────────────────────────────────────────────────────────
# PaperFox Backend — Production Dockerfile
#
# Produces a self-contained image that includes:
#   • Python 3.12 (slim)
#   • TeX Live (subset) — pdflatex + all packages used by PaperFox templates:
#       inputenc, fontenc, geometry, hyperref, enumitem, titlesec, xcolor,
#       microtype (via texlive-latex-extra + texlive-fonts-recommended)
#   • FastAPI / Uvicorn application
#
# The user's browser / laptop does NOT need any LaTeX installation.
# All PDF compilation happens inside this container.
# ──────────────────────────────────────────────────────────────────────────────

FROM python:3.12-slim

# ---------------------------------------------------------------------------
# System dependencies + TeX Live packages required by PaperFox templates
#
# Packages installed and their purpose:
#   texlive-latex-base         — pdflatex engine, core LaTeX classes & tools
#   texlive-latex-extra        — geometry, enumitem, titlesec, microtype
#   texlive-fonts-recommended  — standard fonts (lm, etc.) used by article class
#   texlive-latex-recommended  — hyperref, xcolor
#   ca-certificates            — HTTPS for MongoDB Atlas TLS verification
#
# We clean apt caches in the same RUN layer to keep the image layer small.
# ---------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
        texlive-latex-base \
        texlive-latex-extra \
        texlive-latex-recommended \
        texlive-fonts-recommended \
        ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Verify pdflatex is on PATH after install (build-time smoke test)
RUN pdflatex --version

# ---------------------------------------------------------------------------
# Python application
# ---------------------------------------------------------------------------
WORKDIR /app

# Install Python dependencies first (layer caching — only re-runs on requirements change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# ---------------------------------------------------------------------------
# Runtime configuration
#
# These are safe defaults. Override via docker run -e or docker-compose
# environment:, never commit real secrets.
#
# LATEX_COMPILER is resolvable via PATH inside the container (texlive installs
# pdflatex to /usr/bin/pdflatex), so LATEX_COMPILER_PATH is left empty.
# ---------------------------------------------------------------------------
ENV LATEX_COMPILER=pdflatex \
    LATEX_COMPILER_PATH="" \
    ENVIRONMENT=production \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Create artifact storage directory with correct permissions
RUN mkdir -p /app/storage_data/pdf

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
