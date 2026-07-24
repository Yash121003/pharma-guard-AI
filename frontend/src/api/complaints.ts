import { apiClient } from "./client";
import type { ComplaintCreate, ComplaintListItem, ComplaintPublic } from "../types";

export async function listComplaints(params?: { limit?: number; offset?: number }): Promise<ComplaintListItem[]> {
  const { data } = await apiClient.get<ComplaintListItem[]>("/complaints", { params });
  return data;
}

export async function getComplaint(id: number): Promise<ComplaintPublic> {
  const { data } = await apiClient.get<ComplaintPublic>(`/complaints/${id}`);
  return data;
}

export async function createComplaint(payload: ComplaintCreate): Promise<ComplaintPublic> {
  const { data } = await apiClient.post<ComplaintPublic>("/complaints", payload);
  return data;
}
