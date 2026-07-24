import { useRef, useState, type DragEvent } from "react";
import { extractFromText, uploadAndExtract } from "../../api/ai";
import { apiErrorMessage } from "../../api/client";
import type { ExtractResponse } from "../../types";
import { Button } from "../ui/Button";
import { Spinner } from "../ui/Spinner";

const SUPPORTED = ["pdf", "docx", "txt", "eml"];

export function IntakeSourcePanel({ onExtracted }: { onExtracted: (result: ExtractResponse) => void }) {
  const [mode, setMode] = useState<"upload" | "paste">("upload");
  const [pastedText, setPastedText] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  async function handleFile(file: File) {
    setError(null);
    setFileName(file.name);
    setIsProcessing(true);
    try {
      const result = await uploadAndExtract(file);
      onExtracted(result);
    } catch (err) {
      setError(apiErrorMessage(err, "Could not extract this document."));
    } finally {
      setIsProcessing(false);
    }
  }

  async function handlePasteSubmit() {
    if (!pastedText.trim()) return;
    setError(null);
    setIsProcessing(true);
    try {
      const result = await extractFromText(pastedText);
      onExtracted(result);
    } catch (err) {
      setError(apiErrorMessage(err, "Could not extract fields from this text."));
    } finally {
      setIsProcessing(false);
    }
  }

  function onDrop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) void handleFile(file);
  }

  return (
    <div className="card p-5">
      <div className="mb-4 flex items-center gap-4 border-b border-line pb-3">
        <button
          onClick={() => setMode("upload")}
          className={`font-mono text-[11px] uppercase tracking-stamp ${
            mode === "upload" ? "text-ink" : "text-slate-light"
          }`}
        >
          Upload Document
        </button>
        <button
          onClick={() => setMode("paste")}
          className={`font-mono text-[11px] uppercase tracking-stamp ${
            mode === "paste" ? "text-ink" : "text-slate-light"
          }`}
        >
          Paste Text
        </button>
      </div>

      {mode === "upload" ? (
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setIsDragging(true);
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={onDrop}
          onClick={() => inputRef.current?.click()}
          className={`flex cursor-pointer flex-col items-center justify-center rounded-sm border-2 border-dashed
            px-6 py-10 text-center transition-colors ${
              isDragging ? "border-signal bg-signal-light" : "border-line hover:border-slate-light"
            }`}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".pdf,.docx,.txt,.eml"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) void handleFile(file);
            }}
          />
          <p className="font-mono text-[11px] uppercase tracking-stamp text-slate">
            Drag &amp; drop complaint document here
          </p>
          <p className="mt-1 text-xs text-slate-light">or click to browse — {SUPPORTED.join(", ")}</p>
          {fileName && <p className="mt-3 text-sm text-ink">{fileName}</p>}
        </div>
      ) : (
        <div>
          <textarea
            className="input min-h-[160px]"
            placeholder="Paste the complaint email, letter, or notes here…"
            value={pastedText}
            onChange={(e) => setPastedText(e.target.value)}
          />
          <Button
            className="mt-3 w-full"
            onClick={() => void handlePasteSubmit()}
            isLoading={isProcessing}
            disabled={!pastedText.trim()}
          >
            Extract Fields with AI
          </Button>
        </div>
      )}

      {isProcessing && mode === "upload" && (
        <div className="mt-3">
          <Spinner label="Extracting structured fields…" />
        </div>
      )}

      {error && (
        <p className="mt-3 rounded-sm border border-severity-critical/30 bg-severity-critical/5 px-3 py-2 text-sm text-severity-critical">
          {error}
        </p>
      )}
    </div>
  );
}
