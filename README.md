# PaperFox — AI-Powered Job-Specific Resume Optimization Platform

**PaperFox** is an intelligent, deterministic resume optimization and application tracking platform. It transforms a candidate's master profile into factually grounded, job-tailored, single-page, ATS-compliant resumes in LaTeX and PDF formats, with multi-provider AI routing, persistent project evidence extraction, and comprehensive application lifecycle tracking.

---

## 🚀 Core Workflow

```text
       ┌───────────────────────────────┐
       │     1. Candidate Profile      │
       │   Master Source of Truth      │
       └──────────────┬────────────────┘
                      │
                      ▼
       ┌───────────────────────────────┐
       │     2. Project Evidence       │
       │  (Self vs AI Analysis Text    │
       │   → Structured Evidence)      │
       └──────────────┬────────────────┘
                      │
                      ▼
       ┌───────────────────────────────┐
       │     3. Job Application        │
       │  JD Intelligence & Extraction │
       └──────────────┬────────────────┘
                      │
                      ▼
       ┌───────────────────────────────┐
       │   4. Resume Optimization      │
       │ Fact-Grounded Skill Matching  │
       │ (Multi-Provider Free AI Fallback)
       └──────────────┬────────────────┘
                      │
                      ▼
       ┌───────────────────────────────┐
       │     5. Deterministic LaTeX    │
       │  Dynamic Progressive Fitting  │
       │    & One-Page ATS Validator   │
       └──────────────┬────────────────┘
                      │
                      ▼
       ┌───────────────────────────────┐
       │     6. Application History    │
       │  Status Tracking, Notes & PDF │
       └───────────────────────────────┘
```

---

## 🏗 Architecture & Boundary Principles

PaperFox enforces strict architectural invariants across all layers:

1. **Master Candidate Profile is Immutable to Jobs**: The candidate's master profile remains the permanent source of truth and is never altered by job-specific optimizations.
2. **Job Contexts are Independent Snapshots**: Every job application maintains its own immutable optimization snapshot, resume artifacts, and status history.
3. **AI Produces Content, Deterministic Code Controls Layout**: LLMs never format or design resumes. Content is generated into strict JSON schemas, validated against facts, transformed deterministically, and rendered via LaTeX.
4. **Isolated Storage Abstraction**: Generated PDF binaries are never stored directly in MongoDB. They are persisted in isolated artifact storage (`storage_data/pdf/`) with secure database references.
5. **Multi-Tenant Ownership & Zero Leaks**: Every endpoint strictly enforces user ownership. Cross-user data access is impossible, and unhandled server errors are masked with unique tracing `error_id`s.

```text
Frontend (Next.js 16 / React 19 / TypeScript / Tailwind CSS)
   │
   ▼ HTTPS / REST (Axios Interceptors, Auto-Refresh Rotation)
FastAPI Backend (Python 3.10+ / Starlette / Pydantic v2)
   │
   ├── Security & Observability Middlewares
   │   ├── SecurityHeadersMiddleware (nosniff, DENY, referrer policy)
   │   ├── RateLimitMiddleware (In-memory sliding window: 10 auth/min, 30 AI/min)
   │   └── Global Exception Masking (Returns safe JSON with UUID error_id)
   │
   ├── Service Layer
   │   ├── AuthService & UserService (Bcrypt, JWT access & refresh sessions)
   │   ├── ProfileService & ProjectEvidenceParser (Structured evidence extraction)
   │   ├── JobService & OptimizerService (Factual grounding & keyword alignment)
   │   └── JobResumeService (Progressive compression levels 0–5 & ATS validation)
   │
   ├── AI Provider Layer (Multi-Provider Fallback Router)
   │   ├── Tier 1: Google Gemini (gemini-2.5-flash)
   │   ├── Tier 2: Groq (openai/gpt-oss-20b)
   │   ├── Tier 3: OpenRouter (nvidia/nemotron-3.5-lightning:free)
   │   └── Tier 4: OpenRouter (liquid/lfm-2.5-2.6b:free)
   │
   ├── PDF/LaTeX Worker Layer
   │   └── LaTeXCompilerWorker (pdflatex / xelatex isolated subprocess execution)
   │
   └── Data & Persistence Layer
       ├── MongoDB Atlas (Motor async driver, compound & unique indexes)
       └── Local/Volume PDF Storage (StorageProvider filesystem abstraction)
```

