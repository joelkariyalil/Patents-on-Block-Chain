import { BrowserProvider, Contract } from "ethers";
import React, { useState } from "react";

const CONTRACT_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3";
const ABI = [
  {
    inputs: [
      { internalType: "string", name: "cid", type: "string" },
      { internalType: "uint256", name: "score", type: "uint256" },
      { internalType: "string", name: "decision", type: "string" }
    ],
    name: "storeResult",
    outputs: [],
    stateMutability: "nonpayable",
    type: "function"
  }
];

export default function MetaMaskSubmit({ cid, score, decision }) {
  const [account, setAccount] = useState(null);
  const [status, setStatus] = useState("");

  const connectWallet = async () => {
    try {
      if (!window.ethereum) {
        setStatus("❌ MetaMask not detected");
        return;
      }
      const provider = new BrowserProvider(window.ethereum);
      const signer = await provider.getSigner();
      const userAddress = await signer.getAddress();
      setAccount(userAddress);
      setStatus(`🚀 Connected: ${userAddress}`);
    } catch (err) {
      setStatus(`❌ Wallet connection failed: ${err.message}`);
    }
  };

  const submitToBlockchain = async () => {
    try {
      if (!account) {
        setStatus("⚠️ Please connect wallet first.");
        return;
      }

      const provider = new BrowserProvider(window.ethereum);
      const signer = await provider.getSigner();
      const contract = new Contract(CONTRACT_ADDRESS, ABI, signer);
      const tx = await contract.storeResult(cid, Math.floor(score), decision);
      setStatus(`⏳ Waiting for transaction: ${tx.hash}`);
      await tx.wait();
      setStatus(`✅ Success! TX Hash: ${tx.hash}`);
    } catch (e) {
      if (e.message.includes("CID already recorded")) {
        setStatus("🛑 Nerd! You stealing this Patent? Better move out!");
      } else {
        setStatus(`❌ Error: You can't upload this Patent, Sorry`);
      }      
    }
  };

  return (
    <div style={{
      marginTop: "2rem",
      padding: "1.5rem",
      borderRadius: "10px",
      border: "1px solid #e0e0e0",
      background: "#fafafa",
      boxShadow: "0 2px 8px rgba(0,0,0,0.05)",
      fontFamily: "Segoe UI, sans-serif"
    }}>
      <h3 style={{ color: "#333" }}>🦊 MetaMask Blockchain Submission</h3>
      <p><strong>🧾 CID:</strong> <code>{typeof cid === "string" ? cid : JSON.stringify(cid)}</code></p>
      <p><strong>📌 Decision:</strong> {decision}</p>
      <div style={{ marginTop: "1rem" }}>
        <button
          onClick={connectWallet}
          style={{ padding: "0.5rem 1.2rem", background: "#f6851b", color: "white", border: "none", borderRadius: "6px", cursor: "pointer" }}
        >
          Connect Wallet
        </button>
        <button
          onClick={submitToBlockchain}
          disabled={!account}
          style={{
            marginLeft: "1rem",
            padding: "0.5rem 1.2rem",
            background: account ? "#0070f3" : "#ccc",
            color: "white",
            border: "none",
            borderRadius: "6px",
            cursor: account ? "pointer" : "not-allowed"
          }}
        >
          Submit to Blockchain
        </button>
      </div>

      {status && (
        <div style={{
          marginTop: "1rem",
          padding: "0.75rem",
          backgroundColor: status.startsWith("✅") ? "#e6ffed" :
                           status.startsWith("❌") ? "#ffe6e6" :
                           status.startsWith("⏳") ? "#f0f4ff" : "#f9f9f9",
          border: "1px solid #ddd",
          borderRadius: "8px",
          maxHeight: "150px",
          overflowY: "auto",
          whiteSpace: "pre-wrap",
          wordBreak: "break-word",
          fontSize: "0.9rem",
          color: "#333"
        }}>
          {status}
        </div>
      )}
    </div>
  );
}
