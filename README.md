# PaperFox — Phase 1: Foundation & Authentication

PaperFox is a job-specific resume optimization platform designed to map candidate master profiles to specific company and job descriptions, automatically compiling ATS-compliant, single-page LaTeX resumes.

Phase 1 provides the production-ready architectural foundation: FastAPI backend with Motor/MongoDB Atlas, secure JWT authentication with refresh token rotation and server-side session revocation, future provider abstraction boundaries, and a Next.js + TypeScript + Tailwind CSS frontend.

---

## 🏗 Architecture

```text
Frontend (Next.js 14+ / TypeScript / Tailwind CSS)
   ↓ HTTP / REST API (Axios Interceptors)
FastAPI API Layer (/api/v1/auth & /api/v1/users)
   ↓ Dependency Injection
Service Layer (AuthService, UserService)
   ↓ Clean Data Access
Repository Layer (UserRepository, SessionRepository)
   ↓ Async Motor Driver
MongoDB Atlas Database
```

---

## 🛠 Prerequisites

- **Python**: `3.10+` (Tested on Python `3.14`)
- **Node.js**: `18.x` or `20.x+` (with `npm`)
- **MongoDB**: MongoDB Atlas URI (or local MongoDB for development)

---

## ⚙ Environment Variables

### Backend Configuration (`backend/.env`)

Template provided in `backend/.env.example`:

| Variable | Description | Example / Default |
|---|---|---|
| `PROJECT_NAME` | Application Name | `PaperFox` |
| `API_V1_STR` | API Version Prefix | `/api/v1` |
| `SECRET_KEY` | JWT Access Token Secret Key | `32+ char secret string` |
| `REFRESH_SECRET_KEY` | JWT Refresh Token Secret Key | `32+ char secret string` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access Token Lifetime | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh Token Lifetime | `7` |
| `MONGODB_URL` | MongoDB Atlas Connection String | `mongodb+srv://user:pass@cluster...` |
| `DATABASE_NAME` | Database Name | `paperfox` |
| `ALLOWED_ORIGINS` | CORS Allowed Origins | `["http://localhost:3000"]` |

### Frontend Configuration (`frontend/.env.local`)

Template provided in `frontend/.env.example`:

| Variable | Description | Default |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Backend API Base Endpoint | `http://localhost:8000/api/v1` |

---

## 🚀 Quickstart & Development Commands

### 1. Backend Setup

```bash
cd backend

# Install dependencies
python -m pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Run FastAPI development server
python -m uvicorn app.main:app --reload --port 8000
```

The backend server will run on `http://localhost:8000` with interactive OpenAPI docs available at `http://localhost:8000/docs`.

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env.local

# Run Next.js development server
npm run dev
```

The frontend application will be available at `http://localhost:3000`.

---

## 🧪 Testing

### Running Backend Unit & Integration Tests

The test suite uses `mongomock_motor` so tests run in-memory without needing active production MongoDB credentials.

```bash
cd backend
python -m pytest
```

Test coverage includes:
1. User registration & email normalization
2. Duplicate email rejection
3. Bcrypt password hashing
4. Login credentials validation
5. Invalid credentials rejection
6. Unauthenticated endpoint access rejection
7. Invalid token rejection
8. Protected route access with valid JWT token
9. Refresh token rotation & reissue
10. Invalid/expired refresh token rejection
11. Server-side session logout
12. Post-logout refresh token reuse prevention

### Running Frontend Build & Type Validation

```bash
cd frontend
npm run build
```

---

## 📄 Phase 3: LaTeX Resume Engine

The LaTeX Resume Engine transforms the candidate's Master Candidate Profile into a normalized `ResumeData` structure, escapes LaTeX special characters, renders the document template, and compiles it via `pdflatex`/`xelatex`.

### Template & Rendering Boundaries
- **Template Location**: `backend/app/resume/templates/base_resume.tex`
- **Escaping Engine**: `backend/app/resume/escaping.py` (escapes `&`, `%`, `$`, `#`, `_`, `{`, `}`, `~`, `^`, `\`, and formats `\href` URLs)
- **Data Transformer**: `backend/app/resume/transformer.py` (converts profile to `ResumeData` without mutating MongoDB profile)
- **PDF Storage**: `backend/app/storage/pdf_storage.py` (stores binary PDFs in `storage_data/pdf/` and saves `storage://` references in MongoDB)

### Server Compiler Requirements
- Binary compilation requires local `pdflatex` or `xelatex` installed on the host system (e.g. TeX Live or MiKTeX).
- If no system LaTeX compiler is found on the server environment, the API returns a structured `COMPILER_UNAVAILABLE` response with the saved `.tex` source without generating substitute PDFs.

---

## 🔐 API Overview

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/v1/auth/signup` | Register new user & return token pair | No |
| `POST` | `/api/v1/auth/login` | Authenticate credentials & return token pair | No |
| `POST` | `/api/v1/auth/refresh` | Rotate & refresh token pair | No |
| `POST` | `/api/v1/auth/logout` | Revoke refresh token & invalidate session | No |
| `GET` | `/api/v1/auth/me` | Fetch authenticated user profile | Yes |
| `GET` | `/api/v1/profile` | Fetch candidate master profile | Yes |
| `POST` | `/api/v1/profile` | Upsert candidate master profile | Yes |
| `PUT` | `/api/v1/profile` | Update candidate master profile | Yes |
| `DELETE` | `/api/v1/profile` | Delete candidate master profile | Yes |
| `POST` | `/api/v1/resume/generate` | Generate/regenerate base LaTeX resume | Yes |
| `GET` | `/api/v1/resume/base` | Fetch base resume artifact metadata | Yes |
| `GET` | `/api/v1/resume/base/pdf` | Serve compiled base resume PDF binary | Yes |

---

## 📁 Repository Structure

```text
PaperFox/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   ├── auth.py
│   │   │       │   └── users.py
│   │   │       └── router.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── security.py
│   │   ├── models/
│   │   │   └── user.py
│   │   ├── providers/
│   │   │   ├── ai/
│   │   │   │   └── base.py
│   │   │   └── pdf/
│   │   │       └── base.py
│   │   ├── repositories/
│   │   │   ├── base.py
│   │   │   ├── session_repository.py
│   │   │   └── user_repository.py
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   └── user.py
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   └── user_service.py
│   │   └── main.py
│   ├── tests/
│   │   ├── conftest.py
│   │   └── test_auth.py
│   ├── .env.example
│   ├── pyproject.toml
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── (auth)/
│   │   │   │   ├── login/page.tsx
│   │   │   │   └── signup/page.tsx
│   │   │   ├── dashboard/page.tsx
│   │   │   ├── globals.css
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx
│   │   ├── components/
│   │   │   ├── auth/ProtectedRoute.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── Navbar.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── SystemStatusCard.tsx
│   │   │   └── ui/
│   │   │       ├── Badge.tsx
│   │   │       ├── Button.tsx
│   │   │       ├── Card.tsx
│   │   │       └── Input.tsx
│   │   ├── context/AuthContext.tsx
│   │   ├── lib/
│   │   │   ├── api.ts
│   │   │   └── auth.ts
│   │   └── types/auth.ts
│   ├── .env.example
│   └── package.json
├── .gitignore
└── README.md
```