---

## 📦 Phases 1–8 Implementation Summary

| Phase | Milestone | Deliverables |
|---|---|---|
| **Phase 1** | Foundation & Authentication | FastAPI architecture, MongoDB Atlas integration, JWT access & refresh token rotation, server-side session revocation, Next.js frontend scaffolding. |
| **Phase 2** | Candidate Profile System | Structured schema for personal details, skills grouped by category, education, experience, internships, projects, and completion percentage calculation. |
| **Phase 3** | LaTeX Resume Engine | Deterministic LaTeX escaping engine, Jinja2 template integration, isolated PDF compilation worker, fallback `COMPILER_UNAVAILABLE` handling, binary storage abstraction. |
| **Phase 4** | Job Workspace & JD Intelligence | Job description management, automated requirement extraction (skills, experience, keywords), provider fallback routing. |
| **Phase 5** | Job-Specific AI Optimization | Factually grounded resume optimization, anti-hallucination validation, keyword alignment analysis, immutable job optimization snapshots. |
| **Phase 6** | One-Page ATS Validation | Progressive 6-level deterministic compression (margin fitting, bullet limits, summary trimming), page count enforcement, comprehensive ATS validator. |
| **Phase 7** | Evidence Extraction & App History | Dual project description modes (Self vs AI analysis text), structured evidence extraction, application tracking (Draft, Applied, Interview, Offer, Rejected, Withdrawn), notes, history stats. |
| **Phase 8** | Global Production Hardening | Sliding-window rate limiting, security headers, global exception masking with UUID tracking, safe `/health` database check, comprehensive 99-test regression suite, production build validation. |

---

## 🛠 Tech Stack

- **Backend**: Python 3.10+, FastAPI, Starlette, Pydantic v2, Motor (Async MongoDB), PyJWT, Passlib / Bcrypt, PyPDF.
- **Frontend**: Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS, Lucide React, Axios.
- **Database**: MongoDB Atlas / MongoDB 6.0+.
- **AI Providers**: Google Gemini API, Groq Cloud API, OpenRouter API (100% Free-Tier Models).
- **Document Engine**: LaTeX (`pdflatex` / `xelatex`), Jinja2.
- **Testing**: Pytest, Pytest-Asyncio, HTTPX, MongoMock-Motor.

---

## ⚙ Environment Variables

### Backend Configuration (`backend/.env`)

Template available in `backend/.env.example`:

```env
# Application & Environment
PROJECT_NAME="PaperFox"
API_V1_STR="/api/v1"
ENVIRONMENT="production"            # "development" or "production"

# Authentication & Security
SECRET_KEY="replace-with-a-secure-random-32-byte-hex-string"
REFRESH_SECRET_KEY="replace-with-another-secure-random-32-byte-hex-string"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
SECURE_COOKIES=true

# Database (MongoDB Atlas or Local MongoDB)
MONGODB_URL="mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority"
DATABASE_NAME="paperfox"

# Production CORS Allowed Origins (Comma-separated or JSON array)
ALLOWED_ORIGINS="https://your-domain.com,https://paperfox.app"

# Rate Limiting
RATE_LIMITING_ENABLED=true
RATE_LIMIT_AUTH_PER_MINUTE=10
RATE_LIMIT_AI_PER_MINUTE=30

# Free-Tier AI Providers (Configure any or all for automated fallback)
GEMINI_API_KEY="your-google-gemini-api-key"
GROQ_API_KEY="your-groq-cloud-api-key"
OPENROUTER_API_KEY="your-openrouter-api-key"

# PDF & LaTeX Worker
PDF_STORAGE_DIR="storage_data/pdf"
LATEX_COMPILER_BINARY="pdflatex"
```

### Frontend Configuration (`frontend/.env.local`)

Template available in `frontend/.env.example`:

```env
# Base API URL pointing to the FastAPI backend
NEXT_PUBLIC_API_URL="https://api.your-domain.com/api/v1"
```

---

## 🚦 Local Setup & Running Locally

### 1. Backend Setup

```bash
cd backend

# Create virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
python -m pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Run FastAPI backend server
python -m uvicorn app.main:app --reload --port 8000
```

