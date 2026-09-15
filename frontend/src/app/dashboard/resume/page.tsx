"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { Navbar } from "@/components/dashboard/Navbar";
import { Sidebar } from "@/components/dashboard/Sidebar";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { api } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { CandidateProfile } from "@/types/profile";
import { ResumeArtifact, ResumeGenerateResponse } from "@/types/resume";
import {
  FileText,
  Sparkles,
  Download,
  RefreshCw,
  AlertCircle,
  CheckCircle2,
  AlertTriangle,
  Loader2,
  UserCheck,
  Code2,
} from "lucide-react";

export default function BaseResumePage() {
  const [profile, setProfile] = useState<CandidateProfile | null>(null);
  const [artifact, setArtifact] = useState<ResumeArtifact | null>(null);
  const [pdfBlobUrl, setPdfBlobUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  // Load candidate profile & base resume artifact on mount
  useEffect(() => {
    const loadData = async () => {
      try {
        const profRes = await api.get<CandidateProfile>("/profile");
        setProfile(profRes.data);
      } catch (err) {
        // Candidate profile not created yet
      }

      try {
        const artRes = await api.get<ResumeArtifact>("/resume/base");
        setArtifact(artRes.data);
        if (artRes.data.pdf_storage_reference) {
          await loadPdfBlob();
        }
      } catch (err) {
        // Base resume artifact not generated yet
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const loadPdfBlob = async () => {
    try {
      const response = await api.get("/resume/base/pdf", {
        responseType: "blob",
      });
      const blob = new Blob([response.data], { type: "application/pdf" });
      const url = URL.createObjectURL(blob);
      setPdfBlobUrl(url);
    } catch (err) {
      // PDF binary not compiled or unavailable
      setPdfBlobUrl(null);
    }
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    setError(null);
    setStatusMessage(null);

    try {
      const response = await api.post<ResumeGenerateResponse>("/resume/generate");
      setStatusMessage(response.data.message);
      if (response.data.artifact) {
        setArtifact(response.data.artifact);
      }

      if (response.data.pdf_storage_reference) {
        await loadPdfBlob();
      } else {
        setPdfBlobUrl(null);
      }
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "Failed to generate base resume.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownload = () => {
    if (!pdfBlobUrl) return;
    const a = document.createElement("a");
    a.href = pdfBlobUrl;
    a.download = "base_resume.pdf";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-slate-950 flex flex-col selection:bg-amber-500/30 selection:text-amber-200">
        <Navbar />

        <div className="flex-1 flex">
          <Sidebar />

          <main className="flex-1 p-6 md:p-10 max-w-6xl space-y-8">
            {/* Header Banner */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/60 border border-slate-800 p-6 rounded-xl">
              <div className="space-y-1">
                <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
                  <FileText className="w-6 h-6 text-amber-500" /> Base LaTeX Resume Engine
                </h1>
                <p className="text-xs text-slate-400">
                  Deterministic LaTeX compilation from your Master Candidate Profile into a 1-page PDF.
                </p>
              </div>

              <div className="flex items-center space-x-3">
                {artifact && (
                  <Badge
                    variant={
                      artifact.status === "success"
                        ? "success"
                        : artifact.status === "overflow"
                        ? "warning"
                        : "info"
                    }
                    className="px-3.5 py-1 text-xs"
                  >
                    {artifact.status === "success" && "1-Page Valid"}
                    {artifact.status === "overflow" && `${artifact.page_count} Pages (Overflow)`}
                    {artifact.status === "compiler_unavailable" && "Compiler Unavailable"}
                    {artifact.status === "error" && "Compilation Error"}
                  </Badge>
                )}

                <Button
                  type="button"
                  variant="primary"
                  size="md"
                  onClick={handleGenerate}
                  isLoading={isGenerating}
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  {artifact ? "Regenerate Base Resume" : "Generate Base Resume"}
                </Button>
              </div>
            </div>

            {/* Profile Readiness Warning */}
            {!profile && !loading && (
              <Card className="bg-amber-500/10 border-amber-500/30 p-5 flex items-center justify-between">
                <div className="flex items-center space-x-3 text-amber-400 text-xs">
                  <AlertTriangle className="w-5 h-5 shrink-0" />
                  <div>
                    <p className="font-semibold text-sm">Master Candidate Profile Missing</p>
                    <p className="text-amber-300/80">
                      Please complete your profile information before generating a base resume.
                    </p>
                  </div>
                </div>
                <Link href="/dashboard/profile">
                  <Button variant="primary" size="sm">
                    Complete Profile
                  </Button>
                </Link>
              </Card>
            )}

            {/* Status Messages */}
            {error && (
              <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl flex items-start space-x-3 text-xs text-red-400">
                <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}

            {statusMessage && (
              <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl flex items-start space-x-3 text-xs text-slate-200">
                <CheckCircle2 className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
                <span>{statusMessage}</span>
              </div>
            )}

            {/* Main Content Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Left Column: Artifact Metadata & Compiler Status */}
              <div className="space-y-6">
                <Card className="p-6 space-y-4 border-slate-800 bg-slate-900/60">
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider border-b border-slate-800 pb-2">
                    Engine Artifact Details
                  </h3>

                  {artifact ? (
                    <div className="space-y-3 text-xs">
                      <div>
                        <span className="text-slate-500 block uppercase">Target Type</span>
                        <span className="text-slate-200 font-mono font-semibold uppercase">{artifact.type} Resume</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block uppercase">Detected Page Count</span>
                        <span className="text-amber-400 font-mono font-bold text-sm">{artifact.page_count} Page(s)</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block uppercase">Status</span>
                        <span className="text-slate-200 font-semibold">{artifact.status}</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block uppercase">Last Compiled</span>
                        <span className="text-slate-400 font-mono">
                          {new Date(artifact.updated_at).toLocaleString()}
                        </span>
                      </div>
                      {artifact.pdf_storage_reference && (
                        <div>
                          <span className="text-slate-500 block uppercase">Storage Reference</span>
                          <span className="text-slate-400 font-mono text-[11px] break-all">
                            {artifact.pdf_storage_reference}
                          </span>
                        </div>
                      )}
                    </div>
                  ) : (
                    <p className="text-xs text-slate-500 italic">
                      No base resume compiled yet. Click "Generate Base Resume" to start the LaTeX compilation engine.
                    </p>
                  )}

                  {pdfBlobUrl && (
                    <Button
                      type="button"
                      variant="secondary"
                      size="sm"
                      onClick={handleDownload}
                      className="w-full mt-4"
                    >
                      <Download className="w-4 h-4 mr-2" /> Download PDF
                    </Button>
                  )}
                </Card>

                {/* Compiler System Info */}
                <Card className="p-6 space-y-3 border-slate-800 bg-slate-900/40 text-xs">
                  <h4 className="font-semibold text-slate-200 flex items-center gap-1.5">
                    <Code2 className="w-4 h-4 text-amber-500" /> Server TeX Requirement
                  </h4>
                  <p className="text-slate-400 leading-relaxed">
                    Binary PDF compilation requires local <code className="text-amber-400">pdflatex</code> or <code className="text-amber-400">xelatex</code> installed on the server host environment (e.g., TeX Live or MiKTeX).
                  </p>
                </Card>
              </div>

              {/* Right Column: PDF Preview / Viewer */}
              <div className="lg:col-span-2">
                <Card className="p-4 border-slate-800 bg-slate-900/80 min-h-[600px] flex flex-col justify-between">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
                    <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                      <FileText className="w-4 h-4 text-amber-500" /> PDF Preview Stream
                    </span>
                    {pdfBlobUrl && (
                      <span className="text-xs font-mono text-emerald-400">PDF Binary Active</span>
                    )}
                  </div>

                  {pdfBlobUrl ? (
                    <iframe
                      src={pdfBlobUrl}
                      className="w-full h-[650px] rounded-lg border border-slate-800 bg-slate-950"
                      title="Base Resume PDF Preview"
                    />
                  ) : (
                    <div className="flex-1 flex flex-col items-center justify-center p-12 text-center space-y-4 border-2 border-dashed border-slate-800 rounded-lg">
                      <FileText className="w-12 h-12 text-slate-700" />
                      <div>
                        <h4 className="text-sm font-semibold text-slate-300">No PDF Preview Available</h4>
                        <p className="text-xs text-slate-500 mt-1 max-w-sm">
                          {artifact?.status === "compiler_unavailable"
                            ? "Server TeX compiler is not installed. Install pdflatex on the host system to view binary PDFs."
                            : "Click 'Generate Base Resume' above to run the LaTeX engine."}
                        </p>
                      </div>
                    </div>
                  )}
                </Card>
              </div>
            </div>
          </main>
        </div>
      </div>
    </ProtectedRoute>
  );
}
