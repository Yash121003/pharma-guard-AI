import type { ComplaintCreate } from "../../types";
import { Card, SectionHeader } from "../ui/Card";
import { SelectField, TextAreaField, TextField } from "../ui/FormField";

const COMPLAINT_SOURCES = ["phone", "email", "portal", "letter", "sales_rep", "other"];
const COMPLAINT_TYPES = [
  "efficacy",
  "packaging_defect",
  "contamination",
  "adverse_event",
  "labeling_error",
  "physical_defect",
  "other",
];
const SEVERITY_LEVELS = ["low", "medium", "high", "critical"];
const PRIORITY_LEVELS = ["low", "medium", "high", "urgent"];

interface Props {
  value: ComplaintCreate;
  onChange: (next: ComplaintCreate) => void;
  confidence: Record<string, number>;
}

export function ComplaintForm({ value, onChange, confidence }: Props) {
  function set<K extends keyof ComplaintCreate>(key: K, val: ComplaintCreate[K]) {
    onChange({ ...value, [key]: val });
  }

  return (
    <div className="space-y-6">
      <Card className="p-5">
        <SectionHeader number={1} title="Origin & Customer Details" />
        <div className="grid grid-cols-2 gap-4">
          <SelectField
            label="Complaint Source"
            required
            options={COMPLAINT_SOURCES}
            value={value.complaint_source}
            confidence={confidence.complaint_source}
            onChange={(e) => set("complaint_source", e.target.value as ComplaintCreate["complaint_source"])}
          />
          <TextField
            label="Customer Name"
            required
            value={value.customer_name}
            confidence={confidence.customer_name}
            onChange={(e) => set("customer_name", e.target.value)}
          />
        </div>
      </Card>

      <Card className="p-5">
        <SectionHeader number={2} title="Product & Batch Identification" />
        <div className="grid grid-cols-2 gap-4">
          <TextField
            label="Product Name"
            value={value.product_name ?? ""}
            confidence={confidence.product_name}
            onChange={(e) => set("product_name", e.target.value)}
          />
          <TextField
            label="Strength"
            value={value.strength ?? ""}
            confidence={confidence.strength}
            onChange={(e) => set("strength", e.target.value)}
            placeholder="e.g. 500mg"
          />
          <TextField
            label="Batch Number"
            value={value.batch_number ?? ""}
            confidence={confidence.batch_number}
            onChange={(e) => set("batch_number", e.target.value)}
          />
          <div className="grid grid-cols-2 gap-4">
            <TextField
              label="Mfg. Date"
              type="date"
              value={value.manufacturing_date ?? ""}
              onChange={(e) => set("manufacturing_date", e.target.value)}
            />
            <TextField
              label="Expiry Date"
              type="date"
              value={value.expiry_date ?? ""}
              onChange={(e) => set("expiry_date", e.target.value)}
            />
          </div>
          <TextField
            label="Quantity Affected"
            type="number"
            step="0.01"
            value={value.quantity_affected ?? ""}
            onChange={(e) => set("quantity_affected", e.target.value === "" ? null : Number(e.target.value))}
          />
          <TextField
            label="Quantity Unit"
            value={value.quantity_unit ?? "kg"}
            onChange={(e) => set("quantity_unit", e.target.value)}
          />
        </div>
      </Card>

      <Card className="p-5">
        <SectionHeader number={3} title="Complaint Details" />
        <div className="grid grid-cols-2 gap-4">
          <SelectField
            label="Complaint Type"
            required
            options={COMPLAINT_TYPES}
            value={value.complaint_type}
            confidence={confidence.complaint_type}
            onChange={(e) => set("complaint_type", e.target.value as ComplaintCreate["complaint_type"])}
          />
          <TextField
            label="Complaint Date"
            required
            type="date"
            value={value.complaint_date}
            confidence={confidence.complaint_date}
            onChange={(e) => set("complaint_date", e.target.value)}
          />
        </div>
        <div className="mt-4">
          <TextAreaField
            label="Description"
            required
            value={value.description}
            confidence={confidence.description}
            onChange={(e) => set("description", e.target.value)}
            placeholder="What happened, to which product, and when…"
          />
        </div>
      </Card>

      <Card className="p-5">
        <SectionHeader number={4} title="Initial Assessment & Priority" />
        <div className="grid grid-cols-2 gap-4">
          <SelectField
            label="Initial Severity"
            required
            options={SEVERITY_LEVELS}
            value={value.initial_severity}
            confidence={confidence.initial_severity}
            onChange={(e) => set("initial_severity", e.target.value as ComplaintCreate["initial_severity"])}
          />
          <SelectField
            label="Priority"
            required
            options={PRIORITY_LEVELS}
            value={value.priority}
            confidence={confidence.priority}
            onChange={(e) => set("priority", e.target.value as ComplaintCreate["priority"])}
          />
        </div>
      </Card>
    </div>
  );
}
