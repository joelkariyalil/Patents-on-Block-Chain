import streamlit as st
import time

# ---- Page Config ----
st.set_page_config(page_title="📜 Patents on Blockchain", page_icon="📄", layout="centered")

# ---- Light Background Styling ----
st.markdown("""
    <style>
        body, .main {
            background-color: #f8f9fa !important;
        }
        .metric-card {
            background-color: white;
            padding: 1rem;
            border-radius: 12px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
            text-align: center;
        }
        .metric-title {
            font-size: 1rem;
            color: #666;
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: 700;
            margin-top: 0.2rem;
        }
    </style>
""", unsafe_allow_html=True)

# ---- Title ----
st.title("📜 Patents on BlockChain")
st.caption("Secure. Transparent. Immutable.")

# ---- Metric Dashboard (Simple Card Style) ----
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
        <div class="metric-card">
            <div class="metric-title">📄 Total Patents</div>
            <div class="metric-value">128</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="metric-card">
            <div class="metric-title">🧬 Unique Submissions</div>
            <div class="metric-value">122</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="metric-card">
            <div class="metric-title">⏳ Pending Approvals</div>
            <div class="metric-value">6</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ---- Region Selection ----
st.subheader("🌍 Choose Region")
region = st.selectbox(
    "Choose your region for patent filing",
    ["North America", "Europe", "Asia", "South America", "Africa", "Australia"],
    index=1
)

# ---- File Upload ----
st.subheader("📁 Upload Patent Document")
uploaded_file = st.file_uploader("Choose your file (.pdf, .txt, .json)", type=["pdf", "txt", "json"])

# ---- AI & Blockchain State ----
prediction_ready = False
ai_prediction = None
reviewer_approved = False

if uploaded_file:
    st.success(f"✅ Uploaded `{uploaded_file.name}` successfully.")
    if uploaded_file.type.startswith("text"):
        content = uploaded_file.read().decode("utf-8")
        with st.expander("📄 Preview Text Content"):
            st.text_area("Preview", content, height=300)
    else:
        content = None
        st.info("ℹ️ Preview not available for this file type.")

    # ---- AI Submission ----
    if st.button("🔍 Submit to AI"):
        with st.spinner("🤖 AI is reviewing your submission..."):
            progress = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress.progress(i + 1)
            time.sleep(0.3)

        # 📍 Replace with actual AI call
        ai_prediction = {
            "category": "🌿 BioTech Innovation",
            "novelty_score": 91,
            "recommended_action": "✅ Approve"
        }
        prediction_ready = True
        st.balloons()

# ---- Display AI Results ----
if prediction_ready and ai_prediction:
    st.markdown("---")
    st.subheader("🧠 AI Review Outcome")
    st.write(f"**📂 Category:** {ai_prediction['category']}")
    st.write(f"**📊 Novelty Score:** {ai_prediction['novelty_score']}%")
    st.write(f"**📌 Recommendation:** {ai_prediction['recommended_action']}")

    # ---- Reviewer Manual Approval ----
    reviewer_approved = st.checkbox("✅ I approve this patent for blockchain submission")

    # ---- Final Blockchain Push ----
    if reviewer_approved:
        if st.button("🚀 Push to Blockchain"):
            with st.spinner("🔗 Uploading to Blockchain..."):
                time.sleep(2)

                # 📍 Replace with actual blockchain submission
                # e.g. requests.post("...", json={...})

            st.success("🎉 Patent successfully pushed to the blockchain.")
            st.snow()
    else:
        st.warning("⚠️ Please approve the submission before pushing to blockchain.")
