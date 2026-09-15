"use client";

import React from "react";
import { ProjectEvidence } from "@/types/profile";
import {
  CheckCircle2,
  AlertTriangle,
  Clock,
  Layers,
  Code2,
  Cpu,
  Database,
  Cloud,
  ListChecks,
  Sliders,
  AlertCircle,
  Hash,
} from "lucide-react";

interface EvidencePanelProps {
  evidence?: ProjectEvidence;
  evidenceStatus?: "unverified" | "current" | "stale" | string;
  evidenceVersion?: number;
  evidenceUpdatedAt?: string;
  projectName?: string;
}

export const EvidencePanel: React.FC<EvidencePanelProps> = ({
  evidence,
  evidenceStatus = "unverified",
  evidenceVersion = 0,
  evidenceUpdatedAt,
  projectName = "Project",
}) => {
  if (!evidence) {
    return null;
  }

  const isCurrent = evidenceStatus === "current" || evidence.status === "current";
  const isStale = evidenceStatus === "stale" || evidence.status === "stale";

  const apisList = evidence.apis || evidence.APIs || [];
  const hasContent =
    (evidence.architecture && evidence.architecture.length > 0) ||
    (evidence.technologies && evidence.technologies.length > 0) ||
    (evidence.frameworks && evidence.frameworks.length > 0) ||
    (apisList.length > 0) ||
    (evidence.models && evidence.models.length > 0) ||
    (evidence.databases && evidence.databases.length > 0) ||
    (evidence.deployment && evidence.deployment.length > 0) ||
    (evidence.features && evidence.features.length > 0) ||
    (evidence.technical_details && evidence.technical_details.length > 0) ||
    (evidence.engineering_decisions && evidence.engineering_decisions.length > 0) ||
    (evidence.limitations && evidence.limitations.length > 0);

  if (!hasContent) {
    return null;
  }

  const formattedDate = evidenceUpdatedAt || evidence.verified_at
    ? new Date(evidenceUpdatedAt || evidence.verified_at || "").toLocaleDateString(undefined, {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      })
    : null;

  return (
    <div className="rounded-xl border border-emerald-500/20 bg-emerald-950/10 p-5 space-y-5 transition-all">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-emerald-500/20 pb-3">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-emerald-400" />
          <h4 className="text-xs font-bold text-emerald-300 uppercase tracking-wider">
            Structured Project Evidence
          </h4>
        </div>

        <div className="flex items-center gap-2 text-xs">
          {isCurrent ? (
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
              <CheckCircle2 className="w-3 h-3 text-emerald-400" /> Verified Current
            </span>
          ) : isStale ? (
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/40">
              <AlertTriangle className="w-3 h-3 text-amber-400" /> Stale Evidence
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-700 text-slate-300 border border-slate-600">
              <Clock className="w-3 h-3" /> Unverified
            </span>
          )}

          {evidenceVersion > 0 && (
            <span className="inline-flex items-center gap-0.5 px-2 py-0.5 rounded text-xs bg-slate-800 text-slate-400 font-mono">
              <Hash className="w-3 h-3" /> v{evidenceVersion}
            </span>
          )}

          {formattedDate && (
            <span className="text-slate-400 text-[11px] hidden sm:inline">
              Extracted: {formattedDate}
            </span>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
        {/* Architecture */}
        {evidence.architecture && evidence.architecture.length > 0 && (
          <div className="space-y-1.5 md:col-span-2 bg-slate-900/50 p-3 rounded-lg border border-slate-800">
            <span className="text-slate-400 font-medium flex items-center gap-1">
              <Layers className="w-3.5 h-3.5 text-indigo-400" /> System Architecture
            </span>
            <ul className="list-disc list-inside space-y-1 text-slate-200 pl-1">
              {evidence.architecture.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Technologies & Frameworks */}
        {((evidence.technologies && evidence.technologies.length > 0) ||
          (evidence.frameworks && evidence.frameworks.length > 0)) && (
          <div className="space-y-2 bg-slate-900/50 p-3 rounded-lg border border-slate-800">
            <span className="text-slate-400 font-medium flex items-center gap-1">
              <Code2 className="w-3.5 h-3.5 text-amber-400" /> Tech Stack & Frameworks
            </span>
            <div className="flex flex-wrap gap-1.5">
              {evidence.technologies?.map((tech, i) => (
                <span
                  key={`t-${i}`}
                  className="px-2 py-0.5 rounded bg-slate-800 text-slate-200 border border-slate-700 text-[11px] font-medium"
                >
                  {tech}
                </span>
              ))}
              {evidence.frameworks?.map((fw, i) => (
                <span
                  key={`f-${i}`}
                  className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/30 text-[11px] font-medium"
                >
                  {fw}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Databases & Models */}
        {((evidence.databases && evidence.databases.length > 0) ||
          (evidence.models && evidence.models.length > 0)) && (
          <div className="space-y-2 bg-slate-900/50 p-3 rounded-lg border border-slate-800">
            <span className="text-slate-400 font-medium flex items-center gap-1">
              <Database className="w-3.5 h-3.5 text-cyan-400" /> Storage & AI Models
            </span>
            <div className="flex flex-wrap gap-1.5">
              {evidence.databases?.map((db, i) => (
                <span
                  key={`db-${i}`}
                  className="px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 text-[11px] font-medium"
                >
                  {db}
                </span>
              ))}
              {evidence.models?.map((m, i) => (
                <span
                  key={`m-${i}`}
                  className="px-2 py-0.5 rounded bg-purple-500/10 text-purple-300 border border-purple-500/30 text-[11px] font-medium"
                >
                  {m}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* APIs & Endpoints */}
        {apisList.length > 0 && (
          <div className="space-y-2 bg-slate-900/50 p-3 rounded-lg border border-slate-800">
            <span className="text-slate-400 font-medium flex items-center gap-1">
              <Cpu className="w-3.5 h-3.5 text-blue-400" /> APIs & Protocols
            </span>
            <div className="flex flex-wrap gap-1.5">
              {apisList.map((apiItem, i) => (
                <span
                  key={`api-${i}`}
                  className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-300 border border-blue-500/30 text-[11px] font-mono"
                >
                  {apiItem}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Deployment & Infra */}
        {evidence.deployment && evidence.deployment.length > 0 && (
          <div className="space-y-2 bg-slate-900/50 p-3 rounded-lg border border-slate-800">
            <span className="text-slate-400 font-medium flex items-center gap-1">
              <Cloud className="w-3.5 h-3.5 text-teal-400" /> Deployment & Infrastructure
            </span>
            <div className="flex flex-wrap gap-1.5">
              {evidence.deployment.map((dep, i) => (
                <span
                  key={`dep-${i}`}
                  className="px-2 py-0.5 rounded bg-teal-500/10 text-teal-300 border border-teal-500/30 text-[11px] font-medium"
                >
                  {dep}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Features */}
        {evidence.features && evidence.features.length > 0 && (
          <div className="space-y-1.5 md:col-span-2 bg-slate-900/50 p-3 rounded-lg border border-slate-800">
            <span className="text-slate-400 font-medium flex items-center gap-1">
              <ListChecks className="w-3.5 h-3.5 text-emerald-400" /> Verified Features
            </span>
            <ul className="list-disc list-inside space-y-1 text-slate-200 pl-1">
              {evidence.features.map((feat, i) => (
                <li key={i}>{feat}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Engineering Decisions & Technical Details */}
        {((evidence.engineering_decisions && evidence.engineering_decisions.length > 0) ||
          (evidence.technical_details && evidence.technical_details.length > 0)) && (
          <div className="space-y-1.5 md:col-span-2 bg-slate-900/50 p-3 rounded-lg border border-slate-800">
            <span className="text-slate-400 font-medium flex items-center gap-1">
              <Sliders className="w-3.5 h-3.5 text-violet-400" /> Engineering Decisions & Implementation Details
            </span>
            <ul className="list-disc list-inside space-y-1 text-slate-200 pl-1">
              {evidence.engineering_decisions?.map((dec, i) => (
                <li key={`dec-${i}`}>{dec}</li>
              ))}
              {evidence.technical_details?.map((det, i) => (
                <li key={`det-${i}`}>{det}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Limitations & Missing/Unverified Items */}
        {evidence.limitations && evidence.limitations.length > 0 && (
          <div className="space-y-1.5 md:col-span-2 bg-amber-950/20 p-3 rounded-lg border border-amber-500/30">
            <span className="text-amber-300 font-medium flex items-center gap-1">
              <AlertCircle className="w-3.5 h-3.5 text-amber-400" /> Excluded / Unverified Items (ATS Grounding Guard)
            </span>
            <p className="text-[11px] text-slate-400">
              The following items were noted as unverified or missing in the codebase and will not be claimed in optimized resumes:
            </p>
            <ul className="list-disc list-inside space-y-1 text-amber-200/90 pl-1">
              {evidence.limitations.map((lim, i) => (
                <li key={`lim-${i}`}>{lim}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};
