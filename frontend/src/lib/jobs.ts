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

export async function deleteJobApi(jobId: string): Promise<void> {
  await api.delete(`/jobs/${jobId}`);
}
