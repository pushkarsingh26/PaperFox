import { api } from "./api";
import { ProjectEvidence } from "../types/profile";

export interface ExtractEvidenceResponse {
  evidence: ProjectEvidence;
  evidence_status: "unverified" | "current" | "stale" | string;
  project_name: string;
  was_cached: boolean;
  extracted_at?: string;
  evidence_version?: number;
}

export interface StoredEvidenceResponse {
  evidence: ProjectEvidence;
  evidence_status: string;
  evidence_version?: number;
  extracted_at?: string;
  project_name?: string;
  ai_analysis_text_length?: number;
}

/**
 * Extract structured evidence from a project's ai_analysis_text.
 * Idempotent: returns cached evidence if already current unless force=true.
 */
export async function extractProjectEvidenceApi(
  projectId: string,
  force: boolean = false
): Promise<ExtractEvidenceResponse> {
  const response = await api.post<ExtractEvidenceResponse>(
    `/profile/projects/${projectId}/extract-evidence`,
    null,
    { params: force ? { force: true } : {} }
  );
  return response.data;
}

/**
 * Fetch stored evidence for a project (no AI call).
 */
export async function getProjectEvidenceApi(
  projectId: string
): Promise<StoredEvidenceResponse> {
  const response = await api.get<StoredEvidenceResponse>(
    `/profile/projects/${projectId}/evidence`
  );
  return response.data;
}
