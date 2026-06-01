import React, { useEffect, useState, useContext } from "react";
import { getCases } from "../services/api";
import { useNavigate } from "react-router-dom";
import "../styles/dashboard.css";
import { LoadingContext } from "../context/LoadingContext";

export default function Dashboard() {

  const [cases, setCases] = useState([]);
  const [search, setSearch] = useState("");
  const [filterType, setFilterType] = useState("all");

  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user"));
  const { setLoading } = useContext(LoadingContext);

  useEffect(() => {
    loadCases();
  }, []);

  const loadCases = async () => {
    try {
      setLoading(true);

      const res = await getCases(user.id);

      if (res.cases) {
        const unique = Array.from(
          new Map(res.cases.map((c) => [c.id, c])).values()
        );
        setCases(unique);
      }

    } finally {
      setLoading(false);
    }
  };

  const openCase = (c) => {
    navigate(`/case/${c.id}`, { state: c });
  };

  const filteredCases = cases
    .filter((c) =>
      c.case_id.toLowerCase().includes(search.toLowerCase())
    )
    .filter((c) => {
      if (filterType === "all") return true;
      return c.claim_type === filterType;
    });

  return (
    <div className="page">
      <div className="container">
        <div className="card">

          <div className="dashboard-header">
            <h2>Dashboard</h2>
            <button
              className="new-case-btn"
              onClick={() => navigate("/new-case")}
            >
              + New Case
            </button>
          </div>

          {/* 🔴 STEP 1 — GROUP SEARCH + FILTER */}
          <div className="section-card">
            <div className="flex-row">
              <input
                className="search-box"
                placeholder="Search case ID..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />

              <select
                className="filter-box"
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
              >
                <option value="all">All</option>
                <option value="health">Health</option>
                <option value="motor">Motor</option>
              </select>
            </div>
          </div>

          <h3>Previous Cases</h3>

          {filteredCases.length === 0 && <p>No cases found</p>}

          {filteredCases.map((c) => (
            <div
              key={c.id}
              className="case-card"
              onClick={() => openCase(c)}
            >
              <p><b>Case ID:</b> {c.case_id}</p>
              <p><b>Type:</b> {c.claim_type}</p>
            </div>
          ))}

        </div>
      </div>
    </div>
  );
}