import { api } from "./api";

export interface JobRequirements {
  title?: string;
  experience_years_required?: number;
  education_required?: string;
  required_skills: string[];
  preferred_skills: string[];
  programming_languages: string[];
  technologies_frameworks: string[];
  ai_ml_requirements: string[];
  responsibilities: string[];
  important_keywords: string[];
}

export interface KeywordAlignment {
  matched_keywords: string[];
  missing_keywords: string[];
  safely_usable_keywords: string[];
  unsupported_jd_keywords: string[];
}

export interface OptimizedProject {
  project_id?: string;
  project_name: string;
  relevance_score: number;
  relevance_reasons: string[];
  matched_requirements: string[];
  technologies: string[];
  bullets: string[];
  project_url?: string;
  github_url?: string;
  repository_url?: string;
}

export interface OptimizedExperience {
  id?: string;
  company: string;
  role: string;
  location?: string;
  start_date?: string;
  end_date?: string;
  is_current: boolean;
  bullets: string[];
  technologies: string[];
}

export interface OptimizedInternship {
  id?: string;
  company: string;
  role: string;
  location?: string;
  start_date?: string;
  end_date?: string;
  is_current: boolean;
  bullets: string[];
  technologies: string[];
}

export interface OptimizedSkillGroup {
  category: string;
  skills: string[];
}

export interface OptimizationMetadata {
  status: string;
  provider?: string;
  model?: string;
  generated_at: string;
  error_message?: string;
}

export interface OptimizedResumeData {
  job_id: string;
  profile_snapshot_reference?: string;
  personal_details: Record<string, any>;
  summary: string;
  education: Record<string, any>[];
  experience: OptimizedExperience[];
  internships: OptimizedInternship[];
  projects: OptimizedProject[];
  skills: OptimizedSkillGroup[];
  certifications: Record<string, any>[];
  keyword_alignment: KeywordAlignment;
  optimization_metadata: OptimizationMetadata;
}

export interface OptimizationResponse {
  job_id: string;
  company_name: string;
  role_title: string;
  status: string;
  optimized_resume_data?: OptimizedResumeData;
  created_at: string;
  updated_at: string;
}

// ── Phase 6 types ────────────────────────────────────────────────────────────

export interface ATSValidation {
  is_single_page: boolean;
  page_count: number;
  text_extractable: boolean;
  has_summary: boolean;
  has_skills: boolean;
  has_education: boolean;
  has_experience_or_projects: boolean;
}

export interface JobResumeArtifact {
  latex_source: string;
  pdf_storage_reference?: string;
  page_count: number;
  compression_level_used: number;
  /** "success" | "overflow" | "compiler_unavailable" | "error" */
  status: string;
  ats_validation: ATSValidation;
  error_message?: string;
  generated_at: string;
}

export interface JobResumeRenderResponse {
  status: string;
  message: string;
  compression_level_used: number;
  page_count: number;
  pdf_storage_reference?: string;
  ats_validation: ATSValidation;
  artifact: Record<string, any>;
}

export type ApplicationStatus =
  | "draft"
  | "applied"
  | "interview"
  | "rejected"
  | "offer"
  | "withdrawn";

export interface JobHistoryItem {
  id: string;
  company_name: string;
  role_title: string;
  job_url?: string;
  location?: string;
  application_status: ApplicationStatus | string;
  notes?: string;
  is_analyzed: boolean;
  is_optimized: boolean;
  is_resume_generated: boolean;
  status_updated_at?: string;
  created_at: string;
  updated_at: string;
}

export interface JobHistoryResponse {
  items: JobHistoryItem[];
  total: number;
  status_filter?: string;
}

export interface JobHistoryStats {
  total: number;
  by_status: Record<string, number>;
}

// ── Job Application ──────────────────────────────────────────────────────────

export interface SuggestedMissingSkill {
  skill: string;
  name?: string;
  category?: string;
  importance: "Critical" | "High" | "Medium" | "Low" | string;
  reason: string;
  importance_reason?: string;
  is_critical?: boolean;
}

export interface ConfirmedSkill {
  skill: string;
  source: string;
  confirmed_at?: string;
}

export interface MailingDraft {
  job_id: string;
  recipient_name?: string;
  recipient_email?: string;
  recipient_role?: string;
  subject: string;
  subject_options: string[];
  body: string;
  short_body?: string;
  selected_evidence: string[];
  status: "draft" | "ready" | "sent" | string;
  generated_at?: string;
  updated_at?: string;
}

export interface MailingGenerateRequest {
  recipient_name?: string;
  recipient_email?: string;
  recipient_role?: string;
}

export interface MailingDraftUpdate {
  recipient_name?: string;
  recipient_email?: string;
  recipient_role?: string;
  subject?: string;
  body?: string;
  short_body?: string;
  status?: string;
}

