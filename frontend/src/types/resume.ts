export type ResumeArtifactStatus = "success" | "overflow" | "compiler_unavailable" | "error" | "draft";

export interface ResumeArtifact {
  id: string;
  user_id: string;
  type: "base" | string;
  latex_source: string;
  pdf_storage_reference?: string | null;
  page_count: number;
  status: ResumeArtifactStatus;
  error_message?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ResumeGenerateResponse {
  status: ResumeArtifactStatus;
  message: string;
  page_count: number;
  pdf_storage_reference?: string | null;
  artifact?: ResumeArtifact;
}
