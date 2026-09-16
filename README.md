<p align="center">
  <img src="assets/paperfox-cover.png" alt="PaperFox — AI-Powered Job-Specific Resume Optimization" width="100%" />
</p>

<h1 align="center">PaperFox</h1>

<p align="center">
  <strong>AI-Powered Job-Specific Resume Optimization & Application Platform</strong>
</p>

<p align="center">
  Turn every job description into a tailored, evidence-grounded, single-page ATS resume with deterministic LaTeX rendering and factual verification.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/FastAPI-0.110%2B-009688?logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Next.js-16-black?logo=next.js&logoColor=white" alt="Next.js 16" />
  <img src="https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black" alt="React 19" />
  <img src="https://img.shields.io/badge/MongoDB-Atlas%20%2F%20Async%20Motor-47A248?logo=mongodb&logoColor=white" alt="MongoDB" />
  <img src="https://img.shields.io/badge/LaTeX-pdflatex%20%2F%20TeX%20Live-008080?logo=latex&logoColor=white" alt="LaTeX" />
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white" alt="Docker" />
  <img src="https://img.shields.io/badge/License-MIT-green" alt="MIT License" />
</p>

---

## Overview

Applying to modern software engineering roles with a generic resume leads to poor keyword alignment, low ATS pass-rates, and missed opportunities. Conversely, using unconstrained generative AI tools often introduces fabricated claims—hallucinating libraries, inflated metrics, and non-existent production experience.

**PaperFox** solves this dilemma. It is an intelligent resume optimization and job application tracking platform that tailors a candidate's master profile to individual job descriptions while enforcing **strict factual grounding**. PaperFox guarantees that every project claim, technology mention, and timeline is verified against the candidate's master profile and structured project evidence.

The platform separates content generation from document presentation: multi-provider AI models reason over requirements and draft structured content, while a deterministic LaTeX engine formats and compresses the resume to fit an exact, single-page, ATS-readable PDF.

```text
Master Profile ──► JD Intelligence ──► Missing Skill Diff ──► Candidate Selection
                                                                       │
One-Page ATS PDF ◄── Deterministic LaTeX ◄── Factual Validation ◄──────┘
```

---

## Why PaperFox

| Traditional Resumes | Unconstrained AI Tools | PaperFox Platform |
|---|---|---|
| **Generic & Static**: One static resume sent to hundreds of varied roles. | **Hallucinatory**: Invented tools, frameworks, metrics, and fake responsibilities. | **Factually Grounded**: Optimizes strictly against verified candidate profile facts and repository evidence. |
| **Manual Editing**: Tedious word processing, margin shifting, and broken layouts. | **Uncontrolled Layout**: Arbitrary formatting, awkward page overflows, and broken ATS tables. | **Deterministic LaTeX**: Programmatic layout engine with automated 6-level compression enforcing an exact 1-page budget. |
| **No JD Visibility**: Blind guessing about what keywords the employer prioritizes. | **Black-Box Rewrites**: Unchecked text generation without candidate oversight. | **Candidate in Control**: Highlights missing skills and requires explicit candidate confirmation before inclusion. |
| **Disconnected Outreach**: Cold emails written from scratch without job context. | **Generic AI Spam**: Fluffy, generic outreach emails full of cliché buzzwords. | **Personalized Outreach**: Evidence-backed hiring-team cold outreach drafts based on extracted JD requirements. |

---

## Key Differentiators

- **Evidence-Grounded Generation**: Bullet points and project summaries are grounded in the candidate's verified codebase evidence, preventing fabricated accomplishments.
- **Strict Factual Validation**: Deterministic post-generation validators reject any optimization attempt that alters degrees, institutions, employers, job titles, or dates.
- **Candidate-Controlled Skill Diff**: PaperFox calculates the exact delta between JD requirements and candidate skills. The candidate explicitly selects which matching skills they possess before they are included.
- **Deterministic One-Page LaTeX Layout**: Resumes are compiled via TeX Live (`pdflatex`). Progressive compression levels (0–5) adjust spacing, bullet limits, and summary length deterministically until the document fits an exact single page.
- **Multi-Provider AI Fallback Router**: Zero vendor lock-in. PaperFox routes requests across a tiered chain of free-tier AI providers (Google Gemini, Groq, OpenRouter, NVIDIA) with automatic failover, timeout management, and schema retries.
- **Reusable JD Intelligence**: Deep analysis extracts required skills, preferred qualifications, frameworks, AI/ML requirements, and core responsibilities into an immutable job snapshot.
- **Personalized Mailing System**: Drafts humanized, professional cold emails to hiring teams by matching candidate project evidence to specific job requirements—free of generic AI boilerplate.
- **Multi-Tenant Data Isolation**: Complete user ownership enforcement across all endpoints, paired with rate limiting and secure session token rotation.

