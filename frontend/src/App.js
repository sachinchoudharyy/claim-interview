import { Routes, Route } from "react-router-dom";



import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import NewCase from "./pages/NewCase";
import Interview from "./pages/Interview";
import CaseDetails from "./pages/CaseDetails";
import AdminDashboard from "./pages/AdminDashboard"; // ✅ NEW

import DocumentAnalysis from "./pages/DocumentAnalysis";

export default function App() {

  const user = JSON.parse(localStorage.getItem("user"));

  return (
    <Routes>
      <Route path="/" element={<Login />} />

      {/* ✅ SAFE ROLE-BASED DASHBOARD */}
      <Route
        path="/dashboard"
        element={
          user?.role === "admin"
            ? <AdminDashboard />
            : <Dashboard />
        }
      />

      {/* ✅ KEEP EVERYTHING ELSE SAME */}
      <Route path="/new-case" element={<NewCase />} />
      <Route path="/interview" element={<Interview />} />
      <Route path="/case/:id" element={<CaseDetails />} />

      <Route
        path="/case/:id/document-analysis"
        element={<DocumentAnalysis />}
      />
    </Routes>
  );
}