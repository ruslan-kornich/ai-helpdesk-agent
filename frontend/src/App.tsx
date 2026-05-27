import { Route, Routes } from "react-router-dom";
import { ProtectedRoute } from "./auth";
import Layout from "./components/Layout";
import Analytics from "./pages/Analytics";
import Login from "./pages/Login";
import Settings from "./pages/Settings";
import Simulator from "./pages/Simulator";
import TicketDetail from "./pages/TicketDetail";
import Tickets from "./pages/Tickets";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Tickets />} />
        <Route path="tickets/:ticketId" element={<TicketDetail />} />
        <Route path="simulator" element={<Simulator />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="settings" element={<Settings />} />
      </Route>
    </Routes>
  );
}