> [!NOTE]
> PaperFox does not make misleading claims of "AI detector bypass" or guaranteed hiring outcomes. It provides engineering rigor: clean ATS readability, factual truthfulness, and targeted relevance.

---

## Core Features

### 1. Master Candidate Profile
- **Persistent Source of Truth**: Stores personal contact details, categorized technical skills, education history, work experience, internships, and certifications.
- **Profile Completion Engine**: Dynamically calculates profile completeness percentage to ensure all prerequisite data is in place before optimization.
- **Immutability Invariant**: Job optimizations never overwrite or pollute the master profile.

### 2. Job Workspace & Application Tracking
- **Lifecycle Management**: Track application progression through structured stages: `draft`, `applied`, `interview`, `offer`, `rejected`, and `withdrawn`.
- **Status & Notes**: Append timestamped recruiter feedback, interview notes, and compensation details directly to the job record.
- **History Analytics**: Overview counters provide immediate visibility into active pipelines and conversion rates.

### 3. JD Intelligence Engine
- **Structured Requirement Extraction**: Deconstructs plain-text job postings into structured categories: required skills, preferred skills, programming languages, frameworks/libraries, AI/ML stacks, and role responsibilities.
- **Keyword & Priority Identification**: Ranks critical technologies to drive project relevance scoring and resume alignment.

### 4. Missing Skill Diff & Candidate Approval
- **Automated Set Difference**: Computes normalized missing skills: $\text{JD Skills} \setminus \text{Candidate Facts}$.
- **Dynamic Category Mapping**: Maps missing requirements to the candidate's existing profile categories.
- **Candidate Confirmation Gate**: Missing skills are never automatically injected. The candidate reviews the diff and explicitly selects only the tools they actually know.

### 5. Project Evidence System
- **Dual-Description Architecture**: Projects store both high-level candidate descriptions and raw codebase AI analysis text (`ai_analysis_text`).
- **Structured Evidence Extraction**: Parses analysis text into verified architectural patterns, frameworks, databases, APIs, models, deployment tools, and verified engineering decisions.
- **Idempotent Storage**: Caches evidence with status indicators (`current`, `stale`, `missing`) to avoid redundant AI extraction runs.

### 6. AI Resume Optimization
- **Modular Task Generation**: Dedicated prompts independently optimize the professional summary, select and rank the top relevant projects, reorder bullet points, and categorize technical skills.
- **Anti-Buzzword Sanitization**: Strips generic phrasing (*"cutting-edge"*, *"spearheaded"*, *"seamlessly"*, *"AI-powered"*) and removes markdown bolding and redundant technology repetition.
- **Relevance Scoring**: Ranks candidate projects against job requirements so the most pertinent engineering work is featured prominently.

### 7. ATS Validation & Deterministic PDF Engine
- **TeX Live Compilation**: Resumes compile using Jinja2-templated LaTeX source into text-based vector PDFs.
- **Progressive 6-Level Compression**: An automated loop tests levels 0 to 5, adjusting margins (0.38in down to 0.30in), bullet limits, and summary length until a strict 1-page boundary is satisfied.
- **ATS Verification**: Inspects page count, vector text extractability, and the presence of core structural sections (Summary, Skills, Experience, Education).
- **Graceful Compiler Fallback**: If `pdflatex` is not installed on the host, PaperFox generates and persists the complete LaTeX source, sets status to `compiler_unavailable`, and provides platform-specific installation instructions without generating mock PDFs.

### 8. Multi-Tier AI Provider Routing
- **Ordered Fallback Chain**: Primary requests route through Google Gemini (`gemini-2.5-flash`), falling back automatically to Groq (`openai/gpt-oss-20b`), OpenRouter (`nvidia/nemotron-3.5-lightning:free` and `liquid/lfm-2.5-2.6b:free`), or NVIDIA NIM.
- **Resilience Engine**: Handles HTTP 429 rate limits, 5xx server errors, network timeouts, and JSON schema validation failures with bounded retries.

### 9. Hiring-Team Mailing System
- **Job-Grounded Outreach**: Synthesizes existing JD Intelligence, the target company and role, and the candidate's strongest verified project evidence into an outreach draft.
- **Multiple Subject Options**: Generates 3–4 professional, concise subject line variants alongside a recommended choice.
- **Dual Body Variants**: Generates a standard outreach body and a concise 2–3 paragraph short version suitable for direct messaging.
- **Humanized Tone Rules**: Enforces peer-to-peer technical communication while strictly barring generic email openings (*"I hope this email finds you well"*, *"I am thrilled to apply"*).
- **Editable Drafts**: Saves drafts directly to the job application record, allowing candidates to customize recipients, subjects, and text prior to sending.

---

