import React, { useEffect, useState } from "react";
import { getAllCases, uploadExcel } from "../services/api";
import { useNavigate } from "react-router-dom";

export default function AdminDashboard() {

  const [cases, setCases] = useState([]);
  const [file, setFile] = useState(null);

  // 🔍 SEARCH
  const [search, setSearch] = useState("");

  // 📍 NEW FILTERS
  const [districtFilter, setDistrictFilter] = useState("");
  const [policeFilter, setPoliceFilter] = useState("");
  const [investigatorFilter, setInvestigatorFilter] = useState("");
  const [claimType, setClaimType] = useState("");

  const [allocationFrom, setAllocationFrom] = useState("");
  const [allocationTo, setAllocationTo] = useState("");

  const [firFrom, setFirFrom] = useState("");
  const [firTo, setFirTo] = useState("");

  const navigate = useNavigate();

  useEffect(() => {
    loadCases();
  }, [claimType]);

  const loadCases = async () => {
    const res = await getAllCases({
      claim_type: claimType
    });

    if (res.cases) setCases(res.cases);
  };

  const openCase = (c) => {
    navigate(`/case/${c.id}`, { state: c });
  };

  // 📁 FILE SELECT
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  // 📤 UPLOAD
  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file");
      return;
    }

    try {
      const res = await uploadExcel(file);

      if (res.message) {
        alert("Upload successful ✅");
        setFile(null);
        await loadCases();
      } else {
        alert("Upload failed ❌");
      }

    } catch (err) {
      console.error(err);
      alert("Error uploading file ❌");
    }
  };

  return (
    <div className="page">
      <div className="container">
        <div className="card">

          <h2>Admin Dashboard</h2>

          {/* 📤 UPLOAD */}
          <div>
            <input type="file" accept=".xlsx" onChange={handleFileChange} />
            <button onClick={handleUpload}>
              Upload Excel
            </button>
          </div>

          {/* 🔴 STEP 1 — GROUP FILTERS */}
          <div className="section-card">
            <h3>Filters</h3>

            <div className="grid-3">
              <input
                placeholder="Search Case ID..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />

              <input
                placeholder="District"
                value={districtFilter}
                onChange={(e) => setDistrictFilter(e.target.value)}
              />

              <input
                placeholder="Police Station"
                value={policeFilter}
                onChange={(e) => setPoliceFilter(e.target.value)}
              />

              <input
                placeholder="Investigator"
                value={investigatorFilter}
                onChange={(e) => setInvestigatorFilter(e.target.value)}
              />

              <select
                value={claimType}
                onChange={(e) => setClaimType(e.target.value)}
              >
                <option value="">All Types</option>
                <option value="health">Health</option>
                <option value="motor">Motor</option>
              </select>
            </div>
          </div>

          {/* 📅 ALLOCATION DATE */}
          <div>
            <label>Allocation Date:</label>
            <div>
              <input
                type="date"
                placeholder="From"
                onChange={(e) => setAllocationFrom(e.target.value)}
              />
              <input
                type="date"
                placeholder="To"
                onChange={(e) => setAllocationTo(e.target.value)}
              />
            </div>
          </div>

          {/* 📅 FIR DATE */}
          <div>
            <label>FIR Date:</label>
            <div>
              <input
                type="date"
                onChange={(e) => setFirFrom(e.target.value)}
              />
              <input
                type="date"
                onChange={(e) => setFirTo(e.target.value)}
              />
            </div>
          </div>

          <h3>All Cases</h3>

          {cases.length === 0 && <p>No cases found</p>}

          {/* 🔥 FILTER LOGIC */}
          {cases
            .filter((c) =>
              c.case_id?.toLowerCase().includes(search.toLowerCase())
            )

            .filter((c) =>
              districtFilter
                ? (c.district || "").toLowerCase().includes(districtFilter.toLowerCase())
                : true
            )

            .filter((c) =>
              policeFilter
                ? (c.police_station || "").toLowerCase().includes(policeFilter.toLowerCase())
                : true
            )

            .filter((c) =>
              investigatorFilter
                ? (c.investigator_name || "").toLowerCase().includes(investigatorFilter.toLowerCase())
                : true
            )

            .filter((c) => {
              if (!allocationFrom && !allocationTo) return true;

              const date = new Date(
                new Date(c.allocation_date).toLocaleString("en-US", {
                  timeZone: "Asia/Kolkata"
                })
              );
              if (allocationFrom && date < new Date(allocationFrom)) return false;
              if (allocationTo && date > new Date(allocationTo)) return false;

              return true;
            })

            .filter((c) => {
              if (!firFrom && !firTo) return true;

              const date = new Date(
              new Date(c.fir_date).toLocaleString("en-US", {
                timeZone: "Asia/Kolkata"
              })
            );
              if (firFrom && date < new Date(firFrom)) return false;
              if (firTo && date > new Date(firTo)) return false;

              return true;
            })

            .map((c) => (
              <div
                key={c.id}
                className="case-card"
                onClick={() => openCase(c)}
              >
                {/* 🔴 STEP 3 — IMPROVED CARD */}
                <div className="flex-row">
                  <b>{c.case_id}</b>
                  <span className="badge">{c.claim_type}</span>
                </div>

                <p>👤 {c.investigator_name || "Unassigned"}</p>
                <p>📍 {c.district || "N/A"}</p>
                <p>🏢 {c.police_station || "N/A"}</p>
              </div>
            ))}

        </div>
      </div>
    </div>
  );
}