"use client";

import { useState } from "react";
import {
  ATSValidation,
  JobApplication,
  JobResumeArtifact,
  JobResumeRenderResponse,
  renderJobResumeApi,
} from "@/lib/jobs";

interface JobResumePanelProps {
  job: JobApplication;
  /** Called after a successful render so the parent can refresh job state */
  onRenderComplete?: (updatedJob: JobApplication) => void;
}

// ── Helper sub-components ─────────────────────────────────────────────────────

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, { label: string; cls: string }> = {
    success: {
      label: "✓ Generated — 1 Page",
      cls: "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30",
    },
    overflow: {
      label: "⚠ Generated — Overflow",
      cls: "bg-amber-500/15 text-amber-400 border border-amber-500/30",
    },
    compiler_unavailable: {
      label: "⚙ LaTeX Source Ready",
      cls: "bg-blue-500/15 text-blue-400 border border-blue-500/30",
    },
    error: {
      label: "✕ Generation Failed",
      cls: "bg-red-500/15 text-red-400 border border-red-500/30",
    },
  };

  const { label, cls } = map[status] ?? {
    label: status,
    cls: "bg-zinc-700/40 text-zinc-400 border border-zinc-600",
  };

  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold ${cls}`}>
      {label}
    </span>
  );
}

function ATSCard({ ats }: { ats: ATSValidation }) {
  const checks: { label: string; value: boolean }[] = [
    { label: "Single Page", value: ats.is_single_page },
    { label: "Text Extractable", value: ats.text_extractable },
    { label: "Has Summary", value: ats.has_summary },
    { label: "Has Skills", value: ats.has_skills },
    { label: "Has Education", value: ats.has_education },
    { label: "Has Experience / Projects", value: ats.has_experience_or_projects },
  ];

  const passed = checks.filter((c) => c.value).length;
  const total = checks.length;

  return (
    <div className="rounded-xl border border-white/8 bg-white/3 p-4">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-sm font-semibold text-white/80">ATS Readiness</h4>
        <span
          className={`text-xs font-bold px-2 py-0.5 rounded-full ${
            passed === total
              ? "bg-emerald-500/20 text-emerald-400"
              : passed >= 4
              ? "bg-amber-500/20 text-amber-400"
              : "bg-red-500/20 text-red-400"
          }`}
        >
          {passed}/{total} checks
        </span>
      </div>
      <div className="grid grid-cols-2 gap-2">
        {checks.map((c) => (
          <div
            key={c.label}
            className="flex items-center gap-2 text-xs"
          >
            <span
              className={`w-4 h-4 rounded-full flex items-center justify-center text-[10px] font-bold flex-shrink-0 ${
                c.value
                  ? "bg-emerald-500/20 text-emerald-400"
                  : "bg-red-500/20 text-red-400"
              }`}
            >
              {c.value ? "✓" : "✕"}
            </span>
            <span className={c.value ? "text-white/70" : "text-white/40"}>
              {c.label}
            </span>
          </div>
        ))}
      </div>
      {ats.page_count > 0 && (
        <p className="mt-2 text-xs text-white/40">
          Page count: {ats.page_count}
        </p>
      )}
    </div>
  );
}

function CompressionNote({ level }: { level: number }) {
  if (level === 0)
    return (
      <p className="text-xs text-white/40">
        No compression applied — content fit within one page natively.
      </p>
    );
  const descriptions = [
    "", // 0
    "Slightly tighter margins and section spacing.",
    "Tight margins + project bullets capped at 3.",
    "Capped all experience and internship bullets at 3.",
    "Limited to top 3 most relevant projects.",
    "Maximum compression: top 2 projects, certifications removed.",
  ];
  return (
    <p className="text-xs text-amber-400/80">
      Compression level {level} applied: {descriptions[level]}
    </p>
  );
}

// ── Main panel component ──────────────────────────────────────────────────────

export default function JobResumePanel({ job, onRenderComplete }: JobResumePanelProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<JobResumeRenderResponse | null>(null);

  // Pull existing artifact from job data if already generated
  const existingArtifact: JobResumeArtifact | undefined = job.job_resume_artifact;
  const artifact: JobResumeArtifact | undefined =
    result
      ? ({
          ...result.artifact,
          status: result.status,
          page_count: result.page_count,
          compression_level_used: result.compression_level_used,
          ats_validation: result.ats_validation,
          pdf_storage_reference: result.pdf_storage_reference,
          error_message: result.artifact?.error_message,
          generated_at: result.artifact?.generated_at,
          latex_source: result.artifact?.latex_source ?? "",
        } as JobResumeArtifact)
      : existingArtifact;

  const canGenerate = job.is_optimized;
  const hasDownload =
    artifact?.status === "success" || artifact?.status === "overflow";

  async function handleGenerate() {
    setLoading(true);
    setError(null);
    try {
      const res = await renderJobResumeApi(job.id);
      setResult(res);
      if (onRenderComplete) {
        // Optimistically merge artifact into the job object for parent
        onRenderComplete({
          ...job,
          is_resume_generated: true,
          job_resume_artifact: {
            latex_source: res.artifact?.latex_source ?? "",
            pdf_storage_reference: res.pdf_storage_reference,
            page_count: res.page_count,
            compression_level_used: res.compression_level_used,
            status: res.status,
            ats_validation: res.ats_validation,
            error_message: res.artifact?.error_message,
            generated_at: res.artifact?.generated_at ?? new Date().toISOString(),
          },
        });
      }
    } catch (err: any) {
      const detail =
        err?.response?.data?.detail ||
        err?.message ||
        "Resume generation failed.";
      setError(detail);
    } finally {
      setLoading(false);
    }
  }

  function handleDownload() {
    // Authenticated download — include token via a direct link
    // The download endpoint requires auth; use the api client approach
    import("@/lib/api").then(({ api }) => {
      api
        .get(`/jobs/${job.id}/resume/download`, { responseType: "blob" })
        .then((res) => {
          const blob = new Blob([res.data], { type: "application/pdf" });
          const url = URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = `resume_${job.company_name.replace(/\s+/g, "_")}_${job.role_title.replace(/\s+/g, "_")}.pdf`;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          URL.revokeObjectURL(url);
        })
        .catch(() => {
          setError("PDF download failed. The file may not be available.");
        });
    });
  }

  return (
    <div className="mt-4 rounded-2xl border border-white/10 bg-white/4 backdrop-blur-sm overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-white/8">
        <div>
          <h3 className="text-sm font-semibold text-white flex items-center gap-2">
            <span className="text-base">📄</span>
            Job-Specific Resume
          </h3>
          <p className="text-xs text-white/40 mt-0.5">
            Deterministic PDF generation · ATS-optimised · One-page target
          </p>
        </div>
        <div className="flex items-center gap-3">
          {artifact && <StatusBadge status={artifact.status} />}
          {!canGenerate && (
            <span className="text-xs text-white/30 italic">
              Run optimization first
            </span>
          )}
        </div>
      </div>

      {/* Body */}
      <div className="px-5 py-4 space-y-4">
        {/* Not yet optimized warning */}
        {!canGenerate && (
          <div className="rounded-xl border border-amber-500/25 bg-amber-500/8 p-4 text-sm text-amber-300">
            <p className="font-medium mb-1">Phase 5 Optimization Required</p>
            <p className="text-xs text-amber-300/70">
              Run &quot;Optimize Resume&quot; above to generate the job-specific
              optimization snapshot. Resume generation requires a completed
              optimization.
            </p>
          </div>
        )}

        {/* Compiler unavailable notice */}
        {artifact?.status === "compiler_unavailable" && (
          <div className="rounded-xl border border-blue-500/25 bg-blue-500/8 p-4">
            <p className="text-sm font-medium text-blue-300 mb-1">
              LaTeX Source Ready
            </p>
            <p className="text-xs text-blue-300/70 leading-relaxed">
              The resume LaTeX source was generated successfully. PDF compilation
              requires <strong>pdflatex</strong> or <strong>xelatex</strong> to
              be installed on the server. Your LaTeX source is stored and can be
              compiled locally.
            </p>
          </div>
        )}

        {/* Overflow warning */}
        {artifact?.status === "overflow" && (
          <div className="rounded-xl border border-amber-500/25 bg-amber-500/8 p-4">
            <p className="text-sm font-medium text-amber-300 mb-1">
              Resume Overflow — Maximum Compression Applied
            </p>
            <p className="text-xs text-amber-300/70 leading-relaxed">
              {artifact.error_message ||
                "The resume exceeds one page even after maximum compression. Consider reducing the number of projects or experience bullets in your profile."}
            </p>
          </div>
        )}

        {/* Error notice */}
        {(error || artifact?.status === "error") && (
          <div className="rounded-xl border border-red-500/25 bg-red-500/8 p-4">
            <p className="text-sm font-medium text-red-400 mb-1">
              Generation Error
            </p>
            <p className="text-xs text-red-400/70 leading-relaxed">
              {error || artifact?.error_message || "An unknown error occurred."}
            </p>
          </div>
        )}

        {/* Artifact details */}
        {artifact && artifact.status !== "error" && (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {/* ATS validation card */}
            <ATSCard ats={artifact.ats_validation} />

            {/* Metadata card */}
            <div className="rounded-xl border border-white/8 bg-white/3 p-4 space-y-3">
              <h4 className="text-sm font-semibold text-white/80">
                Generation Details
              </h4>
              <div className="space-y-1.5">
                <div className="flex justify-between text-xs">
                  <span className="text-white/50">Status</span>
                  <span className="text-white/80 capitalize font-medium">
                    {artifact.status.replace(/_/g, " ")}
                  </span>
                </div>
                {artifact.page_count > 0 && (
                  <div className="flex justify-between text-xs">
                    <span className="text-white/50">Pages</span>
                    <span
                      className={`font-medium ${
                        artifact.page_count === 1
                          ? "text-emerald-400"
                          : "text-amber-400"
                      }`}
                    >
                      {artifact.page_count}
                    </span>
                  </div>
                )}
                <div className="flex justify-between text-xs">
                  <span className="text-white/50">Compression</span>
                  <span className="text-white/80 font-medium">
                    Level {artifact.compression_level_used}
                    {artifact.compression_level_used === 0 ? " (none)" : ""}
                  </span>
                </div>
                {artifact.generated_at && (
                  <div className="flex justify-between text-xs">
                    <span className="text-white/50">Generated</span>
                    <span className="text-white/60">
                      {new Date(artifact.generated_at).toLocaleString()}
                    </span>
                  </div>
                )}
              </div>
              <CompressionNote level={artifact.compression_level_used} />
            </div>
          </div>
        )}

        {/* Action buttons */}
        <div className="flex items-center gap-3 pt-1">
          {canGenerate && (
            <button
              id={`btn-generate-resume-${job.id}`}
              onClick={handleGenerate}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold bg-indigo-600 hover:bg-indigo-500 text-white disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/30"
            >
              {loading ? (
                <>
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Generating…
                </>
              ) : artifact ? (
                <>
                  <span>🔄</span>
                  Re-generate Resume
                </>
              ) : (
                <>
                  <span>⚡</span>
                  Generate Resume
                </>
              )}
            </button>
          )}

          {hasDownload && (
            <button
              id={`btn-download-resume-${job.id}`}
              onClick={handleDownload}
              className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold border border-emerald-500/40 bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 transition-all duration-200"
            >
              <span>⬇</span>
              Download PDF
            </button>
          )}
        </div>

        {/* Disclaimer */}
        <p className="text-[10px] text-white/25 leading-relaxed">
          Resume content is derived exclusively from your Master Candidate
          Profile and the Phase 5 optimization snapshot. Layout and formatting
          are determined by PaperFox&apos;s ATS-optimised LaTeX renderer — no AI
          is involved in the PDF generation step.
        </p>
      </div>
    </div>
  );
}
