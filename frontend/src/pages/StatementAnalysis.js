import React, {
  useEffect,
  useState
} from "react";

import {
  useNavigate,
  useParams
} from "react-router-dom";

import axios from "axios";

import "../styles/document-analysis.css";

export default function StatementAnalysis() {

  const { id } = useParams();

  const navigate = useNavigate();

  const [documents, setDocuments] = useState([]);

  const [selectedDoc, setSelectedDoc] = useState(null);

  const [loading, setLoading] = useState(false);

  const [report, setReport] = useState("");

  useEffect(() => {

    loadDocuments();

  }, []);

  const loadDocuments = async () => {

    try {

      const res = await axios.get(
        `http://localhost:8000/documents/${id}`
      );

      const pdfs = (res.data || []).filter(
        (doc) =>
          doc.file_type &&
          doc.file_type.toLowerCase().includes("pdf")
      );

      setDocuments(pdfs);

    } catch (err) {

      console.error(err);

    }
  };

  const analyzeStatement = async () => {

    if (!selectedDoc) {

      alert("Select PDF first");

      return;
    }

    try {

      setLoading(true);

      setReport("");

      const res = await axios.post(
        `http://localhost:8000/statement-analysis/analyze/${selectedDoc.id}`
      );

      setReport(res.data.report);

    } catch (err) {

      console.error(err);

      alert("Analysis failed");

    } finally {

      setLoading(false);

    }
  };

  return (

    <div className="page">

      <div className="container">

        <div className="card">

          <button
            className="back-btn"
            onClick={() => navigate(-1)}
          >
            ← Back
          </button>

          <h2>
            Bank Statement Analysis
          </h2>

          <div className="doc-grid">

            {documents.map((doc) => (

              <div
                key={doc.id}
                className={`doc-card ${
                  selectedDoc?.id === doc.id
                    ? "selected"
                    : ""
                }`}
                onClick={() => setSelectedDoc(doc)}
              >

                <div
                  style={{
                    padding: "20px"
                  }}
                >
                  📄 PDF
                </div>

                <p>
                  {doc.subcategory || "Document"}
                </p>

              </div>

            ))}

          </div>

          <button
            onClick={analyzeStatement}
            disabled={loading}
          >

            {
              loading
                ? "Analyzing..."
                : "Analyze Statement"
            }

          </button>

          {report && (

            <div
              className="result-card"
              style={{
                marginTop: "20px"
              }}
            >

              <h3>
                Statement Analysis Report
              </h3>

              <pre
                style={{
                  whiteSpace: "pre-wrap",
                  fontFamily: "inherit"
                }}
              >
                {report}
              </pre>

            </div>

          )}

        </div>

      </div>

    </div>
  );
}