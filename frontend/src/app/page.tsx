"use client";

import React from "react";
import Link from "next/link";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { FoxLogo } from "@/components/ui/FoxLogo";
import {
  Sparkles,
  FileCheck,
  Brain,
  Mail,
  Layers,
  ArrowRight,
  CheckCircle2,
  FileText,
  Target,
  ShieldCheck,
  Cpu,
  ChevronRight,
} from "lucide-react";
import { useAuth } from "@/context/AuthContext";

export default function LandingPage() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 flex flex-col justify-between selection:bg-amber-500/30 selection:text-amber-200">
      {/* Navigation Header */}
      <header className="h-20 border-b border-slate-800/80 bg-[#090d16]/80 backdrop-blur-xl fixed top-0 left-0 right-0 z-50 px-6 lg:px-12 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-600/20 to-amber-400/20 border border-amber-500/30 flex items-center justify-center shadow-lg shadow-amber-500/10 p-1.5">
            <FoxLogo className="w-7 h-7" size={28} priority />
          </div>
          <span className="font-bold text-xl text-white tracking-tight">
            Paper<span className="text-amber-500">Fox</span>
          </span>
        </div>

        <div className="flex items-center space-x-4">
          {user ? (
            <Link href="/dashboard">
              <Button variant="primary" size="md">
                Open Dashboard
                <ArrowRight className="w-4 h-4 ml-1.5" />
              </Button>
            </Link>
          ) : (
            <>
              <Link href="/login">
                <Button variant="ghost" size="sm" className="text-slate-300 hover:text-white">
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
      <main className="pt-32 pb-24 px-6 lg:px-12 max-w-7xl mx-auto space-y-28">
        <section className="text-center space-y-8 max-w-4xl mx-auto pt-8">
          <div className="inline-flex items-center">
            <Badge variant="amber" dot className="px-4 py-1 text-xs font-semibold uppercase tracking-wider">
              Next-Gen AI Resume & Career Suite
            </Badge>
          </div>

          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold text-white tracking-tight leading-[1.1]">
            Turn Every Job Description Into an{" "}
            <span className="bg-gradient-to-r from-amber-400 via-amber-300 to-amber-500 bg-clip-text text-transparent">
              Interview-Winning Resume
            </span>
          </h1>

          <p className="text-base sm:text-xl text-slate-300 max-w-2xl mx-auto leading-relaxed">
            PaperFox combines deep JD requirement intelligence, verified candidate evidence, and deterministic LaTeX compilation into single-page resumes tailored specifically for the jobs you want.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <Link href={user ? "/dashboard" : "/signup"} className="w-full sm:w-auto">
              <Button size="lg" className="w-full sm:w-auto text-base px-8 py-3.5 shadow-lg shadow-amber-500/20">
                Start Tailoring Resumes
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </Link>
            <Link href={user ? "/dashboard/jobs" : "/login"} className="w-full sm:w-auto">
              <Button variant="outline" size="lg" className="w-full sm:w-auto text-base px-8 py-3.5 border-slate-700 hover:bg-slate-900">
                Explore Job Workspace
              </Button>
            </Link>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-6 pt-6 text-xs text-slate-400">
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" /> 100% Deterministic LaTeX
            </span>
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Evidence-Grounded Facts
            </span>
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Zero ATS Hallucinations
            </span>
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Executive Outreach Engine
            </span>
          </div>
        </section>

        {/* 5-Step Pipeline Workflow */}
        <section className="space-y-8">
          <div className="text-center space-y-2">
            <p className="text-xs font-semibold text-amber-400 uppercase tracking-widest">
              The Architecture of Success
            </p>
            <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
              Precision Resume Engineering Pipeline
            </h2>
            <p className="text-sm text-slate-400 max-w-xl mx-auto">
              How PaperFox turns unstructured job listings and your master work history into interview opportunities.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <Card hover className="p-5 text-center space-y-3 border-slate-800 bg-slate-900/60 flex flex-col justify-between">
              <div className="w-10 h-10 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20 flex items-center justify-center mx-auto text-sm font-bold">
                1
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">Candidate Master Profile</h3>
                <p className="text-xs text-slate-400 mt-1">Single source of truth for experiences, verified metrics, and project evidence.</p>
              </div>
            </Card>

            <Card hover className="p-5 text-center space-y-3 border-slate-800 bg-slate-900/60 flex flex-col justify-between">
              <div className="w-10 h-10 rounded-xl bg-sky-500/10 text-sky-400 border border-sky-500/20 flex items-center justify-center mx-auto text-sm font-bold">
                2
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">Target Job Analysis</h3>
                <p className="text-xs text-slate-400 mt-1">Paste any job description to extract required skills, keywords, and priority signals.</p>
              </div>
            </Card>

            <Card hover className="p-5 text-center space-y-3 border-slate-800 bg-slate-900/60 flex flex-col justify-between">
              <div className="w-10 h-10 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 flex items-center justify-center mx-auto text-sm font-bold">
                3
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">AI Tailoring Engine</h3>
                <p className="text-xs text-slate-400 mt-1">Intelligent bullet point ranking, keyword matching, and candidate evidence alignment.</p>
              </div>
            </Card>

            <Card hover className="p-5 text-center space-y-3 border-slate-800 bg-slate-900/60 flex flex-col justify-between">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center justify-center mx-auto text-sm font-bold">
                4
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">Deterministic LaTeX</h3>
                <p className="text-xs text-slate-400 mt-1">Mathematical single-page typesetting with zero layout breaking or overflowing.</p>
              </div>
            </Card>

            <Card hover className="p-5 text-center space-y-3 border-slate-800 bg-slate-900/60 flex flex-col justify-between">
              <div className="w-10 h-10 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20 flex items-center justify-center mx-auto text-sm font-bold">
                5
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">Outreach & Tracking</h3>
                <p className="text-xs text-slate-400 mt-1">Cold emails, hiring manager messages, and end-to-end application stage pipeline.</p>
              </div>
            </Card>
          </div>
        </section>

        {/* Feature Bento Grid */}
        <section className="space-y-8">
          <div className="text-center space-y-2">
            <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
              Engineered for Serious Job Seekers
            </h2>
            <p className="text-sm text-slate-400 max-w-xl mx-auto">
              Every tool you need to stand out from automated screening algorithms and land executive interviews.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Feature 1 */}
            <Card hover className="p-7 space-y-4 border-slate-800/80 bg-slate-900/60 flex flex-col justify-between">
              <div className="space-y-4">
                <div className="w-12 h-12 rounded-2xl bg-amber-500/10 text-amber-400 border border-amber-500/20 flex items-center justify-center">
                  <Brain className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-bold text-white">Deep JD Intelligence</h3>
                <p className="text-sm text-slate-400 leading-relaxed">
                  Our intelligence parser identifies core competencies, soft skills, hidden requirements, and gaps in your current profile before you apply.
                </p>
              </div>
              <div className="pt-2 border-t border-slate-800/60 flex items-center text-xs font-semibold text-amber-400">
                <span>Skill gap analysis & keyword extraction</span>
              </div>
            </Card>

            {/* Feature 2 */}
            <Card hover className="p-7 space-y-4 border-slate-800/80 bg-slate-900/60 flex flex-col justify-between">
              <div className="space-y-4">
                <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center justify-center">
                  <FileCheck className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-bold text-white">LaTeX Mathematical Precision</h3>
                <p className="text-sm text-slate-400 leading-relaxed">
                  Avoid sloppy word processors. Resumes are compiled with real LaTeX rendering engines to ensure 100% ATS readability and exact 1-page bounds.
                </p>
              </div>
              <div className="pt-2 border-t border-slate-800/60 flex items-center text-xs font-semibold text-emerald-400">
                <span>Overleaf-compatible source & PDF binaries</span>
              </div>
            </Card>

            {/* Feature 3 */}
            <Card hover className="p-7 space-y-4 border-slate-800/80 bg-slate-900/60 flex flex-col justify-between">
              <div className="space-y-4">
                <div className="w-12 h-12 rounded-2xl bg-sky-500/10 text-sky-400 border border-sky-500/20 flex items-center justify-center">
                  <Mail className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-bold text-white">Recruiter Cold Outreach</h3>
                <p className="text-sm text-slate-400 leading-relaxed">
                  Generate hyper-personalized cold outreach emails, LinkedIn connection requests, and follow-up notes grounded in your matched skills.
                </p>
              </div>
              <div className="pt-2 border-t border-slate-800/60 flex items-center text-xs font-semibold text-sky-400">
                <span>Multi-channel email & LinkedIn templates</span>
              </div>
            </Card>
          </div>
        </section>

        {/* Bottom CTA Banner */}
        <section className="relative overflow-hidden rounded-3xl border border-amber-500/30 bg-gradient-to-r from-amber-950/40 via-slate-900/90 to-slate-950/90 p-8 sm:p-14 text-center space-y-6 glow-amber">
          <div className="max-w-2xl mx-auto space-y-4">
            <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
              Ready to Upgrade Your Application Workflow?
            </h2>
            <p className="text-sm sm:text-base text-slate-300">
              Join candidates landing interviews at top tech companies with precision-engineered resumes and AI intelligence.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2">
            <Link href={user ? "/dashboard" : "/signup"} className="w-full sm:w-auto">
              <Button size="lg" className="w-full sm:w-auto text-base px-8 py-3.5">
                Get Started with PaperFox
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </Link>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-8 px-6 lg:px-12 text-center text-xs text-slate-500 bg-[#090d16]">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-2">
            <FoxLogo className="w-4 h-4" size={16} />
            <span>© {new Date().getFullYear()} PaperFox. All rights reserved.</span>
          </div>
          <p className="text-slate-400 font-medium">AI-Powered Job-Specific Resume Optimization</p>
        </div>
      </footer>
    </div>
  );
}
