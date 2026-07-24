import { Navigate, Route, Routes } from "react-router-dom";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { ComplaintListPage } from "./pages/ComplaintListPage";
import { NewComplaintPage } from "./pages/NewComplaintPage";
import { ComplaintDetailPage } from "./pages/ComplaintDetailPage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { ProtectedRoute } from "./routes/ProtectedRoute";
import { AppShell } from "./components/layout/AppShell";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/complaints" replace />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route
        path="/complaints"
        element={
          <ProtectedRoute>
            <AppShell>
              <ComplaintListPage />
            </AppShell>
          </ProtectedRoute>
        }
      />
      <Route
        path="/complaints/new"
        element={
          <ProtectedRoute>
            <AppShell>
              <NewComplaintPage />
            </AppShell>
          </ProtectedRoute>
        }
      />
      <Route
        path="/complaints/:id"
        element={
          <ProtectedRoute>
            <AppShell>
              <ComplaintDetailPage />
            </AppShell>
          </ProtectedRoute>
        }
      />

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
