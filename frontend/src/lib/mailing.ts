import { api } from "./api";

export interface MailingGenerateRequest {
  job_id: string;
  recipient_name?: string;
  recipient_email?: string;
  recipient_role?: string;
  is_short?: boolean;
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
  status: string;
  generated_at?: string;
  updated_at?: string;
}

export function getMailingErrorMessage(err: any, fallbackMessage: string): string {
  const status = err?.response?.status;
  const detail = err?.response?.data?.detail;

  if (typeof detail === "string" && detail.trim()) {
    return detail;
  }

  if (status === 401) {
    return "Your session has expired. Please sign in again.";
  }
  if (status === 403) {
    return "You don't have access to this job application.";
  }
  if (status === 404) {
    return "Job application not found.";
  }
  if (status === 422) {
    return "Prerequisite data is missing or invalid for this outreach email.";
  }
  if (status === 500) {
    return "Unable to generate the outreach email right now.";
  }

  return fallbackMessage;
}

export async function generateMailingDraftApi(
  req: MailingGenerateRequest
): Promise<MailingDraft> {
  const response = await api.post<MailingDraft>("/mailing/generate", req);
  return response.data;
}

export async function getMailingDraftApi(
  jobId: string
): Promise<MailingDraft | null> {
  try {
    const response = await api.get<MailingDraft | null>(`/mailing/${jobId}`);
    return response.data;
  } catch (err: any) {
    if (err?.response?.status === 404) {
      return null;
    }
    throw err;
  }
}

export async function updateMailingDraftApi(
  jobId: string,
  data: MailingDraftUpdate
): Promise<MailingDraft> {
  const response = await api.put<MailingDraft>(`/mailing/${jobId}`, data);
  return response.data;
}