## Resume Optimization Pipeline

```mermaid
flowchart TD
    A[Job Description] --> B[JD Intelligence Engine]
    B --> C[Structured Requirements & Keywords]
    
    D[Master Candidate Profile] --> E[Candidate Fact Graph]
    F[Project Codebase Analysis] --> G[Structured Project Evidence]
    G --> E
    
    C --> H[Missing Skills Diff Engine]
    E --> H
    H --> I[Suggested Missing Skills]
    
    I --> J{Candidate Review & Selection}
    J -->|Explicitly Approved Skills| K[Job-Specific Confirmed Skills]
    
    K --> L[AI Optimization Engine]
    E --> L
    C --> L
    
    L --> M[Structured OptimizedResumeData]
    M --> N{Deterministic Factual Validation}
    
    N -->|Integrity Violation| O[Reject & Fallback to Master Facts]
    N -->|Validation Passed| P[LaTeX Jinja2 Template Renderer]
    
    P --> Q[Deterministic Compression Loop: Levels 0-5]
    Q --> R[Isolated pdflatex Worker]
    
    R --> S{Page Count == 1?}
    S -->|Page Count > 1 & Level < 5| Q
    S -->|Single Page Enforced| T[Save Artifact to Storage]
    
    T --> U[ATS Compliance Validation]
    U --> V[Final 1-Page ATS Resume PDF]
```

---

## Mailing System Architecture

The PaperFox Mailing System generates targeted cold outreach drafts for hiring managers, recruiters, and engineering leads. It reuses existing job context and candidate evidence without requiring redundant data entry.

```mermaid
sequenceDiagram
    autonumber
    actor Candidate as Candidate
    participant UI as Next.js Workspace
    participant API as FastAPI Backend
    participant MailSvc as MailingService
    participant Router as AI Provider Router
    participant DB as MongoDB Atlas

    Candidate->>UI: Request Cold Outreach Draft (Job ID)
    UI->>API: POST /jobs/{job_id}/mailing/generate
    API->>MailSvc: generate_mailing_draft(user_id, job_id, req)
    MailSvc->>DB: Fetch Job Application (Requirements & JD)
    MailSvc->>DB: Fetch Master Profile & Project Evidence
    
    Note over MailSvc: Build prompt with candidate facts,<br/>JD requirements, and strict anti-boilerplate rules.
    
    MailSvc->>Router: generate_structured_json(MailingAIResponse Schema)
    Router-->>MailSvc: Subject options, chosen subject, body, short_body, cited evidence
    
    Note over MailSvc: Deterministic sanitization:<br/>strip bolding, normalize spacing, verify evidence
    
    MailSvc->>DB: Persist draft inside Job Application document
    MailSvc-->>API: Return MailingDraft response
    API-->>UI: Display interactive outreach editor
    
    Candidate->>UI: Edit recipient, subject line, or body
    UI->>API: PUT /jobs/{job_id}/mailing
    API->>DB: Save updated draft
    Candidate->>UI: Copy draft to clipboard
```

### Key Outreach Principles
- **No Fabricated Recipients**: If recipient details are not provided by the candidate, PaperFox defaults to professional company greetings (`Hello [Company] Hiring Team,`). It never fabricates recipient names.
- **Evidence-Backed Claims**: The email highlights only verified projects and tools that solve the specific technical needs identified in the JD.
- **No Automatic Dispatch**: PaperFox does not connect to external SMTP servers or automatically blast emails. It generates an editable, high-quality draft for the candidate to review, refine, and send through their own email client.

---

## AI Provider Architecture

PaperFox eliminates third-party dependencies on expensive proprietary APIs by utilizing an abstract provider framework connected to **100% free-tier AI endpoints**.

```text
               ┌────────────────────────────────────────────────────────┐
               │              AI Provider Router Interface              │
               │   (Timeout: 30s | Retries: 2 | Structured JSON Schema) │
               └───────────────────────────┬────────────────────────────┘
                                           │
                    ┌──────────────────────┴──────────────────────┐
                    ▼                                             ▼
       ┌────────────────────────┐                    ┌────────────────────────┐
       │ Primary: Google Gemini │                    │ Fallback 1: Groq Cloud │
       │   (gemini-2.5-flash)   │                    │  (openai/gpt-oss-20b)  │
       └───────────┬────────────┘                    └───────────┬────────────┘
                   │ (On 429 / 5xx / Timeout)                    │ (On Failure)
                   └──────────────────────┬──────────────────────┘
                                          ▼
                             ┌────────────────────────┐
                             │ Fallback 2: OpenRouter │
                             │  (nemotron / liquid)   │
                             └────────────┬───────────┘
                                          ▼ (Optional NIM)
                             ┌────────────────────────┐
                             │ Fallback 3: NVIDIA NIM │
                             │  (llama-3.1-70b-inst)  │
                             └────────────────────────┘
```

