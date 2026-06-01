import React, { useState, useContext } from "react";
import { createCase } from "../services/api";
import { useNavigate } from "react-router-dom";
import "../styles/case.css";
import { LoadingContext } from "../context/LoadingContext";
import { useLocation } from "react-router-dom";

const motorCategories = [
  "Insured",
  "Driver",
  "Claimant",
  "Accident spot",
  "Hospital",
  "Police station",
  "Eye witnesses",
  "Others"
];

export default function NewCase({ setPage, setCurrentCase }) {

  const [claimType, setClaimType] = useState(null);
  
  const [subcategory, setSubcategory] = useState("");
  const [subcategoryDetail, setSubcategoryDetail] = useState("");
  const [language, setLanguage] = useState("");

  const location = useLocation();
  const existingCase = location.state?.caseData || null;
  const fromCaseDetails = location.state?.fromCaseDetails;

  const [caseId, setCaseId] = useState(existingCase?.case_id || "");

  const user = JSON.parse(localStorage.getItem("user"));
  const navigate = useNavigate();
  const { setLoading } = useContext(LoadingContext);

  const startCase = async () => {
    try {
      setLoading(true);

      let caseResponse;

      if (existingCase) {
        // ✅ DO NOT CREATE NEW CASE
        caseResponse = existingCase;
      } else {
        // ✅ CREATE NEW CASE (NORMAL FLOW)
        const res = await createCase({
          case_id: caseId,
          claim_type: claimType,
          user_id: user.id,
          category: claimType,
          investigator_name: user.name   // ✅ FIX 2
        });

        if (res.error) {
          alert(res.error);
          return;
        }

        caseResponse = res;
      }

      const caseData = {
        ...caseResponse,
        category: claimType,          // ✅ FIX
        subcategory: subcategory,
        subcategory_detail: subcategory === "Others" ? subcategoryDetail : null,
      };

      if (setCurrentCase) setCurrentCase(caseData);
      if (setPage) setPage("interview");

      navigate("/interview", { state: caseData });

    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="card case-box">
        <div className="section-card">

          <h2>New Case</h2>

          {!claimType && (
            <div className="case-buttons">
              <button onClick={() => setClaimType("health")}>
                Health Insurance
              </button>
              <button onClick={() => setClaimType("motor")}>
                Motor Insurance
              </button>
            </div>
          )}

          {claimType && (
            <>
              <input
                placeholder="Enter Case ID"
                value={caseId}
                disabled={!!existingCase}   // ✅ IMPORTANT
                onChange={(e) => setCaseId(e.target.value)}
              />

              {claimType === "motor" && (
                <>
                  <select
                    value={subcategory}
                    onChange={(e) => setSubcategory(e.target.value)}
                  >
                    <option>Select Category</option>
                    {motorCategories.map((c) => (
                      <option key={c}>{c}</option>
                    ))}
                  </select>

                  {subcategory === "Others" && (
                    <input
                      placeholder="Enter custom subcategory"
                      value={subcategoryDetail}
                      onChange={(e) => setSubcategoryDetail(e.target.value)}
                    />
                  )}
                </>
              )}

              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
              >
                <option>Select Language</option>
                <option value="en">English</option>
                <option value="hi">Hindi</option>
              </select>

              <button onClick={startCase}>
                Start Interview
              </button>
            </>
          )}

        </div>
      </div>
    </div>
  );
}