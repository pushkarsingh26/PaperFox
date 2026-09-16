"use client";

import React, { useEffect, useState, useMemo } from "react";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { Navbar } from "@/components/dashboard/Navbar";
import { Sidebar } from "@/components/dashboard/Sidebar";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import {
  listJobsApi,
  analyzeJobApi,
  generateMailingDraftApi,
  updateMailingDraftApi,
  JobApplication,
  MailingDraft,
} from "@/lib/jobs";
import {
  Mail,
  Send,
  Sparkles,
  Copy,
  Check,
  RefreshCw,
  AlertCircle,
  Briefcase,
  User,
  Building2,
  MapPin,
  ListCheck,
  Code,
  FileText,
  Save,
  CheckCircle2,
  ExternalLink,
  Layers,
  ChevronDown,
} from "lucide-react";

export default function MailingSystemPage() {
  const [jobs, setJobs] = useState<JobApplication[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<string>("");
  const [selectedJob, setSelectedJob] = useState<JobApplication | null>(null);
  const [loadingJobs, setLoadingJobs] = useState<boolean>(true);
  const [analyzingJob, setAnalyzingJob] = useState<boolean>(false);

  // Email draft states
  const [draft, setDraft] = useState<MailingDraft | null>(null);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [copied, setCopied] = useState<boolean>(false);
  const [saveSuccess, setSaveSuccess] = useState<boolean>(false);
  const [activeVersion, setActiveVersion] = useState<"standard" | "short">("standard");

  // Editable recipient and email fields
  const [recipientName, setRecipientName] = useState<string>("");
  const [recipientEmail, setRecipientEmail] = useState<string>("");
  const [recipientRole, setRecipientRole] = useState<string>("");
  const [subject, setSubject] = useState<string>("");
  const [body, setBody] = useState<string>("");
  const [shortBody, setShortBody] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  // Fetch all jobs on load
  const fetchJobs = async () => {
    setLoadingJobs(true);
    setError(null);
    try {
      const items = await listJobsApi();
      setJobs(items);
      if (items && items.length > 0) {
        // Default to first job if none selected
        if (!selectedJobId) {
          const first = items[0];
          setSelectedJobId(first.id);
          setSelectedJob(first);
          loadDraftFromJob(first);
        } else {
          const current = items.find((j) => j.id === selectedJobId) || items[0];
          setSelectedJobId(current.id);
          setSelectedJob(current);
          loadDraftFromJob(current);
        }
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to load job applications.");
    } finally {
      setLoadingJobs(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  const loadDraftFromJob = (job: JobApplication) => {
    if (job.mailing_draft) {
      const md = job.mailing_draft;
      setDraft(md);
      setRecipientName(md.recipient_name || "");
      setRecipientEmail(md.recipient_email || "");
      setRecipientRole(md.recipient_role || "");
      setSubject(md.subject || "");
      setBody(md.body || "");
      setShortBody(md.short_body || "");
    } else {
      setDraft(null);
      setRecipientName("");
      setRecipientEmail("");
      setRecipientRole("");
      setSubject("");
      setBody("");
      setShortBody("");
    }
  };

  const handleSelectJob = (jobId: string) => {
    setSelectedJobId(jobId);
    const found = jobs.find((j) => j.id === jobId);
    if (found) {
      setSelectedJob(found);
      loadDraftFromJob(found);
      setError(null);
    }
  };

  const handleRunAnalysis = async () => {
    if (!selectedJob) return;
    setAnalyzingJob(true);
    setError(null);
    try {
      const updated = await analyzeJobApi(selectedJob.id);
      setSelectedJob(updated);
      setJobs((prev) => prev.map((j) => (j.id === updated.id ? updated : j)));
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to analyze job description.");
    } finally {
      setAnalyzingJob(false);
    }
  };

  const handleGenerate = async () => {
    if (!selectedJob) return;
    setIsGenerating(true);
    setError(null);
    try {
      const generated = await generateMailingDraftApi(selectedJob.id, {
        recipient_name: recipientName.trim() || undefined,
        recipient_email: recipientEmail.trim() || undefined,
        recipient_role: recipientRole.trim() || undefined,
      });
      setDraft(generated);
      setSubject(generated.subject);
      setBody(generated.body);
      setShortBody(generated.short_body || "");
      // Update in local job state
      const updatedJob = { ...selectedJob, mailing_draft: generated };
      setSelectedJob(updatedJob);
      setJobs((prev) => prev.map((j) => (j.id === updatedJob.id ? updatedJob : j)));
    } catch (err: any) {
      setError(err?.response?.data?.detail || "AI email generation failed.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSave = async () => {
    if (!selectedJob) return;
    setIsSaving(true);
    setError(null);
    try {
      const updated = await updateMailingDraftApi(selectedJob.id, {
        recipient_name: recipientName.trim() || undefined,
        recipient_email: recipientEmail.trim() || undefined,
        recipient_role: recipientRole.trim() || undefined,
        subject: subject.trim(),
        body: body.trim(),
        short_body: shortBody.trim() || undefined,
        status: "ready",
      });
      setDraft(updated);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 2500);

      const updatedJob = { ...selectedJob, mailing_draft: updated };
      setSelectedJob(updatedJob);
      setJobs((prev) => prev.map((j) => (j.id === updatedJob.id ? updatedJob : j)));
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to save draft edits.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleCopy = async () => {
    const activeText = activeVersion === "standard" ? body : shortBody || body;
    const fullClipboardText = `Subject: ${subject}\n\n${activeText}`;
    try {
      await navigator.clipboard.writeText(fullClipboardText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      alert("Failed to copy to clipboard.");
    }
  };

  const activeContent = activeVersion === "standard" ? body : shortBody;
  const wordCount = useMemo(() => {
    const text = activeContent.trim();
    return text ? text.split(/\s+/).length : 0;
  }, [activeContent]);

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-slate-950 flex flex-col text-slate-100 selection:bg-amber-500/30 selection:text-amber-200">
        <Navbar />

        <div className="flex-1 flex">
          <Sidebar />

          <main className="flex-1 w-full max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-6 md:py-8 space-y-6">
            {/* Page Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
              <div className="space-y-1">
                <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
                  <Mail className="w-6 h-6 text-amber-400" />
                  Mailing System
                </h1>
                <p className="text-sm text-slate-400">
                  Targeted, evidence-grounded cold outreach emails for hiring managers and recruiting teams.
                </p>
              </div>

              {/* Job Switcher Dropdown */}
              {jobs.length > 0 && (
                <div className="flex items-center gap-3">
                  <label className="text-xs text-slate-400 font-medium whitespace-nowrap">
                    Target Job:
                  </label>
                  <div className="relative min-w-[260px]">
                    <select
                      value={selectedJobId}
                      onChange={(e) => handleSelectJob(e.target.value)}
                      className="w-full appearance-none bg-slate-900 border border-slate-800 rounded-xl px-3.5 py-2 pr-8 text-xs font-medium text-white focus:outline-none focus:border-amber-500/60 focus:ring-1 focus:ring-amber-500/30 transition-all cursor-pointer"
                    >
                      {jobs.map((job) => (
                        <option key={job.id} value={job.id}>
                          {job.company_name} — {job.role_title}
                        </option>
                      ))}
                    </select>
                    <ChevronDown className="w-4 h-4 text-slate-400 absolute right-2.5 top-2.5 pointer-events-none" />
                  </div>
                </div>
              )}
            </div>

            {/* Error Banner */}
            {error && (
              <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/60 text-rose-300 text-xs flex items-center gap-3">
                <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
                <span className="flex-1">{error}</span>
                <button
                  type="button"
                  onClick={() => setError(null)}
                  className="text-rose-400 hover:text-rose-200"
                >
                  &times;
                </button>
              </div>
            )}

            {/* Main Content Workspace */}
            {loadingJobs ? (
              <div className="p-16 rounded-2xl bg-slate-900/30 border border-slate-800/80 text-center space-y-3">
                <RefreshCw className="w-6 h-6 text-amber-400 animate-spin mx-auto" />
                <p className="text-xs text-slate-400">Loading jobs and outreach workspaces...</p>
              </div>
            ) : !selectedJob ? (
              <div className="p-16 rounded-2xl bg-slate-900/30 border border-slate-800/80 text-center space-y-4">
                <Briefcase className="w-10 h-10 text-slate-600 mx-auto" />
                <div>
                  <h3 className="text-base font-semibold text-white">No Job Application Selected</h3>
                  <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
                    Create or select a job in the Job Workspace to generate personalized outreach emails.
                  </p>
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
                {/* ── Left Column: Job Context & JD Intelligence (5 cols) ── */}
                <div className="lg:col-span-5 space-y-4">
                  {/* Job Overview Card */}
                  <div className="p-5 rounded-2xl bg-slate-900/50 border border-slate-800/80 space-y-4">
                    <div className="flex items-start justify-between gap-3">
                      <div className="space-y-0.5">
                        <div className="flex items-center gap-2">
                          <Building2 className="w-4 h-4 text-amber-400 shrink-0" />
                          <span className="text-sm font-bold text-white">
                            {selectedJob.company_name}
                          </span>
                        </div>
                        <p className="text-xs text-slate-300 font-medium pl-6">
                          {selectedJob.role_title}
                        </p>
                      </div>

                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-semibold border uppercase tracking-wider bg-slate-800 text-slate-300 border-slate-700">
                        {selectedJob.application_status || "draft"}
                      </span>
                    </div>

                    {selectedJob.location && (
                      <p className="text-xs text-slate-400 flex items-center gap-1.5">
                        <MapPin className="w-3.5 h-3.5 text-slate-500" />
                        {selectedJob.location}
                      </p>
                    )}

                    {/* Unanalyzed Warning */}
                    {!selectedJob.is_analyzed && (
                      <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/25 text-amber-300 space-y-2.5">
                        <div className="flex items-center gap-2">
                          <Sparkles className="w-4 h-4 text-amber-400 shrink-0" />
                          <h4 className="text-xs font-bold uppercase tracking-wider">
                            JD Intelligence Required
                          </h4>
                        </div>
                        <p className="text-xs text-amber-300/80 leading-relaxed">
                          Analyze this job description first so PaperFox can extract verified skill alignment and role requirements.
                        </p>
                        <Button
                          size="sm"
                          disabled={analyzingJob}
                          onClick={handleRunAnalysis}
                          className="w-full text-xs bg-amber-500 hover:bg-amber-400 text-slate-950 font-semibold h-8 shadow"
                        >
                          {analyzingJob ? (
                            <>
                              <RefreshCw className="w-3.5 h-3.5 animate-spin mr-1.5" />
                              Analyzing JD...
                            </>
                          ) : (
                            <>
                              <Sparkles className="w-3.5 h-3.5 mr-1.5" />
                              Extract Intelligence
                            </>
                          )}
                        </Button>
                      </div>
                    )}

                    {/* Analyzed Intelligence Summary */}
                    {selectedJob.is_analyzed && selectedJob.requirements && (
                      <div className="space-y-3.5 pt-2 border-t border-slate-800/80">
                        <div>
                          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block mb-1.5 flex items-center gap-1.5">
                            <ListCheck className="w-3.5 h-3.5 text-amber-400" />
                            Target Required Skills
                          </span>
                          <div className="flex flex-wrap gap-1.5">
                            {(selectedJob.requirements.required_skills || []).slice(0, 8).map((sk, idx) => (
                              <span
                                key={idx}
                                className="px-2 py-0.5 rounded text-[11px] font-medium bg-slate-800/90 text-slate-200 border border-slate-700/80"
                              >
                                {sk}
                              </span>
                            ))}
                          </div>
                        </div>

                        {selectedJob.requirements.responsibilities && selectedJob.requirements.responsibilities.length > 0 && (
                          <div>
                            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block mb-1.5">
                              Key Responsibilities
                            </span>
                            <ul className="space-y-1 text-xs text-slate-300/90 list-disc list-inside">
                              {selectedJob.requirements.responsibilities.slice(0, 3).map((resp, idx) => (
                                <li key={idx} className="line-clamp-2">
                                  {resp}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {/* Confirmed Skills for Job */}
                        {selectedJob.approved_additional_skills && selectedJob.approved_additional_skills.length > 0 && (
                          <div>
                            <span className="text-[11px] font-semibold uppercase tracking-wider text-emerald-400 block mb-1.5 flex items-center gap-1.5">
                              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                              Confirmed Profile Skills
                            </span>
                            <div className="flex flex-wrap gap-1.5">
                              {selectedJob.approved_additional_skills.map((sk, idx) => (
                                <span
                                  key={idx}
                                  className="px-2 py-0.5 rounded text-[11px] font-medium bg-emerald-500/10 text-emerald-300 border border-emerald-500/20"
                                >
                                  {sk}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Selected Evidence Banner */}
                  {draft?.selected_evidence && draft.selected_evidence.length > 0 && (
                    <div className="p-4 rounded-2xl bg-slate-900/40 border border-slate-800/80 space-y-2">
                      <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                        <Code className="w-3.5 h-3.5 text-amber-400" />
                        Verified Candidate Evidence Cited
                      </span>
                      <div className="space-y-1.5">
                        {draft.selected_evidence.map((ev, idx) => (
                          <div
                            key={idx}
                            className="p-2 rounded-lg bg-slate-950/60 border border-slate-800/80 text-xs text-slate-300 font-mono"
                          >
                            • {ev}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* ── Right Column: Email Workspace (7 cols) ── */}
                <div className="lg:col-span-7 space-y-4">
                  <div className="p-5 sm:p-6 rounded-2xl bg-slate-900/60 border border-slate-800/90 shadow-xl space-y-5">
                    {/* Workspace Header */}
                    <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-slate-800/80">
                      <div>
                        <h3 className="text-base font-bold text-white flex items-center gap-2">
                          <Send className="w-4 h-4 text-amber-400" />
                          Outreach Workspace
                        </h3>
                        <p className="text-xs text-slate-400 mt-0.5">
                          Personalized email grounded in your verified projects.
                        </p>
                      </div>

                      <div className="flex items-center gap-2">
                        <Button
                          size="sm"
                          disabled={!selectedJob.is_analyzed || isGenerating}
                          onClick={handleGenerate}
                          className="text-xs h-8 px-3 bg-amber-500 hover:bg-amber-400 text-slate-950 font-semibold shadow flex items-center gap-1.5"
                        >
                          {isGenerating ? (
                            <>
                              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                              Generating...
                            </>
                          ) : (
                            <>
                              <Sparkles className="w-3.5 h-3.5" />
                              {draft ? "Regenerate Email" : "Generate Outreach"}
                            </>
                          )}
                        </Button>
                      </div>
                    </div>

                    {/* Recipient Information Form */}
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                      <div>
                        <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                          Recipient Name
                        </label>
                        <input
                          type="text"
                          value={recipientName}
                          onChange={(e) => setRecipientName(e.target.value)}
                          placeholder="e.g. Alex (or leave blank)"
                          className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white placeholder:text-slate-600 focus:outline-none focus:border-amber-500/60 transition-all"
                        />
                      </div>
                      <div>
                        <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                          Recipient Email
                        </label>
                        <input
                          type="email"
                          value={recipientEmail}
                          onChange={(e) => setRecipientEmail(e.target.value)}
                          placeholder="e.g. alex@company.com"
                          className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white placeholder:text-slate-600 focus:outline-none focus:border-amber-500/60 transition-all"
                        />
                      </div>
                      <div>
                        <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                          Role / Title
                        </label>
                        <input
                          type="text"
                          value={recipientRole}
                          onChange={(e) => setRecipientRole(e.target.value)}
                          placeholder="e.g. Engineering Manager"
                          className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white placeholder:text-slate-600 focus:outline-none focus:border-amber-500/60 transition-all"
                        />
                      </div>
                    </div>

                    {/* Subject Line & AI Options */}
                    <div className="space-y-2">
                      <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
                        Subject Line
                      </label>
                      <input
                        type="text"
                        value={subject}
                        onChange={(e) => setSubject(e.target.value)}
                        placeholder="Click Generate to produce role-specific subjects"
                        className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs font-semibold text-white placeholder:text-slate-600 focus:outline-none focus:border-amber-500/60 transition-all"
                      />

                      {/* Subject Option Chips */}
                      {draft?.subject_options && draft.subject_options.length > 0 && (
                        <div className="flex flex-wrap items-center gap-1.5 pt-1">
                          <span className="text-[10px] text-slate-500 uppercase font-semibold">
                            Options:
                          </span>
                          {draft.subject_options.map((opt, idx) => (
                            <button
                              key={idx}
                              type="button"
                              onClick={() => setSubject(opt)}
                              className={`text-[11px] px-2.5 py-1 rounded-lg border transition-all ${
                                subject === opt
                                  ? "bg-amber-500/20 border-amber-500/40 text-amber-300 font-medium"
                                  : "bg-slate-950/60 border-slate-800 hover:border-slate-700 text-slate-400 hover:text-slate-200"
                              }`}
                            >
                              {opt}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Version Switcher */}
                    <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          onClick={() => setActiveVersion("standard")}
                          className={`text-xs font-semibold px-3 py-1.5 rounded-lg transition-all ${
                            activeVersion === "standard"
                              ? "bg-slate-800 text-amber-400 border border-slate-700"
                              : "text-slate-400 hover:text-white"
                          }`}
                        >
                          Standard Email
                        </button>
                        <button
                          type="button"
                          onClick={() => setActiveVersion("short")}
                          className={`text-xs font-semibold px-3 py-1.5 rounded-lg transition-all ${
                            activeVersion === "short"
                              ? "bg-slate-800 text-amber-400 border border-slate-700"
                              : "text-slate-400 hover:text-white"
                          }`}
                        >
                          Short / Follow-up Version
                        </button>
                      </div>

                      <span className="text-[11px] text-slate-500">
                        {wordCount} words
                      </span>
                    </div>

                    {/* Email Body Editor */}
                    <div>
                      <textarea
                        rows={12}
                        value={activeVersion === "standard" ? body : shortBody}
                        onChange={(e) => {
                          if (activeVersion === "standard") {
                            setBody(e.target.value);
                          } else {
                            setShortBody(e.target.value);
                          }
                        }}
                        placeholder="Click 'Generate Outreach' to create a personalized draft..."
                        className="w-full bg-slate-950 border border-slate-800 rounded-xl p-4 text-xs font-sans text-slate-200 placeholder:text-slate-600 leading-relaxed focus:outline-none focus:border-amber-500/60 transition-all resize-y"
                      />
                    </div>

                    {/* Footer Action Bar */}
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2">
                      <p className="text-[11px] text-slate-500 italic">
                        PaperFox prepares the email for your review. You control when and where to send.
                      </p>

                      <div className="flex items-center gap-2 shrink-0">
                        {draft && (
                          <Button
                            variant="outline"
                            size="sm"
                            disabled={isSaving}
                            onClick={handleSave}
                            className="text-xs h-8 px-3 border-slate-700 text-slate-300 hover:text-white flex items-center gap-1.5"
                          >
                            {isSaving ? (
                              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                            ) : saveSuccess ? (
                              <Check className="w-3.5 h-3.5 text-emerald-400" />
                            ) : (
                              <Save className="w-3.5 h-3.5" />
                            )}
                            {saveSuccess ? "Saved!" : "Save Draft"}
                          </Button>
                        )}

                        <Button
                          size="sm"
                          disabled={!body}
                          onClick={handleCopy}
                          className="text-xs h-8 px-3.5 bg-amber-500 hover:bg-amber-400 text-slate-950 font-semibold shadow flex items-center gap-1.5"
                        >
                          {copied ? (
                            <>
                              <Check className="w-3.5 h-3.5 text-slate-950" />
                              Copied!
                            </>
                          ) : (
                            <>
                              <Copy className="w-3.5 h-3.5" />
                              Copy Email
                            </>
                          )}
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </main>
        </div>
      </div>
    </ProtectedRoute>
  );
}
