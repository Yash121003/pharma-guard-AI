import { useState, type FormEvent } from "react";
import { chat } from "../../api/ai";
import { apiErrorMessage } from "../../api/client";
import type { ChatMessage } from "../../types";
import { Button } from "../ui/Button";

export function ChatPanel({ complaintId }: { complaintId: number }) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [question, setQuestion] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    const trimmed = question.trim();
    if (!trimmed) return;

    setError(null);
    setMessages((prev) => [...prev, { role: "user", message: trimmed }]);
    setQuestion("");
    setIsSending(true);
    try {
      const res = await chat(complaintId, trimmed);
      setMessages((prev) => [...prev, { role: "assistant", message: res.answer }]);
    } catch (err) {
      setError(apiErrorMessage(err, "The assistant couldn't answer that."));
    } finally {
      setIsSending(false);
    }
  }

  return (
    <div className="card flex h-[420px] flex-col p-5">
      <p className="mb-3 font-mono text-[11px] uppercase tracking-stamp text-slate">Intake Assistant</p>

      <div className="flex-1 space-y-3 overflow-y-auto pr-1">
        {messages.length === 0 && (
          <p className="text-sm text-slate-light">
            Ask about this complaint — e.g. "what batch is this?" or "is this a high risk case?"
          </p>
        )}
        {messages.map((m, i) => (
          <div
            key={i}
            className={`max-w-[90%] rounded-sm px-3 py-2 text-sm ${
              m.role === "user" ? "ml-auto bg-ink text-white" : "bg-paper text-ink"
            }`}
          >
            {m.message}
          </div>
        ))}
        {isSending && <p className="text-xs text-slate-light">Assistant is thinking…</p>}
      </div>

      {error && <p className="mt-2 text-xs text-severity-critical">{error}</p>}

      <form onSubmit={onSubmit} className="mt-3 flex gap-2 border-t border-line pt-3">
        <input
          className="input"
          placeholder="Ask a question…"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <Button type="submit" isLoading={isSending} disabled={!question.trim()}>
          Send
        </Button>
      </form>
    </div>
  );
}
