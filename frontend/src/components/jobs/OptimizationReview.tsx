"use client";

import React from "react";
import { OptimizedResumeData } from "@/lib/jobs";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import {
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  FolderGit2,
  Briefcase,
  GraduationCap,
  Award,
  Cpu,
  ShieldCheck,
  Tag,
  Clock,
  Layers
} from "lucide-react";

interface OptimizationReviewProps {
  companyName: string;
  roleTitle: string;
  data: OptimizedResumeData;
}

export const OptimizationReview: React.FC<OptimizationReviewProps> = ({
  companyName,
  roleTitle,
  data
}) => {
  const meta = data.optimization_metadata;
  const alignment = data.keyword_alignment;

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="p-5 rounded-2xl bg-gradient-to-r from-amber-500/10 via-slate-900 to-indigo-500/10 border border-amber-500/30">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Badge variant="warning" className="bg-amber-500/20 text-amber-300 border-amber-500/40">
                <Sparkles className="w-3 h-3 mr-1" /> Job-Specific Optimization Snapshot
              </Badge>
              <Badge variant="neutral" className="border-slate-700 text-slate-400">
                <ShieldCheck className="w-3 h-3 mr-1 text-emerald-400" /> Master Profile Untouched
              </Badge>
            </div>
            <h2 className="text-xl font-bold text-white tracking-tight">
              {roleTitle} <span className="text-slate-400 font-normal">at</span> {companyName}
            </h2>
          </div>

          <div className="flex items-center gap-3 text-xs text-slate-400 bg-slate-950/60 p-3 rounded-xl border border-slate-800">
            <div className="flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5 text-amber-400" />
              <span>Provider: <strong className="text-slate-200">{meta?.provider || "Gemini"}</strong></span>
            </div>
            <span>•</span>
            <div className="flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-indigo-400" />
              <span>Generated: <strong className="text-slate-200">{new Date(meta?.generated_at || Date.now()).toLocaleTimeString()}</strong></span>
            </div>
          </div>
        </div>
      </div>

      {/* Professional Summary */}
      <Card className="p-6 space-y-3 border-slate-800 bg-slate-900/80">
        <h3 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-amber-400" /> Tailored Professional Summary
        </h3>
        <p className="text-sm text-slate-200 leading-relaxed bg-slate-950/50 p-4 rounded-xl border border-slate-800/80 font-normal">
          {data.summary}
        </p>
      </Card>

      {/* Keyword Alignment Widget */}
      <Card className="p-6 space-y-4 border-slate-800 bg-slate-900/80">
        <h3 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center gap-2">
          <Tag className="w-4 h-4 text-emerald-400" /> Factual Keyword Alignment
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Matched & Usable Keywords */}
          <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-800/30 space-y-2">
            <span className="text-xs font-semibold text-emerald-300 uppercase tracking-wider flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> Grounded Candidate Keywords ({alignment.matched_keywords.length})
            </span>
            <div className="flex flex-wrap gap-1.5">
              {alignment.matched_keywords.length === 0 ? (
                <span className="text-xs text-slate-500 italic">No direct matches found.</span>
              ) : (
                alignment.matched_keywords.map((kw, i) => (
                  <span key={i} className="px-2.5 py-1 rounded-md text-xs font-medium bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                    {kw}
                  </span>
                ))
              )}
            </div>
          </div>

          {/* Unsupported / Missing JD Keywords */}
          <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-800/30 space-y-2">
            <span className="text-xs font-semibold text-amber-300 uppercase tracking-wider flex items-center gap-1.5">
              <AlertTriangle className="w-3.5 h-3.5 text-amber-400" /> Excluded JD Keywords ({alignment.unsupported_jd_keywords.length})
            </span>
            <p className="text-[11px] text-slate-400">
              Keywords required by JD but not present in candidate profile. Strictly excluded to preserve factual grounding.
            </p>
            <div className="flex flex-wrap gap-1.5 pt-1">
              {alignment.unsupported_jd_keywords.length === 0 ? (
                <span className="text-xs text-slate-500 italic">100% of JD keywords grounded!</span>
              ) : (
                alignment.unsupported_jd_keywords.map((kw, i) => (
                  <span key={i} className="px-2.5 py-1 rounded-md text-xs font-medium bg-amber-500/10 text-amber-400/80 border border-amber-500/20 line-through opacity-75">
                    {kw}
                  </span>
                ))
              )}
            </div>
          </div>
        </div>
      </Card>

      {/* Prioritized Skills */}
      <Card className="p-6 space-y-4 border-slate-800 bg-slate-900/80">
        <h3 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center gap-2">
          <Layers className="w-4 h-4 text-indigo-400" /> Prioritized Skill Groups
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data.skills.map((grp, idx) => (
            <div key={idx} className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
              <span className="text-xs font-semibold text-indigo-300 uppercase tracking-wider">
                {grp.category}
              </span>
              <div className="flex flex-wrap gap-1.5">
                {grp.skills.map((sk, i) => (
                  <span key={i} className="px-2.5 py-1 rounded-md text-xs font-medium bg-slate-800 text-slate-200 border border-slate-700">
                    {sk}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Tailored Projects */}
      {data.projects.length > 0 && (
        <Card className="p-6 space-y-4 border-slate-800 bg-slate-900/80">
          <h3 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center gap-2">
            <FolderGit2 className="w-4 h-4 text-amber-400" /> Tailored Projects Repository ({data.projects.length})
          </h3>

          <div className="space-y-4">
            {data.projects.map((proj, idx) => (
              <div key={idx} className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="font-semibold text-white text-sm">{proj.project_name}</h4>
                  <Badge variant="warning" className="bg-amber-500/10 text-amber-300 border-amber-500/30">
                    Relevance Score: {Math.round(proj.relevance_score * 100)}%
                  </Badge>
                </div>

                {proj.technologies && proj.technologies.length > 0 && (
                  <div className="flex flex-wrap gap-1.5">
                    {proj.technologies.map((t, i) => (
                      <span key={i} className="px-2 py-0.5 rounded text-[11px] bg-slate-900 text-slate-300 border border-slate-800 font-mono">
                        {t}
                      </span>
                    ))}
                  </div>
                )}

                <ul className="space-y-1.5 pl-4 list-disc text-xs text-slate-300">
                  {proj.bullets.map((b, i) => (
                    <li key={i} className="leading-relaxed">{b}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Tailored Work Experience */}
      {data.experience.length > 0 && (
        <Card className="p-6 space-y-4 border-slate-800 bg-slate-900/80">
          <h3 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center gap-2">
            <Briefcase className="w-4 h-4 text-blue-400" /> Tailored Professional Experience
          </h3>

          <div className="space-y-4">
            {data.experience.map((exp, idx) => (
              <div key={idx} className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-semibold text-white text-sm">{exp.role}</h4>
                    <p className="text-xs text-amber-400 font-medium">{exp.company} {exp.location ? `• ${exp.location}` : ""}</p>
                  </div>
                  <span className="text-xs text-slate-400 font-mono">
                    {exp.start_date} - {exp.is_current ? "Present" : exp.end_date}
                  </span>
                </div>

                <ul className="space-y-1.5 pl-4 list-disc text-xs text-slate-300 pt-1">
                  {exp.bullets.map((b, i) => (
                    <li key={i} className="leading-relaxed">{b}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Tailored Internships */}
      {data.internships.length > 0 && (
        <Card className="p-6 space-y-4 border-slate-800 bg-slate-900/80">
          <h3 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center gap-2">
            <Briefcase className="w-4 h-4 text-teal-400" /> Tailored Internships
          </h3>

          <div className="space-y-4">
            {data.internships.map((intern, idx) => (
              <div key={idx} className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-semibold text-white text-sm">{intern.role}</h4>
                    <p className="text-xs text-teal-400 font-medium">{intern.company}</p>
                  </div>
                  <span className="text-xs text-slate-400 font-mono">
                    {intern.start_date} - {intern.is_current ? "Present" : intern.end_date}
                  </span>
                </div>

                <ul className="space-y-1.5 pl-4 list-disc text-xs text-slate-300 pt-1">
                  {intern.bullets.map((b, i) => (
                    <li key={i} className="leading-relaxed">{b}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Education & Certifications */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Education */}
        <Card className="p-6 space-y-3 border-slate-800 bg-slate-900/80">
          <h3 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center gap-2">
            <GraduationCap className="w-4 h-4 text-purple-400" /> Education (Factual)
          </h3>
          <div className="space-y-3">
            {data.education.map((edu, idx) => (
              <div key={idx} className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 text-xs space-y-1">
                <p className="font-semibold text-white">{edu.institution}</p>
                <p className="text-slate-300">{edu.degree} in {edu.field_of_study}</p>
              </div>
            ))}
          </div>
        </Card>

        {/* Certifications */}
        <Card className="p-6 space-y-3 border-slate-800 bg-slate-900/80">
          <h3 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center gap-2">
            <Award className="w-4 h-4 text-yellow-400" /> Certifications (Factual)
          </h3>
          <div className="space-y-3">
            {data.certifications.length === 0 ? (
              <p className="text-xs text-slate-500 italic">No certifications listed.</p>
            ) : (
              data.certifications.map((cert, idx) => (
                <div key={idx} className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 text-xs space-y-1">
                  <p className="font-semibold text-white">{cert.name}</p>
                  <p className="text-slate-400">{cert.issuer}</p>
                </div>
              ))
            )}
          </div>
        </Card>
      </div>
    </div>
  );
};
