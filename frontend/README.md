# PaperFox — Frontend Web Application

The frontend user interface for **PaperFox**, built with Next.js 16 (App Router), React 19, TypeScript, and Tailwind CSS.

## Architecture

- **Framework**: [Next.js 16](https://nextjs.org/) (App Router)
- **UI Components**: React 19, custom utility design system with [Tailwind CSS](https://tailwindcss.com/)
- **Icons & Visuals**: Lucide React & PaperFox Fox Vector System
- **State & Communication**: Axios with automatic JWT token refresh interceptors and React Context (`AuthContext`)

## Directory Overview

```text
src/
├── app/
│   ├── (auth)/             # Login and candidate account creation
│   ├── dashboard/
│   │   ├── page.tsx        # Overview & pipeline metrics
│   │   ├── profile/        # Master Candidate Profile editor
│   │   ├── jobs/           # Job workspace, JD Intelligence, and optimization
│   │   ├── applications/   # Applications lifecycle tracking
│   │   ├── mailing/        # Cold outreach email draft manager
│   │   └── resume/         # Base resume preview & compiler diagnostics
│   ├── layout.tsx          # Root layout with PaperFox metadata & favicon
│   └── page.tsx            # High-conversion product landing page
├── components/             # Reusable UI primitives, modal dialogs, and panels
│   └── ui/FoxLogo.tsx      # Authoritative PaperFox brand mark component
├── context/                # Authentication context provider
├── lib/                    # API client, service helpers, and data mappers
└── types/                  # TypeScript interface definitions
```

## Running Locally

```bash
# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Set NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Start development server
npm run dev
```

Visit `http://localhost:3000` in your browser.