### Provider Matrix

| Provider | Model Identifier | Role | Strengths |
|---|---|---|---|
| **Google Gemini** | `gemini-2.5-flash` | Primary Provider | High-throughput structured JSON output and rapid context ingestion. |
| **Groq Cloud** | `openai/gpt-oss-20b` | Tier 1 Fallback | Near-instant sub-second inference for failover continuity. |
| **OpenRouter** | `nvidia/nemotron-3.5-lightning:free` | Tier 2 Fallback | High reasoning capacity for complex requirement synthesis. |
| **OpenRouter** | `liquid/lfm-2.5-2.6b:free` | Tier 3 Fallback | High-availability lightweight backup model. |
| **NVIDIA NIM** | `meta/llama-3.1-70b-instruct` | Optional Tier | Enterprise-grade instruct model for detailed technical summaries. |

---

## Deterministic Resume Rendering & Compression Engine

To guarantee that generated resumes pass automated screening systems without human intervention, PaperFox uses a deterministic progressive compression engine.

```text
Optimized Resume Data
        │
        ├── Level 0: Reference Margins (0.38in top/bottom, 0.40in sides), 4pt section spacing, full bullets
        │            Compile with pdflatex ──► Page Count == 1? ──► [DONE]
        │
        ├── Level 1: Margins: 0.36in / 0.38in, 3pt section spacing
        │            Compile with pdflatex ──► Page Count == 1? ──► [DONE]
        │
        ├── Level 2: Margins: 0.35in / 0.38in, Cap project bullets to max 3
        │            Compile with pdflatex ──► Page Count == 1? ──► [DONE]
        │
        ├── Level 3: Margins: 0.34in / 0.36in, Cap all experience bullets to 3, summary <= 400 chars
        │            Compile with pdflatex ──► Page Count == 1? ──► [DONE]
        │
        ├── Level 4: Margins: 0.32in / 0.35in, Keep top-3 projects by relevance, summary <= 350 chars
        │            Compile with pdflatex ──► Page Count == 1? ──► [DONE]
        │
        └── Level 5: Maximum compression: Margins: 0.30in / 0.34in, top-2 projects, summary <= 300 chars, omit certs
                     Compile with pdflatex ──► Final 1-Page Vector PDF Artifact
```

