import type { InputHTMLAttributes, SelectHTMLAttributes, TextareaHTMLAttributes } from "react";
import { labelize } from "../../lib/formatters";

function ConfidenceMark({ confidence }: { confidence?: number }) {
  if (confidence === undefined) return null;
  const pct = Math.round(confidence * 100);
  const tone = confidence >= 0.7 ? "text-severity-low" : confidence >= 0.4 ? "text-severity-medium" : "text-severity-high";
  return <span className={`font-mono text-[10px] ${tone}`}>AI {pct}%</span>;
}

interface FieldWrapperProps {
  label: string;
  required?: boolean;
  confidence?: number;
  hint?: string;
}

export function TextField({
  label,
  required,
  confidence,
  hint,
  ...rest
}: FieldWrapperProps & InputHTMLAttributes<HTMLInputElement>) {
  return (
    <label className="block">
      <span className="field-label flex items-center justify-between">
        <span>
          {label}
          {required && <span className="text-severity-critical"> *</span>}
        </span>
        <ConfidenceMark confidence={confidence} />
      </span>
      <input className="input" {...rest} />
      {hint && <span className="mt-1 block text-xs text-slate-light">{hint}</span>}
    </label>
  );
}

export function SelectField({
  label,
  required,
  options,
  confidence,
  ...rest
}: FieldWrapperProps & SelectHTMLAttributes<HTMLSelectElement> & { options: string[] }) {
  return (
    <label className="block">
      <span className="field-label flex items-center justify-between">
        <span>
          {label}
          {required && <span className="text-severity-critical"> *</span>}
        </span>
        <ConfidenceMark confidence={confidence} />
      </span>
      <select className="input" {...rest}>
        <option value="" disabled>
          Select…
        </option>
        {options.map((opt) => (
          <option key={opt} value={opt}>
            {labelize(opt)}
          </option>
        ))}
      </select>
    </label>
  );
}

export function TextAreaField({
  label,
  required,
  confidence,
  ...rest
}: FieldWrapperProps & TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <label className="block">
      <span className="field-label flex items-center justify-between">
        <span>
          {label}
          {required && <span className="text-severity-critical"> *</span>}
        </span>
        <ConfidenceMark confidence={confidence} />
      </span>
      <textarea className="input min-h-[110px] resize-y" {...rest} />
    </label>
  );
}
