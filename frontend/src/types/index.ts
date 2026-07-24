// Mirrors backend/app/models/*.py enums and backend/app/schemas/*.py shapes
// exactly. Keep in sync if the backend schema changes.

export type UserRole = "admin" | "qa_manager" | "agent";

export interface UserPublic {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
}

export type ComplaintSource = "phone" | "email" | "portal" | "letter" | "sales_rep" | "other";

export type ComplaintType =
  | "efficacy"
  | "packaging_defect"
  | "contamination"
  | "adverse_event"
  | "labeling_error"
  | "physical_defect"
  | "other";

export type SeverityLevel = "low" | "medium" | "high" | "critical";

export type PriorityLevel = "low" | "medium" | "high" | "urgent";

export type ComplaintStatus = "pending_triage" | "under_investigation" | "capa_assigned" | "closed";

export interface ComplaintCreate {
  complaint_source: ComplaintSource;
  customer_name: string;

  product_name?: string | null;
  strength?: string | null;
  batch_number?: string | null;
  manufacturing_date?: string | null; // YYYY-MM-DD
  expiry_date?: string | null;
  quantity_affected?: number | null;
  quantity_unit?: string | null;

  complaint_type: ComplaintType;
  complaint_date: string;
  description: string;

  initial_severity: SeverityLevel;
  priority: PriorityLevel;

  source_document_path?: string | null;
  source_document_type?: string | null;
}

export interface ComplaintPublic {
  id: number;
  complaint_source: ComplaintSource;
  customer_name: string;
  product_id: number | null;
  product_name_raw: string | null;
  strength: string | null;
  batch_id: number | null;
  batch_number_raw: string | null;
  manufacturing_date: string | null;
  expiry_date: string | null;
  quantity_affected: number | null;
  quantity_unit: string | null;
  complaint_type: ComplaintType;
  complaint_date: string;
  description: string;
  initial_severity: SeverityLevel;
  priority: PriorityLevel;
  status: ComplaintStatus;
  ai_summary: string | null;
  ai_root_cause: string | null;
  ai_capa_recommendation: string | null;
  ai_risk_level: string | null;
  ai_completeness_score: number | null;
  ai_completeness_notes: string | null;
  is_duplicate_of_id: number | null;
  created_by_id: number | null;
  created_at: string;
  updated_at: string;
}

export interface ComplaintListItem {
  id: number;
  customer_name: string;
  product_name_raw: string | null;
  complaint_type: ComplaintType;
  status: ComplaintStatus;
  priority: PriorityLevel;
  complaint_date: string;
  created_at: string;
}

// --- AI schemas ---

export interface ExtractResponse {
  fields: Record<string, unknown>;
  confidence: Record<string, number>;
  raw_text_preview: string;
  source_document_path?: string | null;
}

export interface ChatMessage {
  role: "user" | "assistant" | "system";
  message: string;
}

export interface SummaryResponse {
  summary: string;
}

export interface RootCauseResponse {
  root_cause: string;
}

export interface CapaResponse {
  capa_recommendation: string;
}

export interface RiskResponse {
  risk_level: string;
  reasoning: string;
}

export interface DuplicateCheckResponse {
  is_duplicate: boolean;
  duplicate_of_id: number | null;
  reasoning: string;
}

export interface CompletenessResponse {
  completeness_score: number;
  completeness_notes: string;
  missing_fields: string[];
}
