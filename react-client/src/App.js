import axios from "axios";
import React, { useState } from "react";
import MetaMaskSubmit from "./components/MetaMaskSubmit";

const BACKEND_URL = "http://localhost:8000";

export default function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [cid, setCid] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => setFile(e.target.files[0]);

  const handleEvaluate = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await axios.post(`${BACKEND_URL}/upload/`, formData);
      setResult(res.data);
    } catch (err) {
      console.error("❌ Error evaluating document:", err);
      alert("Error evaluating document. Make sure FastAPI is running at http://localhost:8000");
    } finally {
      setLoading(false);
    }
  };

  const handleUploadToIPFS = async () => {
    try {
      const res = await axios.post(`${BACKEND_URL}/upload_ipfs/`, result);
      const ipfsCid = res.data?.cid;
      if (!ipfsCid || typeof ipfsCid !== "string") {
        throw new Error("❗ Unexpected CID format received from backend");
      }
      console.log("✅ IPFS CID received:", ipfsCid);
      setCid(ipfsCid);
    } catch (err) {
      console.error("❌ Failed to upload to IPFS:", err);
      alert("Failed to upload to IPFS: " + err.message);
    }
  };

  return (
    <div style={{
      background: "linear-gradient(135deg, #d3dce6, #a6b4c7)",
      minHeight: "100vh",
      padding: "2rem",
      fontFamily: "'Poppins', sans-serif"
    }}>
      <div style={{
        background: "rgba(255, 255, 255, 0.25)",
        boxShadow: "0 8px 32px 0 rgba(31, 38, 135, 0.2)",
        backdropFilter: "blur(10px)",
        borderRadius: "20px",
        padding: "2rem",
        maxWidth: "600px",
        margin: "3rem auto",
        color: "#1a1a1a"
      }}>
        <h1 style={{ textAlign: "center", marginBottom: "1rem" }}>🔍 <span style={{ fontWeight: 600 }}>PatentAI</span></h1>
        <p style={{ textAlign: "center", fontSize: "0.95rem", marginBottom: "2rem", color: "#444" }}>
          Validate novelty before filing — For the <strong>United States Patent Office (USPTO)</strong> 📁
        </p>

        <label style={{ fontWeight: "600", display: "block", marginBottom: "0.5rem" }}>
          📄 Upload Patent Document:
        </label>
        <input type="file" onChange={handleFileChange} accept=".pdf" style={{
          border: "1px solid #ddd",
          borderRadius: "8px",
          padding: "0.4rem",
          width: "100%",
          marginBottom: "1rem"
        }} />

        <div style={{ textAlign: "center", marginTop: "1.5rem" }}>
          <button onClick={handleEvaluate} disabled={loading} style={{
            background: "linear-gradient(to right, #667eea, #764ba2)",
            color: "white",
            padding: "0.6rem 1.4rem",
            borderRadius: "8px",
            border: "none",
            cursor: "pointer",
            transition: "0.3s"
          }}>
            {loading ? "Evaluating..." : "Click to evaluate with our Agent AI"}
          </button>
        </div>

        {result && (
          <div style={{ marginTop: "2rem" }}>
            <h3 style={{ fontSize: "1.2rem" }}>📊 <strong>Evaluation Result</strong></h3>
            <p><strong>📌 Decision:</strong> {result.is_unique ? "✅ Unique" : "❌ Not Unique"}</p>
            <p><strong>📉 Similarity Score:</strong> {((1.0 - Math.min(1.0, result.uniqueness_score))* 100).toFixed(2)}%</p>
            <p><strong>🤖 LLM Judgment:</strong></p>
            <pre>{
              result.agent_judgment?.trim() === "(a)"
                ? "(a) Clearly novel"
                : result.agent_judgment?.trim() === "(b)"
                ? "(b) An obvious modification"
                : result.agent_judgment?.trim() === "(c)"
                ? "(c) Possibly plagiarized"
                : result.agent_judgment
            }</pre>

            {result.is_unique && (
              <>
                <div style={{ textAlign: "center" }}>
                  <button onClick={handleUploadToIPFS} style={{
                    marginTop: "1rem",
                    background: "#222",
                    color: "white",
                    padding: "0.6rem 1.4rem",
                    borderRadius: "8px",
                    border: "none",
                    cursor: "pointer"
                  }}>
                    Upload Result to IPFS
                  </button>
                </div>
                {typeof cid === "string" && (
                  <>
                    <p style={{ marginTop: "1rem" }}>✅ Uploaded to IPFS. CID: <code>{cid}</code></p>
                    <MetaMaskSubmit
                      cid={cid}
                      score={result.uniqueness_score}
                      decision="Unique"
                    />
                  </>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
