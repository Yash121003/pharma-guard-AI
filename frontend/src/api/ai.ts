import { apiClient } from "./client";
import type {
  CapaResponse,
  CompletenessResponse,
  DuplicateCheckResponse,
  ExtractResponse,
  RiskResponse,
  RootCauseResponse,
  SummaryResponse,
} from "../types";

export async function extractFromText(text: string): Promise<ExtractResponse> {
  const { data } = await apiClient.post<ExtractResponse>("/ai/extract-text", { text });
  return data;
}

export async function uploadAndExtract(file: File): Promise<ExtractResponse> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await apiClient.post<ExtractResponse>("/uploads/extract", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function chat(complaintId: number, question: string): Promise<{ answer: string }> {
  const { data } = await apiClient.post<{ answer: string }>("/ai/chat", {
    complaint_id: complaintId,
    question,
  });
  return data;
}

export async function summarize(complaintId: number): Promise<SummaryResponse> {
  const { data } = await apiClient.post<SummaryResponse>(`/ai/summarize/${complaintId}`);
  return data;
}

export async function rootCause(complaintId: number): Promise<RootCauseResponse> {
  const { data } = await apiClient.post<RootCauseResponse>(`/ai/root-cause/${complaintId}`);
  return data;
}

export async function capa(complaintId: number): Promise<CapaResponse> {
  const { data } = await apiClient.post<CapaResponse>(`/ai/capa/${complaintId}`);
  return data;
}

export async function risk(complaintId: number): Promise<RiskResponse> {
  const { data } = await apiClient.post<RiskResponse>(`/ai/risk/${complaintId}`);
  return data;
}

export async function duplicateCheck(complaintId: number): Promise<DuplicateCheckResponse> {
  const { data } = await apiClient.post<DuplicateCheckResponse>(`/ai/duplicate-check/${complaintId}`);
  return data;
}

export async function completeness(complaintId: number): Promise<CompletenessResponse> {
  const { data } = await apiClient.post<CompletenessResponse>(`/ai/completeness/${complaintId}`);
  return data;
}
