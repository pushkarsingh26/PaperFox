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

export interface JobApplication {
  id: string;
  user_id: string;
  company_name: string;
  role_title: string;
  job_description: string;
  job_url?: string;
  location?: string;
  requirements?: JobRequirements;
  analysis_provider?: string;
  analysis_model?: string;
  is_analyzed: boolean;
  optimization?: OptimizedResumeData;
  is_optimized?: boolean;
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

export async function optimizeJobApi(jobId: string): Promise<OptimizationResponse> {
  const response = await api.post<OptimizationResponse>(`/jobs/${jobId}/optimize`);
  return response.data;
}

export async function getJobOptimizationApi(jobId: string): Promise<OptimizationResponse> {
  const response = await api.get<OptimizationResponse>(`/jobs/${jobId}/optimization`);
  return response.data;
}

export async function deleteJobApi(jobId: string): Promise<void> {
  await api.delete(`/jobs/${jobId}`);
}
