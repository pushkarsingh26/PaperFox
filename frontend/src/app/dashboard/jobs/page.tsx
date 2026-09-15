"use client";

import React, { useEffect, useState } from "react";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { Navbar } from "@/components/dashboard/Navbar";
import { Sidebar } from "@/components/dashboard/Sidebar";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import {
  listJobsApi,
  createJobApi,
  analyzeJobApi,
  optimizeJobApi,
  deleteJobApi,
  JobApplication,
  CreateJobInput,
} from "@/lib/jobs";
import { OptimizationReview } from "@/components/jobs/OptimizationReview";
import {
  Briefcase,
  Plus,
  Sparkles,
  Trash2,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  MapPin,
  Clock,
  Cpu,
  Layers,
  Code,
  Brain,
  ListCheck,
  Tag,
  RefreshCw,
  X,
} from "lucide-react";

export default function JobsPage() {
  const [jobs, setJobs] = useState<JobApplication[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Form State
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState<CreateJobInput>({
    company_name: "",
    role_title: "",
    job_description: "",
    job_url: "",
    location: "",
  });

  // Analysis / Selected State
  const [analyzingId, setAnalyzingId] = useState<string | null>(null);
  const [analysisError, setAnalysisError] = useState<{ id: string; msg: string } | null>(null);
  const [optimizingId, setOptimizingId] = useState<string | null>(null);
  const [optimizationError, setOptimizationError] = useState<{ id: string; msg: string } | null>(null);
  const [activeViewTab, setActiveViewTab] = useState<"intelligence" | "optimization">("intelligence");
  const [selectedJob, setSelectedJob] = useState<JobApplication | null>(null);

  const fetchJobs = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listJobsApi();
      setJobs(data);
      if (data.length > 0 && !selectedJob) {
        setSelectedJob(data[0]);
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to load job applications.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.company_name || !formData.role_title || !formData.job_description) {
      return;
    }
    setSubmitting(true);
    try {
      const created = await createJobApi(formData);
      setJobs((prev) => [created, ...prev]);
      setSelectedJob(created);
      setShowCreateModal(false);
      setFormData({
        company_name: "",
        role_title: "",
        job_description: "",
        job_url: "",
        location: "",
      });
    } catch (err: any) {
      alert(err?.response?.data?.detail || "Failed to create job application.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleAnalyze = async (jobId: string) => {
    setAnalyzingId(jobId);
    setAnalysisError(null);
    try {
      const updated = await analyzeJobApi(jobId);
      setJobs((prev) => prev.map((j) => (j.id === jobId ? updated : j)));
      if (selectedJob?.id === jobId) {
        setSelectedJob(updated);
      }
    } catch (err: any) {
      setAnalysisError({
        id: jobId,
        msg: err?.response?.data?.detail || "AI Analysis failed across fallback providers.",
      });
    } finally {
      setAnalyzingId(null);
    }
  };

  const handleOptimize = async (jobId: string) => {
    setOptimizingId(jobId);
    setOptimizationError(null);
    try {
      const optRes = await optimizeJobApi(jobId);
      setJobs((prev) =>
        prev.map((j) =>
          j.id === jobId
            ? { ...j, optimization: optRes.optimized_resume_data, is_optimized: true }
            : j
        )
      );
      if (selectedJob?.id === jobId && optRes.optimized_resume_data) {
        setSelectedJob({
          ...selectedJob,
          optimization: optRes.optimized_resume_data,
          is_optimized: true,
        });
      }
      setActiveViewTab("optimization");
    } catch (err: any) {
      setOptimizationError({
        id: jobId,
        msg: err?.response?.data?.detail || "AI Resume Optimization failed across free fallback providers.",
      });
    } finally {
      setOptimizingId(null);
    }
  };

  const handleDelete = async (jobId: string) => {
    if (!confirm("Are you sure you want to delete this job application?")) return;
    try {
      await deleteJobApi(jobId);
      setJobs((prev) => prev.filter((j) => j.id !== jobId));
      if (selectedJob?.id === jobId) {
        setSelectedJob(null);
      }
    } catch (err: any) {
      alert(err?.response?.data?.detail || "Failed to delete job application.");
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-slate-950 flex flex-col text-slate-100 selection:bg-amber-500/30 selection:text-amber-200">
        <Navbar />

        <div className="flex-1 flex">
          <Sidebar />

          <main className="flex-1 p-6 md:p-8 max-w-7xl">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
                  <Briefcase className="w-6 h-6 text-amber-400" />
                  Job Workspace
                </h1>
                <p className="text-sm text-slate-400 mt-1">
                  Target job descriptions & AI-powered requirement intelligence.
                </p>
              </div>

              <Button
                variant="primary"
                onClick={() => setShowCreateModal(true)}
                className="self-start md:self-auto flex items-center gap-2 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-semibold"
              >
                <Plus className="w-4 h-4" />
                New Job Application
              </Button>
            </div>

            {/* Error Banner */}
            {error && (
              <div className="mb-6 p-4 rounded-xl bg-red-950/40 border border-red-800/60 text-red-300 flex items-center gap-3">
                <AlertCircle className="w-5 h-5 shrink-0" />
                <span>{error}</span>
                <Button variant="outline" size="sm" onClick={fetchJobs} className="ml-auto">
                  Retry
                </Button>
              </div>
            )}

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Jobs List (Left Col) */}
              <div className="lg:col-span-5 space-y-4">
                <div className="flex items-center justify-between px-1">
                  <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                    Saved Applications ({jobs.length})
                  </span>
                  {loading && <RefreshCw className="w-3.5 h-3.5 text-amber-400 animate-spin" />}
                </div>

                {loading && jobs.length === 0 ? (
                  <div className="p-8 rounded-2xl bg-slate-900/40 border border-slate-800/80 text-center space-y-3">
                    <RefreshCw className="w-6 h-6 text-amber-400 animate-spin mx-auto" />
                    <p className="text-sm text-slate-400">Loading applications...</p>
                  </div>
                ) : jobs.length === 0 ? (
                  <div className="p-8 rounded-2xl bg-slate-900/40 border border-slate-800/80 text-center space-y-4">
                    <Briefcase className="w-10 h-10 text-slate-600 mx-auto" />
                    <div>
                      <h3 className="text-sm font-semibold text-slate-200">No Job Applications</h3>
                      <p className="text-xs text-slate-400 mt-1">
                        Add a job description to extract AI skill intelligence.
                      </p>
                    </div>
                    <Button variant="secondary" size="sm" onClick={() => setShowCreateModal(true)}>
                      Add First Job
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-3 max-h-[calc(100vh-16rem)] overflow-y-auto pr-1">
                    {jobs.map((job) => {
                      const isSelected = selectedJob?.id === job.id;
                      const isAnalyzing = analyzingId === job.id;

                      return (
                        <div
                          key={job.id}
                          onClick={() => setSelectedJob(job)}
                          className={`p-4 rounded-xl border transition-all cursor-pointer relative ${
                            isSelected
                              ? "bg-slate-900/90 border-amber-500/40 shadow-lg shadow-amber-500/5"
                              : "bg-slate-900/40 border-slate-800/70 hover:bg-slate-900/70 hover:border-slate-700"
                          }`}
                        >
                          <div className="flex items-start justify-between gap-2 mb-1.5">
                            <h3 className="font-semibold text-slate-100 text-sm line-clamp-1">
                              {job.role_title}
                            </h3>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDelete(job.id);
                              }}
                              className="text-slate-500 hover:text-red-400 transition-colors p-1"
                              title="Delete Application"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </div>

                          <p className="text-xs font-medium text-amber-400/90 mb-2">
                            {job.company_name}
                            {job.location && (
                              <span className="text-slate-400 font-normal ml-2">
                                • {job.location}
                              </span>
                            )}
                          </p>

                          <div className="flex items-center justify-between mt-3 pt-2.5 border-t border-slate-800/60 text-xs">
                            {job.is_analyzed ? (
                              <div className="flex items-center gap-1.5 text-emerald-400 font-medium">
                                <CheckCircle2 className="w-3.5 h-3.5" />
                                <span>Analyzed ({job.analysis_provider})</span>
                              </div>
                            ) : (
                              <div className="flex items-center gap-1.5 text-slate-400">
                                <Clock className="w-3.5 h-3.5" />
                                <span>Not Analyzed</span>
                              </div>
                            )}

                            <Button
                              variant="outline"
                              size="sm"
                              disabled={isAnalyzing}
                              onClick={(e) => {
                                e.stopPropagation();
                                handleAnalyze(job.id);
                              }}
                              className="text-xs h-7 px-2.5 bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border-amber-500/30"
                            >
                              {isAnalyzing ? (
                                <>
                                  <RefreshCw className="w-3 h-3 animate-spin mr-1" />
                                  Analyzing...
                                </>
                              ) : (
                                <>
                                  <Sparkles className="w-3 h-3 mr-1 text-amber-400" />
                                  {job.is_analyzed ? "Re-Analyze" : "Analyze JD"}
                                </>
                              )}
                            </Button>
                          </div>

                          {analysisError?.id === job.id && (
                            <div className="mt-2 p-2 rounded bg-red-950/60 border border-red-800 text-[11px] text-red-300">
                              {analysisError.msg}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Selected Job Requirements Detail View (Right Col) */}
              <div className="lg:col-span-7">
                {selectedJob ? (
                  <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 space-y-6">
                    {/* Detail Header */}
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800/80">
                      <div>
                        <div className="flex items-center gap-2">
                          <h2 className="text-xl font-bold text-white">{selectedJob.role_title}</h2>
                          {selectedJob.job_url && (
                            <a
                              href={selectedJob.job_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-slate-400 hover:text-amber-400 transition-colors"
                            >
                              <ExternalLink className="w-4 h-4" />
                            </a>
                          )}
                        </div>
                        <p className="text-sm font-medium text-amber-400 mt-0.5">
                          {selectedJob.company_name}
                          {selectedJob.location && (
                            <span className="text-slate-400 ml-2">({selectedJob.location})</span>
                          )}
                        </p>
                      </div>

                      <div className="flex flex-wrap items-center gap-2">
                        {selectedJob.is_analyzed && (
                          <Button
                            variant="primary"
                            size="sm"
                            disabled={optimizingId === selectedJob.id}
                            onClick={() => handleOptimize(selectedJob.id)}
                            className="bg-gradient-to-r from-amber-500 to-indigo-600 hover:from-amber-400 hover:to-indigo-500 text-slate-950 font-semibold shadow-md"
                          >
                            {optimizingId === selectedJob.id ? (
                              <>
                                <RefreshCw className="w-3.5 h-3.5 animate-spin mr-1.5" />
                                Optimizing...
                              </>
                            ) : (
                              <>
                                <Sparkles className="w-3.5 h-3.5 mr-1.5" />
                                {selectedJob.optimization ? "Re-Optimize Resume" : "Optimize Resume"}
                              </>
                            )}
                          </Button>
                        )}

                        {!selectedJob.is_analyzed && (
                          <Button
                            variant="primary"
                            size="sm"
                            disabled={analyzingId === selectedJob.id}
                            onClick={() => handleAnalyze(selectedJob.id)}
                            className="bg-amber-500 text-slate-950 font-semibold hover:bg-amber-400"
                          >
                            {analyzingId === selectedJob.id ? (
                              <>
                                <RefreshCw className="w-3.5 h-3.5 animate-spin mr-1.5" />
                                Running AI Router...
                              </>
                            ) : (
                              <>
                                <Sparkles className="w-3.5 h-3.5 mr-1.5" />
                                Extract Intelligence
                              </>
                            )}
                          </Button>
                        )}
                      </div>
                    </div>

                    {/* Optimization Error Banner */}
                    {optimizationError?.id === selectedJob.id && (
                      <div className="p-3 rounded-xl bg-red-950/60 border border-red-800 text-xs text-red-300 flex items-center justify-between">
                        <span>{optimizationError.msg}</span>
                        <Button size="sm" variant="outline" onClick={() => handleOptimize(selectedJob.id)}>Retry</Button>
                      </div>
                    )}

                    {/* View Switcher Tabs (when Analyzed or Optimized) */}
                    {selectedJob.is_analyzed && (
                      <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
                        <button
                          type="button"
                          onClick={() => setActiveViewTab("intelligence")}
                          className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                            activeViewTab === "intelligence"
                              ? "bg-slate-800 text-amber-300 border border-amber-500/30"
                              : "text-slate-400 hover:text-slate-200"
                          }`}
                        >
                          JD Intelligence
                        </button>
                        <button
                          type="button"
                          onClick={() => setActiveViewTab("optimization")}
                          className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 ${
                            activeViewTab === "optimization"
                              ? "bg-indigo-950/60 text-indigo-300 border border-indigo-500/40"
                              : "text-slate-400 hover:text-slate-200"
                          }`}
                        >
                          <Sparkles className="w-3 h-3 text-indigo-400" />
                          Optimized Resume Snapshot
                          {selectedJob.optimization && (
                            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                          )}
                        </button>
                      </div>
                    )}

                    {/* Tab 2: Optimization Review View */}
                    {activeViewTab === "optimization" && selectedJob.is_analyzed ? (
                      selectedJob.optimization ? (
                        <OptimizationReview
                          companyName={selectedJob.company_name}
                          roleTitle={selectedJob.role_title}
                          data={selectedJob.optimization}
                        />
                      ) : (
                        <div className="p-8 rounded-2xl bg-slate-950/60 border border-dashed border-slate-800 text-center space-y-4">
                          <Sparkles className="w-10 h-10 text-indigo-400 mx-auto" />
                          <div>
                            <h3 className="text-sm font-semibold text-white">No Resume Optimization Generated Yet</h3>
                            <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
                              Click "Optimize Resume" above to run PaperFox's multi-task AI pipeline and transform your candidate profile into a job-specific resume snapshot.
                            </p>
                          </div>
                          <Button
                            variant="primary"
                            size="sm"
                            disabled={optimizingId === selectedJob.id}
                            onClick={() => handleOptimize(selectedJob.id)}
                            className="bg-gradient-to-r from-amber-500 to-indigo-600 hover:from-amber-400 hover:to-indigo-500 text-slate-950 font-semibold"
                          >
                            <Sparkles className="w-4 h-4 mr-2" /> Optimize Resume Now
                          </Button>
                        </div>
                      )
                    ) : selectedJob.requirements ? (
                      <div className="space-y-6">
                        {/* Meta Requirements Row */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                          {selectedJob.requirements.experience_years_required && (
                            <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-center gap-3">
                              <Clock className="w-4 h-4 text-amber-400 shrink-0" />
                              <div>
                                <p className="text-[11px] text-slate-400 uppercase font-semibold">
                                  Required Experience
                                </p>
                                <p className="text-sm font-bold text-slate-200">
                                  {selectedJob.requirements.experience_years_required}+ Years
                                </p>
                              </div>
                            </div>
                          )}

                          {selectedJob.requirements.education_required && (
                            <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-center gap-3">
                              <Layers className="w-4 h-4 text-amber-400 shrink-0" />
                              <div>
                                <p className="text-[11px] text-slate-400 uppercase font-semibold">
                                  Education / Degree
                                </p>
                                <p className="text-sm font-bold text-slate-200 line-clamp-1">
                                  {selectedJob.requirements.education_required}
                                </p>
                              </div>
                            </div>
                          )}
                        </div>

                        {/* Mandatory Required Skills */}
                        {selectedJob.requirements.required_skills?.length > 0 && (
                          <div>
                            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1.5">
                              <ListCheck className="w-3.5 h-3.5 text-amber-400" />
                              Mandatory Required Skills
                            </h4>
                            <div className="flex flex-wrap gap-1.5">
                              {selectedJob.requirements.required_skills.map((skill, idx) => (
                                <span
                                  key={idx}
                                  className="px-2.5 py-1 rounded-lg text-xs font-medium bg-amber-500/10 text-amber-300 border border-amber-500/20"
                                >
                                  {skill}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Preferred Skills */}
                        {selectedJob.requirements.preferred_skills?.length > 0 && (
                          <div>
                            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1.5">
                              <Sparkles className="w-3.5 h-3.5 text-sky-400" />
                              Nice-to-Have / Preferred Skills
                            </h4>
                            <div className="flex flex-wrap gap-1.5">
                              {selectedJob.requirements.preferred_skills.map((skill, idx) => (
                                <span
                                  key={idx}
                                  className="px-2.5 py-1 rounded-lg text-xs font-medium bg-sky-500/10 text-sky-300 border border-sky-500/20"
                                >
                                  {skill}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Programming Languages & Tech Stack */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {selectedJob.requirements.programming_languages?.length > 0 && (
                            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
                              <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2.5 flex items-center gap-1.5">
                                <Code className="w-3.5 h-3.5 text-emerald-400" />
                                Languages
                              </h4>
                              <div className="flex flex-wrap gap-1.5">
                                {selectedJob.requirements.programming_languages.map((lang, idx) => (
                                  <span
                                    key={idx}
                                    className="px-2 py-0.5 rounded text-xs font-medium bg-emerald-500/10 text-emerald-300 border border-emerald-500/20"
                                  >
                                    {lang}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}

                          {selectedJob.requirements.technologies_frameworks?.length > 0 && (
                            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
                              <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2.5 flex items-center gap-1.5">
                                <Layers className="w-3.5 h-3.5 text-purple-400" />
                                Frameworks & Tools
                              </h4>
                              <div className="flex flex-wrap gap-1.5">
                                {selectedJob.requirements.technologies_frameworks.map((tech, idx) => (
                                  <span
                                    key={idx}
                                    className="px-2 py-0.5 rounded text-xs font-medium bg-purple-500/10 text-purple-300 border border-purple-500/20"
                                  >
                                    {tech}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>

                        {/* AI / ML Requirements */}
                        {selectedJob.requirements.ai_ml_requirements?.length > 0 && (
                          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
                            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2.5 flex items-center gap-1.5">
                              <Brain className="w-3.5 h-3.5 text-pink-400" />
                              AI / ML Requirements
                            </h4>
                            <div className="flex flex-wrap gap-1.5">
                              {selectedJob.requirements.ai_ml_requirements.map((aiml, idx) => (
                                <span
                                  key={idx}
                                  className="px-2.5 py-1 rounded-lg text-xs font-medium bg-pink-500/10 text-pink-300 border border-pink-500/20"
                                >
                                  {aiml}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Core Responsibilities */}
                        {selectedJob.requirements.responsibilities?.length > 0 && (
                          <div>
                            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2.5">
                              Core Responsibilities
                            </h4>
                            <ul className="space-y-1.5 pl-4 list-disc text-xs text-slate-300 leading-relaxed">
                              {selectedJob.requirements.responsibilities.map((resp, idx) => (
                                <li key={idx}>{resp}</li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {/* ATS Keywords */}
                        {selectedJob.requirements.important_keywords?.length > 0 && (
                          <div>
                            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1.5">
                              <Tag className="w-3.5 h-3.5 text-amber-400" />
                              ATS Keywords
                            </h4>
                            <div className="flex flex-wrap gap-1.5">
                              {selectedJob.requirements.important_keywords.map((kw, idx) => (
                                <span
                                  key={idx}
                                  className="px-2 py-0.5 rounded text-[11px] font-mono bg-slate-800 text-slate-300 border border-slate-700"
                                >
                                  #{kw}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="p-8 rounded-xl bg-slate-950/40 border border-slate-800/80 text-center space-y-3">
                        <Sparkles className="w-8 h-8 text-amber-400/60 mx-auto" />
                        <div>
                          <h4 className="text-sm font-semibold text-slate-200">
                            Job Requirements Not Yet Extracted
                          </h4>
                          <p className="text-xs text-slate-400 mt-1">
                            Click "Extract Intelligence" to analyze this JD using Gemini, Groq, or OpenRouter.
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-12 text-center text-slate-500 space-y-3">
                    <Briefcase className="w-10 h-10 mx-auto text-slate-700" />
                    <p className="text-sm">Select an application from the left to view requirements.</p>
                  </div>
                )}
              </div>
            </div>

            {/* Create Job Modal */}
            {showCreateModal && (
              <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
                <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg p-6 space-y-5 shadow-2xl relative">
                  <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                    <h3 className="text-lg font-bold text-white flex items-center gap-2">
                      <Plus className="w-5 h-5 text-amber-400" />
                      Add Job Application
                    </h3>
                    <button
                      onClick={() => setShowCreateModal(false)}
                      className="text-slate-400 hover:text-white transition-colors"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>

                  <form onSubmit={handleCreate} className="space-y-4">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                          Company Name *
                        </label>
                        <input
                          type="text"
                          required
                          value={formData.company_name}
                          onChange={(e) =>
                            setFormData({ ...formData, company_name: e.target.value })
                          }
                          placeholder="e.g. OpenAI"
                          className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500/50"
                        />
                      </div>

                      <div>
                        <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                          Target Role Title *
                        </label>
                        <input
                          type="text"
                          required
                          value={formData.role_title}
                          onChange={(e) =>
                            setFormData({ ...formData, role_title: e.target.value })
                          }
                          placeholder="e.g. Senior AI Engineer"
                          className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500/50"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                          Location (Optional)
                        </label>
                        <input
                          type="text"
                          value={formData.location || ""}
                          onChange={(e) =>
                            setFormData({ ...formData, location: e.target.value })
                          }
                          placeholder="e.g. Remote / San Francisco"
                          className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500/50"
                        />
                      </div>

                      <div>
                        <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                          Job URL (Optional)
                        </label>
                        <input
                          type="url"
                          value={formData.job_url || ""}
                          onChange={(e) =>
                            setFormData({ ...formData, job_url: e.target.value })
                          }
                          placeholder="https://..."
                          className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500/50"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                        Job Description Text *
                      </label>
                      <textarea
                        required
                        rows={6}
                        value={formData.job_description}
                        onChange={(e) =>
                          setFormData({ ...formData, job_description: e.target.value })
                        }
                        placeholder="Paste the full job description here..."
                        className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500/50 font-mono text-xs leading-relaxed"
                      />
                    </div>

                    <div className="flex items-center justify-end gap-3 pt-2">
                      <Button
                        type="button"
                        variant="secondary"
                        onClick={() => setShowCreateModal(false)}
                      >
                        Cancel
                      </Button>
                      <Button
                        type="submit"
                        variant="primary"
                        disabled={submitting}
                        className="bg-amber-500 text-slate-950 font-semibold hover:bg-amber-400"
                      >
                        {submitting ? "Saving..." : "Save Job Application"}
                      </Button>
                    </div>
                  </form>
                </div>
              </div>
            )}
          </main>
        </div>
      </div>
    </ProtectedRoute>
  );
}
