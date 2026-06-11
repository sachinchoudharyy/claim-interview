import React, { useEffect, useState } from "react";

import { useNavigate, useParams } from "react-router-dom";

import axios from "axios";

import "../styles/document-analysis.css";

export default function DocumentAnalysis() {

  const { id } = useParams();

  const navigate = useNavigate();

  const [documents, setDocuments] = useState([]);

  const [selectedDoc, setSelectedDoc] = useState(null);

  const [loading, setLoading] = useState(false);

  const [results, setResults] = useState(null);

  // ==========================================
  // LOAD DOCUMENTS
  // ==========================================

  useEffect(() => {

    loadDocuments();

  }, []);

  const loadDocuments = async () => {

    try {

      const res = await axios.get(
        `http://localhost:8000/documents/${id}`
      );

      setDocuments(res.data || []);

    } catch (e) {

      console.error(e);

    }
  };

  // ==========================================
  // ANALYZE
  // ==========================================

  const analyzeDocument = async () => {

    if (!selectedDoc) {

      alert("Select document first");

      return;
    }

    try {

      setLoading(true);

      setResults(null);

      const res = await axios.post(
        `http://localhost:8000/document-fraud/analyze/${selectedDoc.id}`
      );

      console.log(
        "ANALYSIS RESPONSE:",
        res.data
      );

      setResults(res.data);

    } catch (e) {

      console.error(e);

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

          <h2>Document Analysis</h2>

          {/* ================================= */}
          {/* DOCUMENT LIST */}
          {/* ================================= */}

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

                <img
                  src={doc.file_url}
                  alt="document"
                />

                <p>{doc.file_type}</p>

              </div>
            ))}

          </div>

          <button
            onClick={analyzeDocument}
            disabled={loading}
          >
            {
              loading
                ? "Analyzing..."
                : "Analyze Document"
            }
          </button>

          {/* ================================= */}
          {/* RESULTS */}
          {/* ================================= */}


          {results?.success && (

            <div className="analysis-results">

              <h3>
                Final Fraud Score:
                {results.final_score}/100
              </h3>

              <p>
                {results.final_verdict}
              </p>


              {/* ================================= */}
              {/* AI DETECTION */}
              {/* ================================= */}

              <div className="result-card">

                <h4>AI Detection</h4>

                <p>

                  <strong>Result:</strong>{" "}

                  {
                    results.modules.ai_detection.label
                  }

                </p>

                <p>

                  <strong>Confidence:</strong>{" "}

                  {
                    results.modules.ai_detection.confidence
                  }%

                </p>

              </div>

              {results?.modules?.face_verification && (

                <div className="result-card">

                  <h4>
                    Face Verification
                  </h4>

                  <p>

                    <strong>
                      Match Score:
                    </strong>

                    {" "}

                    {
                      results.modules
                        .face_verification
                        .score
                    }%

                  </p>

                  <p>

                    <strong>
                      Status:
                    </strong>

                    {" "}

                    {
                      results.modules
                        .face_verification
                        .status
                    }

                  </p>

                </div>

              )}

              {/* ================================= */}
              {/* METADATA */}
              {/* ================================= */}

              <div className="result-card">

                <h4>Metadata</h4>

                <p>
                  Score:
                  {results.modules.metadata.score}
                </p>

                <p>
                  Verdict:
                  {results.modules.metadata.verdict}
                </p>

                {
                  results.modules.metadata.reasons?.map(
                    (reason, index) => (
                      <p key={index}>
                        • {reason}
                      </p>
                    )
                  )
                }

              </div>

              {/* ================================= */}
              {/* ELA */}
              {/* ================================= */}

              <div className="result-card">

                <h4>ELA</h4>

                <p>
                  Score:
                  {results.modules.ela.score}
                </p>

                <p>
                  Verdict:
                  {results.modules.ela.verdict}
                </p>

                <div className="image-grid">

                  <div>

                    <h5>ELA Image</h5>

                    <img
                      src={`http://localhost:8000${results.modules.ela.images.ela}`}
                      alt=""
                    />

                  </div>

                  <div>

                    <h5>Mask</h5>

                    <img
                      src={`http://localhost:8000${results.modules.ela.images.mask}`}
                      alt=""
                    />

                  </div>

                  <div>

                    <h5>Overlay</h5>

                    <img
                      src={`http://localhost:8000${results.modules.ela.images.overlay}`}
                      alt=""
                    />

                  </div>

                  <div>

                    <h5>Detected Regions</h5>

                    <img
                      src={`http://localhost:8000${results.modules.ela.images.boxed}`}
                      alt=""
                    />

                  </div>

                </div>

              </div>

              {/* ================================= */}
              {/* MANTRANET */}
              {/* ================================= */}


              {/* ================================= */}
              {/* COPY MOVE */}
              {/* ================================= */}

              <div className="result-card">

                <h4>Copy Move</h4>

                <p>
                  Score:
                  {results.modules.copy_move.score}
                </p>

                <p>
                  Verdict:
                  {results.modules.copy_move.verdict}
                </p>

                <div className="image-grid">

                  <div>

                    <h5>Visualization</h5>

                    <img
                      src={`http://localhost:8000${results.modules.copy_move.images.visualization}`}
                      alt=""
                    />

                  </div>

                </div>

              </div>

              {/* ================================= */}
              {/* FACE TAMPERING */}
              {/* ================================= */}

              <div className="result-card">

                <h4>Face Tampering</h4>

                <p>
                  Score:
                  {results.modules.face_tamper.score}
                </p>

                <p>
                  Verdict:
                  {results.modules.face_tamper.verdict}
                </p>

                <div className="image-grid">

                  <div>

                    <h5>Detected Face Regions</h5>

                    <img
                      src={`http://localhost:8000${results.modules.face_tamper.images.visualization}`}
                      alt=""
                    />

                  </div>

                </div>

              </div>

            </div>
          )}

        </div>

      </div>

    </div>
  );
}