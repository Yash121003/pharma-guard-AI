import { NavLink } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

const NAV_LINKS = [
  { to: "/complaints", label: "Complaint Log" },
  { to: "/complaints/new", label: "New Intake" },
];

export function Sidebar() {
  const { user, logout } = useAuth();

  return (
    <aside className="flex h-screen w-60 shrink-0 flex-col justify-between bg-ink text-white">
      <div>
        <div className="border-b border-white/10 px-5 py-5">
          <p className="font-mono text-[11px] uppercase tracking-stamp text-white/50">Pharma QMS</p>
          <p className="mt-1 text-sm font-semibold leading-tight">
            Complaint Intake &amp; Traceability Console
          </p>
        </div>
        <nav className="flex flex-col gap-1 px-3 py-4">
          {NAV_LINKS.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `rounded-sm px-3 py-2 text-sm transition-colors ${
                  isActive ? "bg-white/10 text-white" : "text-white/70 hover:bg-white/5 hover:text-white"
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </div>

      <div className="border-t border-white/10 px-5 py-4">
        <p className="truncate text-sm font-medium">{user?.full_name}</p>
        <p className="truncate font-mono text-[11px] uppercase tracking-stamp text-white/50">{user?.role}</p>
        <button
          onClick={() => void logout()}
          className="mt-3 text-xs text-white/60 underline decoration-white/30 underline-offset-2 hover:text-white"
        >
          Sign out
        </button>
      </div>
    </aside>
  );
}
