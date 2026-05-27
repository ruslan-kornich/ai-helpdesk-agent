import { Navigate } from "react-router-dom";
import { getAccessToken } from "./api";

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  if (!getAccessToken()) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}
