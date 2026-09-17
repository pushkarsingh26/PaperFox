# PaperFox — Production Deployment Guide

**Target architecture:**
```
Browser → Vercel (Next.js) → Cloud Run asia-south1 (FastAPI + pdflatex) → MongoDB Atlas
```

All sensitive credentials are stored in **Google Cloud Secret Manager** — never in source code or environment files committed to Git.

---

## Prerequisites

| Tool | Purpose |
|---|---|
| `gcloud` CLI | Cloud Run, Artifact Registry, Secret Manager |
| Docker (optional) | Local image testing |
| Vercel CLI or vercel.com | Frontend deployment |
| MongoDB Atlas account | Existing database |

---

## Step 1 — GCP Project Setup

```bash
# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com

# Create Artifact Registry repository (Mumbai)
gcloud artifacts repositories create paperfox \
  --repository-format=docker \
  --location=asia-south1 \
  --description="PaperFox Docker images"

# Authenticate Docker to push images
gcloud auth configure-docker asia-south1-docker.pkg.dev
```

---

## Step 2 — Create Secrets in Secret Manager

Run each command once. Replace placeholder values with your real credentials.

```bash
# MongoDB Atlas connection string
echo -n "mongodb+srv://USER:PASS@cluster.mongodb.net/?retryWrites=true&w=majority" \
  | gcloud secrets create paperfox-mongodb-url --data-file=-

# JWT signing secrets (generate with: python -c "import secrets; print(secrets.token_hex(32))")
echo -n "YOUR_32_CHAR_RANDOM_HEX_ACCESS_SECRET" \
  | gcloud secrets create paperfox-secret-key --data-file=-

echo -n "YOUR_32_CHAR_RANDOM_HEX_REFRESH_SECRET" \
  | gcloud secrets create paperfox-refresh-secret-key --data-file=-

# AI provider keys
echo -n "AIzaSy..." \
  | gcloud secrets create paperfox-google-api-key --data-file=-

echo -n "gsk_..." \
  | gcloud secrets create paperfox-groq-api-key --data-file=-

echo -n "sk-or-..." \
  | gcloud secrets create paperfox-openrouter-api-key --data-file=-

echo -n "nvapi-..." \
  | gcloud secrets create paperfox-nvidia-api-key --data-file=-

# CORS origins — fill in your Vercel URL after Step 5
# Update this secret after you know your Vercel domain
echo -n '["https://YOUR-APP.vercel.app","http://localhost:3000"]' \
  | gcloud secrets create paperfox-allowed-origins --data-file=-
```

Grant Cloud Run's service account access to read these secrets:

```bash
# Get the default Cloud Run service account email
PROJECT_NUMBER=$(gcloud projects describe YOUR_PROJECT_ID --format="value(projectNumber)")
CR_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:${CR_SA}" \
  --role="roles/secretmanager.secretAccessor"
```

---

## Step 3 — MongoDB Atlas Network Access

Ensure your Atlas cluster allows connections from Cloud Run.

In MongoDB Atlas → Network Access:
- Add IP: **`0.0.0.0/0`** (allow all — Cloud Run IPs are dynamic)

Or use a more restrictive VPC connector approach if needed later.

---

## Step 4 — Deploy Backend to Cloud Run

### Option A: One-command via Cloud Build (recommended)

```bash
# From the project root
gcloud builds submit . \
  --config cloudbuild.yaml \
  --substitutions _PROJECT_ID=YOUR_PROJECT_ID
```

This builds the image, pushes it to Artifact Registry, and deploys to Cloud Run.

### Option B: Manual steps

```bash
IMAGE="asia-south1-docker.pkg.dev/YOUR_PROJECT_ID/paperfox/backend"

# Build and push
docker build -t "${IMAGE}:latest" ./BACKENd
docker push "${IMAGE}:latest"

# Deploy
gcloud run deploy paperfox-backend \
  --image "${IMAGE}:latest" \
  --region asia-south1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8000 \
  --memory 1Gi \
  --cpu 1 \
  --timeout 120 \
  --min-instances 0 \
  --max-instances 2 \
  --set-env-vars "ENVIRONMENT=production,DATABASE_NAME=paperfox,LATEX_COMPILER=pdflatex,LATEX_COMPILER_PATH=,GOOGLE_MODEL=gemini-2.5-flash,AI_TIMEOUT_SECONDS=30,AI_MAX_RETRIES=2,JD_ANALYSIS_PRIMARY_PROVIDER=gemini" \
  --set-secrets "MONGODB_URL=paperfox-mongodb-url:latest,SECRET_KEY=paperfox-secret-key:latest,REFRESH_SECRET_KEY=paperfox-refresh-secret-key:latest,GOOGLE_API_KEY=paperfox-google-api-key:latest,GROQ_API_KEY=paperfox-groq-api-key:latest,OPENROUTER_API_KEY=paperfox-openrouter-api-key:latest,NVIDIA_API_KEY=paperfox-nvidia-api-key:latest,ALLOWED_ORIGINS=paperfox-allowed-origins:latest"
```

