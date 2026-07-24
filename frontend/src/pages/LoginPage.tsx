import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { apiErrorMessage } from "../api/client";
import { Button } from "../components/ui/Button";

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await login(email, password);
      navigate("/complaints");
    } catch (err) {
      setError(apiErrorMessage(err, "Incorrect email or password."));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-ink px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <p className="font-mono text-[11px] uppercase tracking-stamp text-white/50">Pharma QMS</p>
          <h1 className="mt-1 text-lg font-semibold text-white">Complaint Intake Console</h1>
        </div>

        <form onSubmit={onSubmit} className="card space-y-4 p-6">
          <label className="block">
            <span className="field-label">Email</span>
            <input
              type="email"
              required
              autoFocus
              className="input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@company.com"
            />
          </label>
          <label className="block">
            <span className="field-label">Password</span>
            <input
              type="password"
              required
              className="input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
            />
          </label>

          {error && (
            <p className="rounded-sm border border-severity-critical/30 bg-severity-critical/5 px-3 py-2 text-sm text-severity-critical">
              {error}
            </p>
          )}

          <Button type="submit" isLoading={isSubmitting} className="w-full">
            Sign in
          </Button>
        </form>

        <p className="mt-4 text-center text-sm text-white/60">
          No account?{" "}
          <Link to="/register" className="text-white underline underline-offset-2">
            Register
          </Link>
        </p>
      </div>
    </div>
  );
}