export interface JobApplication {
  id: string;
  user_id: string;
  company_name: string;
  role_title: string;
  job_description: string;
  job_url?: string;
  location?: string;
  requirements?: JobRequirements;
  suggested_missing_skills?: SuggestedMissingSkill[];
  approved_additional_skills?: string[];
  confirmed_skills?: ConfirmedSkill[];
  analysis_provider?: string;
  analysis_model?: string;
  is_analyzed: boolean;
  optimization?: OptimizedResumeData;
  is_optimized?: boolean;
  job_resume_artifact?: JobResumeArtifact;
  is_resume_generated?: boolean;
  mailing_draft?: MailingDraft;
  application_status?: ApplicationStatus | string;
  notes?: string;
  status_updated_at?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateJobInput {
  company_name: string;
  role_title: string;
  job_description: string;
  job_url?: string;
  location?: string;
}

// ── API functions ─────────────────────────────────────────────────────────────

export async function createJobApi(input: CreateJobInput): Promise<JobApplication> {
  const response = await api.post<JobApplication>("/jobs", input);
  return response.data;
}

export async function listJobsApi(): Promise<JobApplication[]> {
  const response = await api.get<{ items: JobApplication[]; total: number }>("/jobs");
  return response.data.items;
}

export async function getJobApi(jobId: string): Promise<JobApplication> {
  const response = await api.get<JobApplication>(`/jobs/${jobId}`);
  return response.data;
}

export async function analyzeJobApi(jobId: string): Promise<JobApplication> {
  const response = await api.post<JobApplication>(`/jobs/${jobId}/analyze`);
  return response.data;
}

export async function updateApprovedSkillsApi(
  jobId: string,
  approvedSkills: string[]
): Promise<JobApplication> {
  const response = await api.post<JobApplication>(`/jobs/${jobId}/approved-skills`, {
    approved_skills: approvedSkills,
  });
  return response.data;
}

export async function optimizeJobApi(jobId: string): Promise<OptimizationResponse> {
  const response = await api.post<OptimizationResponse>(`/jobs/${jobId}/optimize`);
  return response.data;
}

export async function getJobOptimizationApi(jobId: string): Promise<OptimizationResponse> {
  const response = await api.get<OptimizationResponse>(`/jobs/${jobId}/optimization`);
  return response.data;
}

// Phase 6 API functions

export async function renderJobResumeApi(jobId: string): Promise<JobResumeRenderResponse> {
  const response = await api.post<JobResumeRenderResponse>(`/jobs/${jobId}/render`);
  return response.data;
}

export async function getJobResumeArtifactApi(jobId: string): Promise<JobResumeArtifact> {
  const response = await api.get<JobResumeArtifact>(`/jobs/${jobId}/resume`);
  return response.data;
}

/**
 * Returns the absolute download URL for the job-specific resume PDF.
 * Use this as an <a href> target — the browser will trigger download directly.
 */
export function getJobResumePdfUrl(jobId: string): string {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
  return `${baseUrl}/jobs/${jobId}/resume/download`;
}

// Phase 7 API functions

export async function updateJobStatusApi(
  jobId: string,
  status: ApplicationStatus | string
): Promise<JobApplication> {
  const response = await api.patch<JobApplication>(`/jobs/${jobId}/status`, {
    status,
  });
  return response.data;
}

export async function updateJobNotesApi(
  jobId: string,
  notes: string
): Promise<JobApplication> {
  const response = await api.patch<JobApplication>(`/jobs/${jobId}/notes`, {
    notes,
  });
  return response.data;
}

export async function getJobHistoryApi(
  statusFilter?: string
): Promise<JobHistoryResponse> {
  const params = statusFilter ? { status: statusFilter } : {};
  const response = await api.get<JobHistoryResponse>("/jobs/history", { params });
  return response.data;
}

export async function getJobHistoryStatsApi(): Promise<JobHistoryStats> {
  const response = await api.get<JobHistoryStats>("/jobs/history/stats");
  return response.data;
}

export async function deleteJobApi(jobId: string): Promise<void> {
  await api.delete(`/jobs/${jobId}`);
}

// ── Mailing System API functions ───────────────────────────────────────────

export async function generateMailingDraftApi(
  jobId: string,
  req?: MailingGenerateRequest
): Promise<MailingDraft> {
  const response = await api.post<MailingDraft>(`/jobs/${jobId}/mailing/generate`, req || {});
  return response.data;
}

export async function getMailingDraftApi(
  jobId: string
): Promise<MailingDraft | null> {
  const response = await api.get<MailingDraft | null>(`/jobs/${jobId}/mailing`);
  return response.data;
}

export async function updateMailingDraftApi(
  jobId: string,
  data: MailingDraftUpdate
): Promise<MailingDraft> {
  const response = await api.put<MailingDraft>(`/jobs/${jobId}/mailing`, data);
  return response.data;
}

