import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { apiErrorMessage } from "../api/client";
import { Button } from "../components/ui/Button";
import { SelectField } from "../components/ui/FormField";
import type { UserRole } from "../types";

const ROLES: UserRole[] = ["agent", "qa_manager", "admin"];

export function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<UserRole>("agent");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await register({ email, password, full_name: fullName, role });
      navigate("/complaints");
    } catch (err) {
      setError(apiErrorMessage(err, "Registration failed."));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-ink px-4 py-10">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <p className="font-mono text-[11px] uppercase tracking-stamp text-white/50">Pharma QMS</p>
          <h1 className="mt-1 text-lg font-semibold text-white">Create an account</h1>
        </div>

        <form onSubmit={onSubmit} className="card space-y-4 p-6">
          <label className="block">
            <span className="field-label">Full name</span>
            <input
              required
              className="input"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Jordan Ruiz"
            />
          </label>
          <label className="block">
            <span className="field-label">Email</span>
            <input
              type="email"
              required
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
              minLength={8}
              className="input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="At least 8 characters"
            />
          </label>
          <SelectField
            label="Role"
            options={ROLES}
            value={role}
            onChange={(e) => setRole(e.target.value as UserRole)}
          />

          {error && (
            <p className="rounded-sm border border-severity-critical/30 bg-severity-critical/5 px-3 py-2 text-sm text-severity-critical">
              {error}
            </p>
          )}

          <Button type="submit" isLoading={isSubmitting} className="w-full">
            Create account
          </Button>
        </form>

        <p className="mt-4 text-center text-sm text-white/60">
          Already registered?{" "}
          <Link to="/login" className="text-white underline underline-offset-2">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
