"use client";

import React from "react";
import Link from "next/link";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import {
  FileText,
  Sparkles,
  ShieldCheck,
  Cpu,
  ArrowRight,
  Check,
  Layers,
  Terminal,
} from "lucide-react";
import { useAuth } from "@/context/AuthContext";

export default function LandingPage() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-between selection:bg-amber-500/30 selection:text-amber-200">
      {/* Navigation Header */}
      <header className="h-20 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-lg fixed top-0 left-0 right-0 z-50 px-6 lg:px-12 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-600 to-amber-400 flex items-center justify-center shadow-lg shadow-amber-600/20">
            <FileText className="w-5 h-5 text-slate-950 font-bold" />
          </div>
          <span className="font-bold text-xl text-white tracking-tight">
            Paper<span className="text-amber-500">Fox</span>
          </span>
        </div>

        <div className="flex items-center space-x-4">
          {user ? (
            <Link href="/dashboard">
              <Button variant="primary" size="md">
                Go to Dashboard
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </Link>
          ) : (
            <>
              <Link href="/login">
                <Button variant="ghost" size="sm">
                  Sign In
                </Button>
              </Link>
              <Link href="/signup">
                <Button variant="primary" size="sm">
                  Get Started
                </Button>
              </Link>
            </>
          )}
        </div>
      </header>

      {/* Hero Section */}
      <main className="pt-32 pb-20 px-6 lg:px-12 max-w-7xl mx-auto space-y-24">
        <section className="text-center space-y-8 max-w-4xl mx-auto pt-8">
          <div className="inline-flex items-center">
            <Badge variant="warning" className="px-3.5 py-1 text-xs uppercase tracking-wider">
              <Sparkles className="w-3.5 h-3.5 mr-1.5" /> Phase 1 Foundation Live
            </Badge>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold text-white tracking-tight leading-tight">
            Precision Job-Specific{" "}
            <span className="bg-gradient-to-r from-amber-400 via-amber-500 to-amber-200 bg-clip-text text-transparent">
              Resume Optimization
            </span>
          </h1>

          <p className="text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed">
            PaperFox maps your master candidate profile directly to job specifications, generating ATS-compliant, one-page LaTeX resumes tailored for targeted applications.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <Link href="/signup" className="w-full sm:w-auto">
              <Button size="lg" className="w-full sm:w-auto text-base">
                Create Account
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </Link>
            <Link href="/login" className="w-full sm:w-auto">
              <Button variant="outline" size="lg" className="w-full sm:w-auto text-base">
                Candidate Login
              </Button>
            </Link>
          </div>
        </section>

        {/* Core Flow Architecture */}
        <section className="space-y-6">
          <div className="text-center space-y-2">
            <h2 className="text-2xl font-bold text-white">Target Product Architecture</h2>
            <p className="text-sm text-slate-400">
              The end-to-end pipeline driving precision job-matched resume compilation.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 relative">
            <Card className="p-5 text-center space-y-2 border-amber-500/20 bg-amber-950/10">
              <div className="w-8 h-8 rounded-lg bg-amber-500/10 text-amber-400 flex items-center justify-center mx-auto text-sm font-bold">
                1
              </div>
              <h3 className="text-sm font-semibold text-slate-200">Candidate Profile</h3>
              <p className="text-xs text-slate-400">Master experience, skills & projects repository.</p>
            </Card>

            <Card className="p-5 text-center space-y-2 border-slate-800">
              <div className="w-8 h-8 rounded-lg bg-slate-800 text-slate-300 flex items-center justify-center mx-auto text-sm font-bold">
                2
              </div>
              <h3 className="text-sm font-semibold text-slate-200">Job Specification</h3>
              <p className="text-xs text-slate-400">Company, role target & JD requirements analysis.</p>
            </Card>

            <Card className="p-5 text-center space-y-2 border-sky-500/20 bg-sky-950/10">
              <div className="w-8 h-8 rounded-lg bg-sky-500/10 text-sky-400 flex items-center justify-center mx-auto text-sm font-bold">
                3
              </div>
              <h3 className="text-sm font-semibold text-slate-200">AI Optimization</h3>
              <p className="text-xs text-slate-400">Relevance scoring & bullet prioritization.</p>
            </Card>

            <Card className="p-5 text-center space-y-2 border-emerald-500/20 bg-emerald-950/10">
              <div className="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center mx-auto text-sm font-bold">
                4
              </div>
              <h3 className="text-sm font-semibold text-slate-200">LaTeX Resume</h3>
              <p className="text-xs text-slate-400">Overleaf-compatible LaTeX template binding.</p>
            </Card>

            <Card className="p-5 text-center space-y-2 border-purple-500/20 bg-purple-950/10">
              <div className="w-8 h-8 rounded-lg bg-purple-500/10 text-purple-400 flex items-center justify-center mx-auto text-sm font-bold">
                5
              </div>
              <h3 className="text-sm font-semibold text-slate-200">ATS-Safe PDF</h3>
              <p className="text-xs text-slate-400">Validated 1-page PDF binary compilation.</p>
            </Card>
          </div>
        </section>

        {/* Phase 1 Implemented Features */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <Card className="space-y-4">
            <div className="w-10 h-10 rounded-xl bg-amber-500/10 text-amber-400 flex items-center justify-center">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-white">Secure JWT Authentication</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Bcrypt password hashing with access token rotation and server-side refresh session invalidation.
            </p>
            <ul className="space-y-2 text-xs text-slate-300">
              <li className="flex items-center"><Check className="w-3.5 h-3.5 mr-2 text-emerald-400" /> Short-lived access JWTs</li>
              <li className="flex items-center"><Check className="w-3.5 h-3.5 mr-2 text-emerald-400" /> Server-side token hash revocation</li>
            </ul>
          </Card>

          <Card className="space-y-4">
            <div className="w-10 h-10 rounded-xl bg-sky-500/10 text-sky-400 flex items-center justify-center">
              <Layers className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-white">Layered FastAPI Architecture</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Clean separation of routes, business logic services, and MongoDB data repositories.
            </p>
            <ul className="space-y-2 text-xs text-slate-300">
              <li className="flex items-center"><Check className="w-3.5 h-3.5 mr-2 text-emerald-400" /> Thin API route handlers</li>
              <li className="flex items-center"><Check className="w-3.5 h-3.5 mr-2 text-emerald-400" /> Async Motor database layer</li>
            </ul>
          </Card>

          <Card className="space-y-4">
            <div className="w-10 h-10 rounded-xl bg-purple-500/10 text-purple-400 flex items-center justify-center">
              <Cpu className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-white">Extensible Provider Contracts</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Abstract boundary interfaces ready for future LLM engine and LaTeX compiler integrations.
            </p>
            <ul className="space-y-2 text-xs text-slate-300">
              <li className="flex items-center"><Check className="w-3.5 h-3.5 mr-2 text-emerald-400" /> Abstract LLMProvider interface</li>
              <li className="flex items-center"><Check className="w-3.5 h-3.5 mr-2 text-emerald-400" /> Abstract PDFWorkerProvider contract</li>
            </ul>
          </Card>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-8 px-6 lg:px-12 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <p>© {new Date().getFullYear()} PaperFox. All rights reserved.</p>
          <p className="font-mono">Phase 1 Foundation • FastAPI + Next.js + MongoDB</p>
        </div>
      </footer>
    </div>
  );
}
