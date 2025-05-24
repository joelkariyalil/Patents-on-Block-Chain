import requests
import streamlit as st
import os
import base64
import urllib.parse
import webbrowser

# BACKEND URLS
EVALUATE_URL = "http://localhost:8000/upload/"
IPFS_UPLOAD_URL = "http://localhost:8000/upload_ipfs/"

st.title("📜 Patent Uniqueness Verifier")

uploaded_file = st.file_uploader("Upload Your Patent Document", type=["pdf", "txt", "json"])

if uploaded_file is not None:
    st.success("File uploaded successfully!")
    st.write("**Filename:**", uploaded_file.name)

    region = st.selectbox(
        "Choose Your Region",
        ["North America", "Europe", "Asia", "South America", "Africa", "Australia"],
        index=1
    )
    st.write("**Selected Region:**", region)

    # Send to backend for evaluation
    files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
    with st.spinner("Evaluating document..."):
        res = requests.post(EVALUATE_URL, files=files)

    if res.status_code == 200:
        result = res.json()
        st.subheader("📊 Evaluation Result")

        # Show score & reasoning
        st.write(f"**Score:** {result['uniqueness_score']:.4f}")
        st.write(f"**Decision:** {'✅ Unique' if result['is_unique'] else '❌ Not Unique'}")
        st.text_area("LLM Judgment", result["agent_judgment"], height=200)

        # Save globally
        st.session_state["result"] = result

        # --- Only allow IPFS upload if it's unique ---
        if result["is_unique"]:
            if st.button("Upload Result to IPFS"):
                with st.spinner("Uploading to IPFS..."):
                    ipfs_res = requests.post(IPFS_UPLOAD_URL, json=result)
                if ipfs_res.status_code == 200:
                    cid = ipfs_res.json()["cid"]
                    st.session_state["cid"] = cid
                    st.success(f"Uploaded to IPFS ✅ CID: {cid}")
                    st.write(f"🔗 [View on IPFS](https://gateway.pinata.cloud/ipfs/{cid}/result.json)")
                else:
                    st.error(f"IPFS upload failed. Status: {ipfs_res.status_code}, Response: {ipfs_res.text}")

        else:
            st.warning("This document is **not unique enough** to be stored on-chain.")

    else:
        st.error("Backend evaluation failed: " + res.text)

# --- Blockchain Submission via MetaMask ---
if "cid" in st.session_state and "result" in st.session_state:
    st.subheader("🦊 Smart Contract Recording (MetaMask)")
    result = st.session_state["result"]
    cid_dict = st.session_state["cid"]
    cid = cid_dict["cid"] if isinstance(cid_dict, dict) else cid_dict

    score = result["uniqueness_score"]
    decision = "Unique"

    # Absolute path to the local HTML file
    file_path = os.path.abspath("../static/metamask_ui.html")
    params = urllib.parse.urlencode({"cid": cid, "score": score, "decision": decision})
    file_url = f"http://localhost:5500/metamask_ui.html?{params}"


    if st.button("🦊 Open MetaMask Submission Page"):
        webbrowser.open_new_tab(file_url)