- API Base: `http://localhost:8000`
- Interactive Swagger UI: `http://localhost:8000/api/v1/docs` (in development mode)
- Health Check: `http://localhost:8000/health`

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local

# Run Next.js development server
npm run dev
```

- Web UI: `http://localhost:3000`

---

## 🤖 AI Provider & Multi-Tier Fallback Strategy

PaperFox is designed to operate on **100% free AI models** with zero downtime or single-provider lock-in:

1. **Google Gemini Flash**: Primary provider (`gemini-2.5-flash`) for high-throughput, structured JSON generation.
2. **Groq Cloud**: Tier 2 fallback (`openai/gpt-oss-20b`) for sub-second failover.
3. **OpenRouter Tier 3**: `nvidia/nemotron-3.5-lightning:free` for high-capacity backup.
4. **OpenRouter Tier 4**: `liquid/lfm-2.5-2.6b:free` for final resilience.

The `ProviderRouter` handles network timeouts, HTTP 429 rate limits, HTTP 5xx failures, and JSON schema validation failures by automatically promoting requests down the fallback chain with full provider and model attribution.

---

## 📄 Resume Rendering & Deterministic One-Page ATS Pipeline

```text
OptimizedResumeData
   │
   ├── Progressive Compression Transformer (Levels 0 to 5)
   │   ├── Level 0: Full fidelity (0.50in margins, no bullet caps)
   │   ├── Level 1: Tight margins (0.40in margins)
   │   ├── Level 2: Compact bullets (Max 3 bullets per project)
   │   ├── Level 3: Ultra-tight margins (0.35in) & summary truncation (250 chars)
   │   ├── Level 4: Project prioritization (Max 2 most relevant projects)
   │   └── Level 5: Extreme compression (1 project, 2 bullets, omit certifications)
   │
   ├── LaTeX Jinja2 Template Renderer (With character escaping)
   │
   ├── Isolated LaTeX Worker (pdflatex/xelatex subprocess compilation)
   │
   └── Deterministic ATS Validator
       ├── Page count check (strictly targets 1 page)
       ├── Content section presence verification
       └── Overflow detection & reporting
```

---

## 🔒 Security & Production Hardening

- **JWT Authentication**: Short-lived access tokens (30 min) + rotating refresh tokens stored in hashed format in MongoDB.
- **Session Revocation**: Full server-side invalidation upon logout; revoked tokens cannot be reused.
- **Resource Ownership**: Strict multi-tenant isolation; cross-user attempts return 404 to avoid ID enumeration.
- **Security Headers**: Standard headers injected on all routes (`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy`).
- **Sliding-Window Rate Limiter**: In-memory rate limiting preventing brute-force authentication attacks (10 req/min/IP) and AI abuse (30 req/min/user).
- **Error Masking**: Global uncaught exception handler prevents stack trace and environment leakage, logging full traces internally and returning an opaque `error_id`.

---

## 🧪 Verification & Test Suite

### Full Backend Test Suite (99 Passing Tests)

```bash
cd backend
python -m pytest -v
```

Tests cover:
- Health checks and simulated database disconnection
- Response security headers & exception trace masking
- Sliding-window auth and AI rate limiting
- Multi-user data isolation and authorization
- Full 22-step end-to-end integration lifecycle test
- Complete regression across authentication, profiles, jobs, optimization, resume rendering, and application history

### Frontend Production Build

```bash
cd frontend
npm run build
```

Build verifies 100% type safety and zero static page generation errors across all Next.js App Router endpoints.

---

## 🌐 Production Deployment Architecture

```text
       Internet / End Users
                │
                ▼ HTTPS
       [ Cloudflare / CDN / Reverse Proxy ]
                │
       ┌────────┴───────────────────────────┐
       │                                    │
       ▼                                    ▼
[ Next.js Frontend ]               [ FastAPI Backend ]
  (Vercel / Node.js)                 (Docker / Gunicorn / Uvicorn)
                                            │
                                            ├── [ MongoDB Atlas Cluster ]
                                            ├── [ Free AI Providers (Gemini/Groq/OpenRouter) ]
                                            └── [ Isolated LaTeX Compilation Worker ]
```

---

## 📜 License

MIT License. Built with precision for production reliability.