### LaTeX Engine Safety Invariants
1. **Character Escaping**: All dynamic text passes through a LaTeX sanitization engine that escapes reserved characters (`&`, `%`, `$`, `#`, `_`, `{`, `}`, `~`, `^`, `\`).
2. **Deterministic Layout**: Formatting is defined strictly by the Jinja2 LaTeX template; LLMs never generate styling commands.
3. **Subprocess Isolation**: LaTeX compilation runs in an isolated subprocess with explicit timeouts and temporary directory cleanup.
4. **Binary Isolation**: PDF binaries are persisted to dedicated volume storage (`storage_data/pdf/`) and referenced via UUID in MongoDB.

---

## Data & Factual Integrity Model

PaperFox maintains a clear distinction between candidate facts and job requirements. The platform enforces the following integrity axioms:

```text
┌──────────────────────────────────────┐       ┌──────────────────────────────────────┐
│       Master Candidate Profile       │       │            Job Description           │
│   (Persistent Source of Truth)       │       │    (Target Requirements & Context)   │
└──────────────────┬───────────────────┘       └──────────────────┬───────────────────┘
                   │                                              │
                   ▼                                              ▼
┌──────────────────────────────────────┐       ┌──────────────────────────────────────┐
│      Verified Project Evidence       │       │           JD Intelligence            │
│  (Codebase Analysis & Concrete Tech) │       │ (Required Skills & Keyword Priorities)│
└──────────────────┬───────────────────┘       └──────────────────┬───────────────────┘
                   │                                              │
                   └──────────────────────┬───────────────────────┘
                                          │
                                          ▼
                       ┌─────────────────────────────────────┐
                       │     Candidate Missing Skill Gate    │
                       │ (Only Candidate-Confirmed Additions)│
                       └──────────────────┬──────────────────┘
                                          │
                                          ▼
                       ┌─────────────────────────────────────┐
                       │      Job-Specific Optimization      │
                       │    (Factual Grounding Enforced)     │
                       └─────────────────────────────────────┘
```

### Fundamental Integrity Axioms

$$\text{JD Requirement} \neq \text{Candidate Skill}$$
A skill required by a job description is never assumed to be possessed by the candidate. It is presented as a diff and requires explicit candidate confirmation.

$$\text{Candidate-Confirmed Skill} \neq \text{Project Evidence}$$
When a candidate confirms a missing skill that they understand, it may appear in the resume's **Technical Skills** section. However, the AI is strictly prohibited from fabricating project bullet points or experience claiming they used that tool in past work.

$$\text{Factual Immutability Invariant}$$
The post-optimization validator deterministically verifies that degrees, universities, companies, job titles, and dates match the master profile exactly. Any deviation triggers an immediate validation failure and rolls back the generation.

---

## Technology Stack

| Layer | Technology | Description |
|---|---|---|
| **Frontend Framework** | Next.js 16.3.5 (App Router) | Server-rendered and client-interactive modern React architecture. |
| **UI Library & Styling** | React 19, Tailwind CSS 4 | Responsive interface with custom utility styling. |
| **Icons & Design** | Lucide React | Clean, modern iconography across workspaces. |
| **HTTP Client** | Axios 1.20 | Configured with request/response interceptors for automatic JWT refresh. |
| **Backend Framework** | FastAPI 0.110+, Starlette | Asynchronous, high-performance REST API with OpenAPI documentation. |
| **Data Validation** | Pydantic v2, Pydantic-Settings | Strict runtime schema enforcement and environment configuration. |
| **Database & Driver** | MongoDB Atlas / MongoDB 6.0+, Motor 3.3+ | Non-blocking asynchronous MongoDB driver with unique compound indexes. |
| **Security & Auth** | PyJWT, Passlib (Bcrypt) | Short-lived access tokens, refresh token hashing, and server-side revocation. |
| **AI Integration** | Custom HTTP client (HTTPX) | Resilient provider router connecting to Gemini, Groq, OpenRouter, and NVIDIA. |
| **Document Compiler** | TeX Live (`pdflatex`) | Deterministic vector PDF generation with Jinja2 templating. |
| **Containerization** | Docker, Docker Compose | Production multi-stage builds with TeX Live pre-installed in the backend image. |

---

## System Architecture

```mermaid
graph TD
    Client["Browser / Next.js 16 Frontend"]
    
    subgraph FastAPI_Backend ["FastAPI Application (Port 8000)"]
        SecurityMW["SecurityHeadersMiddleware<br/>(nosniff, DENY, ReferrerPolicy)"]
        RateLimitMW["RateLimitMiddleware<br/>(10 auth/min, 30 AI/min)"]
        Router["API Router (/api/v1)"]
        
        subgraph Services ["Application Service Layer"]
            AuthSvc["AuthService & UserService"]
            ProfileSvc["ProfileService"]
            EvidenceSvc["ProjectEvidenceService"]
            JobSvc["JobService"]
            OptSvc["OptimizerService"]
            ResumeSvc["JobResumeService"]
            MailSvc["MailingService"]
            HistorySvc["ApplicationHistoryService"]
        end
        
        subgraph Workers ["Document Workers & Routers"]
            AIRouter["ProviderRouter<br/>(Gemini ➔ Groq ➔ OpenRouter)"]
            TeXWorker["LaTeXCompilerWorker<br/>(pdflatex subprocess)"]
        end
    end
    
    subgraph Data_Storage ["Data & Artifact Storage"]
        Mongo[("MongoDB Atlas<br/>Users, Profiles, Jobs, Drafts")]
        PDFStore[("Persistent Volume<br/>storage_data/pdf/")]
    end
    
    Client -->|HTTPS / REST| SecurityMW
    SecurityMW --> RateLimitMW
    RateLimitMW --> Router
    
    Router --> AuthSvc
    Router --> ProfileSvc
    Router --> EvidenceSvc
    Router --> JobSvc
    Router --> ResumeSvc
    Router --> MailSvc
    Router --> HistorySvc
    
    JobSvc --> OptSvc
    OptSvc --> AIRouter
    EvidenceSvc --> AIRouter
    MailSvc --> AIRouter
    
    ResumeSvc --> TeXWorker
    TeXWorker --> PDFStore
    
    AuthSvc --> Mongo
    ProfileSvc --> Mongo
    JobSvc --> Mongo
    MailSvc --> Mongo
    HistorySvc --> Mongo
    ResumeSvc --> Mongo
```

---

## Project Structure

```text
PaperFox/
├── docker-compose.yml              # Production multi-container composition
├── README.md                       # Comprehensive project documentation
├── assets/
│   └── paperfox-cover.png          # High-resolution project presentation banner
│
├── backend/
│   ├── Dockerfile                  # Multi-stage image with Python & TeX Live
│   ├── requirements.txt            # Locked backend dependencies
│   ├── pyproject.toml              # Project configuration & tool settings
│   ├── .env.example                # Backend environment variable template
│   └── app/
│       ├── main.py                 # FastAPI initialization, CORS, middlewares & health
│       ├── api/
│       │   ├── deps.py             # Dependency injection (Auth, Services, Repos)
│       │   └── v1/
│       │       ├── router.py       # V1 route aggregator
│       │       └── endpoints/
│       │           ├── auth.py     # Login, signup, refresh, logout, me
│       │           ├── users.py    # User identity management
│       │           ├── profile.py  # Master candidate profile endpoints
│       │           ├── profile_evidence.py # Project evidence extraction API
│       │           ├── jobs.py     # Jobs, JD intelligence, optimization, mailing
│       │           └── resume.py   # Base resume generation & compiler diagnostics
│       ├── core/
│       │   ├── config.py           # Pydantic settings schema & validation
│       │   ├── database.py         # Async Motor client lifecycle & ping
│       │   ├── middleware.py       # Sliding-window rate limiter & security headers
│       │   └── security.py         # Bcrypt hashing & JWT token creation/decoding
│       ├── models/                 # Database document representations
│       ├── repositories/           # MongoDB Atlas persistence layer
│       ├── schemas/                # Pydantic request and response schemas
│       ├── services/
│       │   ├── ai/
│       │   │   ├── provider_router.py      # Resilient multi-provider fallback router
│       │   │   ├── optimizer_service.py    # Modular resume optimization tasks
│       │   │   └── project_evidence_parser.py # Structured evidence extraction
│       │   ├── job_service.py              # Job workspace & JD intelligence
│       │   ├── job_resume_service.py       # Deterministic compression & ATS check
│       │   ├── mailing_service.py          # Cold outreach generation & drafts
│       │   └── project_evidence_service.py # Evidence cache management
│       ├── providers/
│       │   ├── ai/                         # Gemini, Groq, OpenRouter, NVIDIA providers
│       │   └── pdf/                        # LaTeX worker & subprocess manager
│       ├── resume/
│       │   ├── compression.py              # Progressive compression level definitions
│       │   ├── escaping.py                 # Comprehensive LaTeX character escaping
│       │   ├── job_resume_renderer.py      # Jinja2 template rendering engine
│       │   └── templates/                  # Production LaTeX resume templates
│       ├── storage/                        # PDF volume storage abstraction
│       └── utils/                          # Factual validation & normalizers
│
└── frontend/
    ├── Dockerfile                  # Standalone Next.js container build
    ├── package.json                # Next.js 16, React 19, Tailwind CSS dependencies
    ├── tsconfig.json               # TypeScript configuration
    ├── .env.example                # Frontend environment variable template
    └── src/
        ├── app/
        │   ├── layout.tsx          # Root layout with AuthProvider & metadata
        │   ├── page.tsx            # High-conversion landing page
        │   ├── (auth)/             # Login and signup routes
        │   └── dashboard/
        │       ├── page.tsx        # Application overview & metric cards
        │       ├── profile/        # Master profile multi-step editor
        │       ├── jobs/           # Job workspace, JD analysis, optimization
        │       ├── resume/         # Base resume preview & compiler setup
        │       ├── mailing/        # Cold outreach draft manager
        │       └── applications/   # Kanban / list application tracker
        ├── components/             # Reusable UI, dialogs, forms, and editors
        ├── context/                # Authentication context & token management
        ├── lib/                    # Axios client, interceptors, and API wrappers
        └── types/                  # TypeScript interface definitions
```

---

## Getting Started

### Prerequisites

- **Docker & Docker Compose** (Recommended for easiest setup, as TeX Live is pre-configured)
- *Alternatively, for local native setup:*
  - **Python 3.10+**
  - **Node.js 20+** and **npm**
  - **MongoDB 6.0+** (or a free MongoDB Atlas cluster URI)
  - **LaTeX distribution** (`pdflatex`): MiKTeX (Windows) or TeX Live (Linux/macOS)

---

### Option A: Running with Docker Compose (Recommended)

Docker Compose provisions the entire platform—including Next.js and FastAPI with a complete TeX Live installation inside the container—without requiring local LaTeX packages.

1. **Clone the repository**:
   ```bash
   git clone https://github.com/pushkarsingh26/PaperFox.git
   cd PaperFox
   ```

2. **Configure backend environment**:
   ```bash
   cp backend/.env.example backend/.env
   ```
   *Open `backend/.env` and supply your `MONGODB_URL` and free AI provider API keys (e.g., `GOOGLE_API_KEY`).*

3. **Start services**:
   ```bash
   docker compose up -d --build
   ```

4. **Access the application**:
   - Web Interface: `http://localhost:3000`
   - FastAPI REST API: `http://localhost:8000`
   - API Documentation: `http://localhost:8000/api/v1/docs` (when `ENVIRONMENT=development`)

---

### Option B: Local Native Setup

#### 1. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit backend/.env with your secrets and API keys

# Start FastAPI development server
python -m uvicorn app.main:app --reload --port 8000
```

#### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment variables
cp .env.example .env.local
# Set NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Start Next.js development server
npm run dev
```

#### 3. LaTeX Compiler Verification

Check your compiler setup at any time via the API:
```bash
curl http://localhost:8000/api/v1/resume/compiler-status
```
If `pdflatex` is installed outside standard system paths, specify its location in `backend/.env`:
```env
LATEX_COMPILER_PATH="C:\Users\<user>\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe"
```

---

## Environment Variables

### Backend Configuration (`backend/.env`)

| Variable | Purpose | Default / Example | Required |
|---|---|---|:---:|
| `PROJECT_NAME` | Name of the platform | `PaperFox` | No |
| `API_V1_STR` | Base API routing prefix | `/api/v1` | No |
| `ENVIRONMENT` | Runtime environment (`development` / `production`) | `production` | No |
| `SECRET_KEY` | HMAC secret for JWT access tokens | *32+ random hex characters* | **Yes** |
| `REFRESH_SECRET_KEY` | HMAC secret for JWT refresh tokens | *32+ random hex characters* | **Yes** |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifespan | `30` | No |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifespan | `7` | No |
| `SECURE_COOKIES` | Enforce secure HTTPS flags on cookies | `true` | No |
| `MONGODB_URL` | MongoDB connection URI | `mongodb+srv://user:pass@cluster.mongodb.net` | **Yes** |
| `DATABASE_NAME` | MongoDB database identifier | `paperfox` | No |
| `ALLOWED_ORIGINS` | Permitted CORS origins | `["http://localhost:3000"]` | **Yes** |
| `RATE_LIMITING_ENABLED` | Toggle sliding-window rate limiting | `true` | No |
| `RATE_LIMIT_AUTH_PER_MINUTE` | Auth route request cap per IP | `10` | No |
| `RATE_LIMIT_AI_PER_MINUTE` | AI task request cap per user | `30` | No |
| `LATEX_COMPILER` | LaTeX binary executable name | `pdflatex` | No |
| `LATEX_COMPILER_PATH` | Explicit path to LaTeX executable | *Empty (relies on PATH)* | No |
| `GOOGLE_API_KEY` | Google Gemini API key | `AIzaSy...` | Optional* |
| `GOOGLE_MODEL` | Primary Gemini model identifier | `gemini-2.5-flash` | No |
| `GROQ_API_KEY` | Groq Cloud API key | `gsk_...` | Optional* |
| `GROQ_MODEL` | Primary Groq model identifier | `openai/gpt-oss-20b` | No |
| `OPENROUTER_API_KEY` | OpenRouter API key | `sk-or-v1-...` | Optional* |
| `OPENROUTER_MODEL` | OpenRouter primary backup model | `nvidia/nemotron-3.5-lightning:free` | No |
| `NVIDIA_API_KEY` | NVIDIA NIM API key | `nvapi-...` | Optional* |
| `JD_ANALYSIS_PRIMARY_PROVIDER`| Primary provider routing target | `gemini` | No |
| `JD_ANALYSIS_FALLBACK_PROVIDERS`| Ordered fallback array | `["groq", "openrouter"]` | No |

*\*At least one valid AI provider key must be supplied for optimization and extraction features.*

### Frontend Configuration (`frontend/.env.local`)

| Variable | Purpose | Default / Example | Required |
|---|---|---|:---:|
| `NEXT_PUBLIC_API_URL` | Target FastAPI endpoint URL | `http://localhost:8000/api/v1` | **Yes** |

---

## End-to-End Workflow

```text
 1. Sign Up & Login
    Create an account to initialize an isolated candidate record.

 2. Build Master Candidate Profile
    Populate contact details, categorized skills, education, work experience, and certifications.

 3. Ingest Project Evidence
    Provide codebase analysis text for projects to extract verified architectures, frameworks, and metrics.

 4. Create a Job Application
    Add target company, role title, and paste the full job description into the Job Workspace.

 5. Execute JD Intelligence
    Run automated extraction to identify required skills, preferred tools, and core keywords.

 6. Review Missing Skill Diff
    Inspect the delta between JD requirements and candidate skills categorized under profile headings.

 7. Approve Matching Skills
    Explicitly select only the missing skills you possess for inclusion in this job's resume.

 8. Optimize Resume
    Generate a tailored resume snapshot with anti-hallucination validation and relevance ranking.

 9. Compile & Verify One-Page PDF
    Trigger LaTeX rendering with automated compression level adjustments to produce a 1-page ATS PDF.

10. Generate Hiring-Team Outreach Draft
    Produce an evidence-backed cold email draft with selectable subject lines for recruiter outreach.
```

---

## API Overview

All API endpoints are prefixed with `/api/v1`. Authenticated routes require a standard `Authorization: Bearer <token>` header.

### Authentication & Users
- `POST /auth/signup` — Register a new account and receive access/refresh token pair.
- `POST /auth/login` — Authenticate credentials and receive token pair.
- `POST /auth/refresh` — Issue a new token pair using a valid refresh token.
- `POST /auth/logout` — Invalidate the server-side refresh session.
- `GET /auth/me` — Retrieve identity details for the authenticated user.

### Master Candidate Profile
- `GET /profile` — Retrieve the current user's master candidate profile.
- `POST /profile` — Create or overwrite the master candidate profile.
- `PUT /profile` — Incrementally update specific profile sections.
- `DELETE /profile` — Permanently delete the candidate profile.

### Project Evidence
- `POST /profile/projects/{project_id}/extract-evidence` — Parse codebase analysis text into structured technical evidence (`?force=true` forces re-extraction).
- `GET /profile/projects/{project_id}/evidence` — Retrieve cached structured evidence for a project.

### Job Applications & JD Intelligence
- `POST /jobs` — Create a new job application with company, role, and JD text.
- `GET /jobs` — List all job applications owned by the user.
- `GET /jobs/{job_id}` — Retrieve complete application details and analysis state.
- `POST /jobs/{job_id}/analyze` — Run JD Intelligence extraction via the AI provider chain.
- `POST /jobs/{job_id}/approved-skills` — Persist candidate-approved missing skills for optimization.
- `DELETE /jobs/{job_id}` — Delete a job application and all associated snapshots.

### Resume Optimization & LaTeX Compilation
- `POST /jobs/{job_id}/optimize` — Execute fact-grounded resume optimization for the target role.
- `GET /jobs/{job_id}/optimization` — Retrieve the stored `OptimizedResumeData` snapshot.
- `POST /jobs/{job_id}/render` — Execute deterministic LaTeX compilation and progressive compression.
- `GET /jobs/{job_id}/resume` — Retrieve PDF artifact metadata, page count, and ATS validation results.
- `GET /jobs/{job_id}/resume/download` — Download the compiled one-page resume PDF binary.
- `GET /resume/compiler-status` — Inspect host LaTeX compiler availability and paths.

### Mailing System
- `POST /jobs/{job_id}/mailing/generate` — Generate an evidence-grounded cold outreach email draft.
- `GET /jobs/{job_id}/mailing` — Retrieve the stored mailing draft for a job application.
- `PUT /jobs/{job_id}/mailing` — Update editable draft fields (recipient, subject, body, status).

### Application Lifecycle Tracking
- `GET /jobs/history` — Query application history with optional status filters (`draft`, `applied`, etc.).
- `GET /jobs/history/stats` — Retrieve aggregated application counts across lifecycle stages.
- `PATCH /jobs/{job_id}/status` — Update application status without altering resume artifacts.
- `PATCH /jobs/{job_id}/notes` — Append interview notes and follow-up reminders.

---

## Security & Privacy Architecture

- **Token Security**: Employs short-lived JWT access tokens (30-minute expiration) paired with cryptographically secure, hashed refresh tokens stored in MongoDB.
- **Server-Side Session Revocation**: Logging out invalidates the refresh session server-side, preventing token reuse.
- **Strict Multi-Tenant Isolation**: Every database query enforces the authenticated `user_id`. Unauthorized access attempts return generic 404 responses to prevent ID enumeration.
- **Defensive Security Headers**: Injected across all responses:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Permissions-Policy: geolocation=(), microphone=(), camera=()`
- **Sliding-Window Rate Limiting**: In-memory rate limiting prevents brute-force authentication attacks (10 requests/min/IP) and protects AI endpoints from runaway usage (30 requests/min/user).
- **Error Masking**: Global exception handlers capture unhandled server errors, log the complete trace internally, and return a sanitized JSON response containing an opaque tracking `error_id`.
- **Isolated Artifact Storage**: PDF binaries are saved to disk or mounted container volumes (`storage_data/pdf/`), ensuring the core database remains lightweight and performant.

---

## Roadmap

- [ ] **Multi-Template LaTeX Switcher**: Choose between Classic Academic, Modern Minimalist, and Technical Compact LaTeX designs.
- [ ] **Browser Extension**: 1-click import of job descriptions directly from LinkedIn, Indeed, and Ashby into the PaperFox Job Workspace.
- [ ] **Application Stage Reminders**: Automated notifications for follow-ups and interview scheduling.
- [ ] **Interview Question Generator**: Generate technical interview practice questions based on the candidate's verified project evidence and target JD requirements.
- [ ] **Multi-Language Support**: Locale-based resume formatting and translation for global job markets.

---

## License

Distributed under the [MIT License](https://opensource.org/licenses/MIT). Built with engineering discipline for reliability and factual integrity.