After deployment, **copy the Cloud Run service URL** shown in the output. It looks like:
```
https://paperfox-backend-XXXXXXXX-el.a.run.app
```

Verify:
```bash
curl https://paperfox-backend-XXXXXXXX-el.a.run.app/health
# Expected: {"status":"healthy","database":"connected","service":"PaperFox","version":"1.0.0"}
```

---

## Step 5 — Deploy Frontend to Vercel

### Using Vercel dashboard (simplest)

1. Push this repository to GitHub.
2. Go to [vercel.com/new](https://vercel.com/new) → Import your GitHub repo.
3. Set **Root Directory** to `frontend`.
4. Under **Environment Variables**, add:
   ```
   Name:  NEXT_PUBLIC_API_URL
   Value: https://paperfox-backend-XXXXXXXX-el.a.run.app/api/v1
   ```
   (Replace with your actual Cloud Run URL from Step 4.)
5. Click **Deploy**.

Vercel auto-detects Next.js and builds it correctly.

### Using Vercel CLI

```bash
cd frontend
npx vercel --prod
# When prompted for environment variables, set NEXT_PUBLIC_API_URL
```

After deployment, note your Vercel domain (e.g. `paperfox-abc123.vercel.app`).

---

## Step 6 — Update CORS with Vercel Domain

Now that you have both URLs, update the CORS secret:

```bash
echo -n '["https://paperfox-abc123.vercel.app","http://localhost:3000"]' \
  | gcloud secrets versions add paperfox-allowed-origins --data-file=-

# Redeploy Cloud Run to pick up the new secret version
gcloud run deploy paperfox-backend \
  --image "asia-south1-docker.pkg.dev/YOUR_PROJECT_ID/paperfox/backend:latest" \
  --region asia-south1 \
  --platform managed
```

---

## Step 7 — Verify End-to-End

1. Open your Vercel URL in a browser.
2. Sign up for an account.
3. Complete your candidate profile.
4. Add a job and paste a JD.
5. Run JD Analysis → Resume Optimization → PDF Download.
6. Use the Mailing System.

---

## Updating Secrets

To rotate any secret:
```bash
echo -n "new-secret-value" \
  | gcloud secrets versions add SECRET-NAME --data-file=-
```

Cloud Run will use the new `latest` version on the next container cold start.
To force an immediate rollout:
```bash
gcloud run deploy paperfox-backend \
  --image "asia-south1-docker.pkg.dev/YOUR_PROJECT_ID/paperfox/backend:latest" \
  --region asia-south1 --platform managed
```

---

## Re-deploying after Code Changes

```bash
# From project root — rebuilds and redeploys in one command
gcloud builds submit . \
  --config cloudbuild.yaml \
  --substitutions _PROJECT_ID=YOUR_PROJECT_ID
```

For frontend changes, just push to GitHub — Vercel auto-deploys on every push to main.

---

## Local Development (unchanged)

```bash
# Backend
cd BACKENd
cp .env.example .env
# Fill in real values in .env
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# Frontend
cd frontend
cp .env.example .env.local
# NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1 (already set)
npm run dev
```

---

## Environment Variables Reference

### Backend (set via Secret Manager in production)

| Variable | Secret Manager Name | Description |
|---|---|---|
| `MONGODB_URL` | `paperfox-mongodb-url` | MongoDB Atlas connection string |
| `SECRET_KEY` | `paperfox-secret-key` | JWT access token signing key |
| `REFRESH_SECRET_KEY` | `paperfox-refresh-secret-key` | JWT refresh token signing key |
| `GOOGLE_API_KEY` | `paperfox-google-api-key` | Google AI Studio (Gemini) key |
| `GROQ_API_KEY` | `paperfox-groq-api-key` | Groq API key |
| `OPENROUTER_API_KEY` | `paperfox-openrouter-api-key` | OpenRouter API key |
| `NVIDIA_API_KEY` | `paperfox-nvidia-api-key` | NVIDIA NIM API key |
| `ALLOWED_ORIGINS` | `paperfox-allowed-origins` | JSON array of allowed CORS origins |

### Frontend (set in Vercel dashboard)

| Variable | Description |
|---|---|
| `NEXT_PUBLIC_API_URL` | Full Cloud Run backend URL including `/api/v1` |
