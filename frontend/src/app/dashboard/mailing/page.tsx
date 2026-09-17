"use client";

import React, { useEffect, useState, useMemo } from "react";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { Navbar } from "@/components/dashboard/Navbar";
import { Sidebar } from "@/components/dashboard/Sidebar";
import { Button } from "@/components/ui/Button";
import { listJobsApi, JobApplication } from "@/lib/jobs";
import {
  generateMailingDraftApi,
  getMailingDraftApi,
  updateMailingDraftApi,
  getMailingErrorMessage,
  MailingDraft,
} from "@/lib/mailing";
import {
  Mail,
  Send,
  Sparkles,
  Copy,
  Check,
  RefreshCw,
  AlertCircle,
  Briefcase,
  Building2,
  MapPin,
  ListCheck,
  Code,
  Save,
  CheckCircle2,
  ChevronDown,
  FileText,
} from "lucide-react";

export default function MailingSystemPage() {
  const [jobs, setJobs] = useState<JobApplication[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<string>("");
  const selectedJob = useMemo(
    () => jobs.find((j) => j.id === selectedJobId) || null,
    [jobs, selectedJobId]
  );
  const [loadingJobs, setLoadingJobs] = useState<boolean>(true);

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

  // Fetch all jobs on initial load
  const fetchJobs = async (targetJobId?: string | null) => {
    setLoadingJobs(true);
    setError(null);
    try {
      const items = await listJobsApi();
      const jobList = items || [];
      setJobs(jobList);
      if (jobList.length > 0) {
        if (targetJobId) {
          const match = jobList.find((j) => j.id === targetJobId);
          if (match) {
            setSelectedJobId(match.id);
          } else {
            setSelectedJobId("");
            setError("The requested job application could not be found.");
          }
        } else {
          setSelectedJobId((prev) =>
            prev && jobList.some((j) => j.id === prev) ? prev : jobList[0].id
          );
        }
      } else {
        setSelectedJobId("");
      }
    } catch (err: any) {
      setError(getMailingErrorMessage(err, "Failed to load job applications."));
    } finally {
      setLoadingJobs(false);
    }
  };

  useEffect(() => {
    let targetJobId: string | null = null;
    if (typeof window !== "undefined") {
      const urlParams = new URLSearchParams(window.location.search);
      targetJobId = urlParams.get("job_id") || urlParams.get("jobId");
    }
    fetchJobs(targetJobId);
  }, []);

  // Sync draft state whenever selectedJob changes
  useEffect(() => {
    if (!selectedJob) {
      setDraft(null);
      setRecipientName("");
      setRecipientEmail("");
      setRecipientRole("");
      setSubject("");
      setBody("");
      setShortBody("");
      return;
    }

    // Try loading from selectedJob or fetch from API
    if (selectedJob.mailing_draft) {
      const md = selectedJob.mailing_draft;
      setDraft(md);
      setRecipientName(md.recipient_name || "");
      setRecipientEmail(md.recipient_email || "");
      setRecipientRole(md.recipient_role || "");
      setSubject(md.subject || "");
      setBody(md.body || "");
      setShortBody(md.short_body || "");
    } else {
      // Attempt to load from independent mailing endpoint
      getMailingDraftApi(selectedJob.id)
        .then((existing) => {
          if (existing) {
            setDraft(existing);
            setRecipientName(existing.recipient_name || "");
            setRecipientEmail(existing.recipient_email || "");
            setRecipientRole(existing.recipient_role || "");
            setSubject(existing.subject || "");
            setBody(existing.body || "");
            setShortBody(existing.short_body || "");
          } else {
            setDraft(null);
            setRecipientName("");
            setRecipientEmail("");
            setRecipientRole("");
            setSubject("");
            setBody("");
            setShortBody("");
          }
        })
        .catch(() => {
          setDraft(null);
        });
    }
  }, [selectedJobId]);

  const handleSelectJob = (jobId: string) => {
    setSelectedJobId(jobId);
    setError(null);
  };

  const handleGenerate = async () => {
    if (!selectedJobId) {
      setError("Please select a valid job application first.");
      return;
    }
    setIsGenerating(true);
    setError(null);
    try {
      const generated = await generateMailingDraftApi({
        job_id: selectedJobId,
        recipient_name: recipientName.trim() || undefined,
        recipient_email: recipientEmail.trim() || undefined,
        recipient_role: recipientRole.trim() || undefined,
      });
      setDraft(generated);
      setSubject(generated.subject);
      setBody(generated.body);
      setShortBody(generated.short_body || "");
      // Update in local jobs list
      setJobs((prev) =>
        prev.map((j) => (j.id === selectedJobId ? { ...j, mailing_draft: generated } : j))
      );
    } catch (err: any) {
      setError(getMailingErrorMessage(err, "Unable to generate the outreach email right now."));
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSave = async () => {
    if (!selectedJobId) return;
    setIsSaving(true);
    setError(null);
    try {
      const updated = await updateMailingDraftApi(selectedJobId, {
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

      // Update in local jobs list
      setJobs((prev) =>
        prev.map((j) => (j.id === selectedJobId ? { ...j, mailing_draft: updated } : j))
      );
    } catch (err: any) {
      setError(getMailingErrorMessage(err, "Failed to save draft edits."));
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

  const activeContent = activeVersion === "standard" ? body : shortBody || body;
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
                    Select a job application to generate personalized cold outreach emails.
                  </p>
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
                {/* ── Left Column: Job Context & Structured Intelligence (5 cols) ── */}
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

                    {/* Stage Badges */}
                    <div className="pt-2 border-t border-slate-800/80 flex flex-wrap gap-2 text-[11px]">
                      <span className={`px-2 py-0.5 rounded-md flex items-center gap-1 font-medium ${
                        selectedJob.is_analyzed
                          ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                          : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                      }`}>
                        {selectedJob.is_analyzed ? <CheckCircle2 className="w-3 h-3" /> : <AlertCircle className="w-3 h-3" />}
                        JD Intelligence: {selectedJob.is_analyzed ? "Ready" : "Pending Analysis"}
                      </span>

                      <span className={`px-2 py-0.5 rounded-md flex items-center gap-1 font-medium ${
                        selectedJob.is_optimized
                          ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                          : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                      }`}>
                        {selectedJob.is_optimized ? <CheckCircle2 className="w-3 h-3" /> : <AlertCircle className="w-3 h-3" />}
                        Resume Snapshot: {selectedJob.is_optimized ? "Optimized" : "Pending Optimization"}
                      </span>
                    </div>

                    {/* Relevant JD Signals */}
                    {selectedJob.requirements && (
                      <div className="space-y-3 pt-2 border-t border-slate-800/80">
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
                              Key Role Context
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
                      </div>
                    )}

                    {/* Relevant Candidate Evidence */}
                    {selectedJob.optimization?.projects && selectedJob.optimization.projects.length > 0 && (
                      <div className="space-y-2 pt-2 border-t border-slate-800/80">
                        <span className="text-[11px] font-semibold uppercase tracking-wider text-emerald-400 block flex items-center gap-1.5">
                          <Code className="w-3.5 h-3.5 text-emerald-400" />
                          Relevant Candidate Projects
                        </span>
                        <div className="space-y-1.5">
                          {selectedJob.optimization.projects.slice(0, 2).map((p, idx) => (
                            <div key={idx} className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/80 text-xs">
                              <p className="font-semibold text-white">{p.project_name}</p>
                              {p.technologies && p.technologies.length > 0 && (
                                <p className="text-[11px] text-slate-400 mt-0.5">
                                  Tech: {p.technologies.join(", ")}
                                </p>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Cited Evidence Banner (if draft exists) */}
                  {draft?.selected_evidence && draft.selected_evidence.length > 0 && (
                    <div className="p-4 rounded-2xl bg-slate-900/40 border border-slate-800/80 space-y-2">
                      <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                        <CheckCircle2 className="w-3.5 h-3.5 text-amber-400" />
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

                {/* ── Right Column: Recipient & Outreach Email Workspace (7 cols) ── */}
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
                          Personalized email grounded in your verified projects and JD signals.
                        </p>
                      </div>

                      <div className="flex items-center gap-2">
                        <Button
                          size="sm"
                          disabled={!selectedJob.is_analyzed || isGenerating}
                          onClick={handleGenerate}
                          className="text-xs h-8 px-3 bg-amber-500 hover:bg-amber-400 text-slate-950 font-semibold shadow flex items-center gap-1.5 cursor-pointer"
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
                    <div className="space-y-2">
                      <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
                        Recipient Context (Optional)
                      </span>
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                        <div>
                          <label className="text-[10px] text-slate-500 uppercase font-semibold block mb-1">
                            Name
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
                          <label className="text-[10px] text-slate-500 uppercase font-semibold block mb-1">
                            Email
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
                          <label className="text-[10px] text-slate-500 uppercase font-semibold block mb-1">
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
                              className={`text-[11px] px-2.5 py-1 rounded-lg border transition-all text-left ${
                                subject === opt
                                  ? "bg-amber-500/20 border-amber-500/50 text-amber-300 font-medium"
                                  : "bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700"
                              }`}
                            >
                              {opt}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Email Body & Version Tabs */}
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1 bg-slate-950 p-0.5 rounded-lg border border-slate-800">
                          <button
                            type="button"
                            onClick={() => setActiveVersion("standard")}
                            className={`px-3 py-1 rounded-md text-[11px] font-medium transition-all ${
                              activeVersion === "standard"
                                ? "bg-amber-500 text-slate-950 font-bold"
                                : "text-slate-400 hover:text-slate-200"
                            }`}
                          >
                            Standard Email
                          </button>
                          <button
                            type="button"
                            onClick={() => setActiveVersion("short")}
                            className={`px-3 py-1 rounded-md text-[11px] font-medium transition-all ${
                              activeVersion === "short"
                                ? "bg-amber-500 text-slate-950 font-bold"
                                : "text-slate-400 hover:text-slate-200"
                            }`}
                          >
                            Short Version
                          </button>
                        </div>

                        <span className="text-[11px] text-slate-500 font-mono">
                          {wordCount} words
                        </span>
                      </div>

                      {activeVersion === "standard" ? (
                        <textarea
                          rows={12}
                          value={body}
                          onChange={(e) => setBody(e.target.value)}
                          placeholder="Email body will appear here after clicking Generate Outreach..."
                          className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3.5 text-xs text-slate-200 leading-relaxed placeholder:text-slate-600 focus:outline-none focus:border-amber-500/60 font-sans transition-all resize-y"
                        />
                      ) : (
                        <textarea
                          rows={8}
                          value={shortBody}
                          onChange={(e) => setShortBody(e.target.value)}
                          placeholder="Short version will appear here after clicking Generate Outreach..."
                          className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3.5 text-xs text-slate-200 leading-relaxed placeholder:text-slate-600 focus:outline-none focus:border-amber-500/60 font-sans transition-all resize-y"
                        />
                      )}
                    </div>

                    {/* Action Bar */}
                    <div className="pt-4 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-3">
                      <div className="flex items-center gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          disabled={!body || isSaving}
                          onClick={handleSave}
                          className="text-xs h-8 border-slate-800 hover:border-slate-700 bg-slate-950 flex items-center gap-1.5"
                        >
                          {saveSuccess ? (
                            <>
                              <Check className="w-3.5 h-3.5 text-emerald-400" />
                              <span className="text-emerald-400">Saved!</span>
                            </>
                          ) : isSaving ? (
                            <>
                              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                              Saving...
                            </>
                          ) : (
                            <>
                              <Save className="w-3.5 h-3.5 text-slate-400" />
                              Save Draft
                            </>
                          )}
                        </Button>

                        <Button
                          size="sm"
                          variant="outline"
                          disabled={!activeContent}
                          onClick={handleCopy}
                          className="text-xs h-8 border-slate-800 hover:border-slate-700 bg-slate-950 flex items-center gap-1.5"
                        >
                          {copied ? (
                            <>
                              <Check className="w-3.5 h-3.5 text-emerald-400" />
                              <span className="text-emerald-400">Copied!</span>
                            </>
                          ) : (
                            <>
                              <Copy className="w-3.5 h-3.5 text-slate-400" />
                              Copy to Clipboard
                            </>
                          )}
                        </Button>
                      </div>

                      <div className="text-[11px] text-slate-500 flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-amber-400" />
                        Humanized Cold Outreach (Peer-to-Peer)
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
