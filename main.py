import streamlit as st
import time
from pypdf import PdfReader
import requests as request
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io

# ---- Convert text to PDF ----
def convert_text_to_pdf(text: str) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 40
    for line in text.splitlines():
        c.drawString(40, y, line[:1000])  # truncate long lines
        y -= 15
        if y < 40:
            c.showPage()
            y = height - 40
    c.save()
    buffer.seek(0)
    return buffer.read()

# ---- Page Config ----
st.set_page_config(page_title="📜 Patents on Blockchain", page_icon="📄", layout="centered")

# ---- Styling ----
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

# ---- Metrics ----
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""<div class="metric-card"><div class="metric-title">📄 Total Patents</div><div class="metric-value">128</div></div>""", unsafe_allow_html=True)
with col2:
    st.markdown("""<div class="metric-card"><div class="metric-title">🧬 Unique Submissions</div><div class="metric-value">122</div></div>""", unsafe_allow_html=True)
with col3:
    st.markdown("""<div class="metric-card"><div class="metric-title">⏳ Pending Approvals</div><div class="metric-value">6</div></div>""", unsafe_allow_html=True)

st.markdown("---")

# ---- Region ----
st.subheader("🌍 Choose Region")
region = st.selectbox("Choose your region for patent filing", ["North America", "Europe", "Asia", "South America", "Africa", "Australia"], index=1)

# ---- Upload ----
st.subheader("📁 Upload Patent Document")
uploaded_file = st.file_uploader("Choose your file (.pdf, .txt, .json)", type=["pdf", "txt", "json"])

prediction_ready = False
ai_prediction = None
reviewer_approved = False

st.markdown("---")

if uploaded_file:
    st.success(f"✅ Uploaded `{uploaded_file.name}` successfully.")
    file_text = ""

    if uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                file_text += text + "\n"
        if file_text.strip():
            with st.expander("📄 Preview PDF Content"):
                st.text_area("PDF Preview", file_text.strip(), height=300)
        else:
            st.warning("⚠️ No extractable text found in PDF.")

    elif uploaded_file.type.startswith("text") or uploaded_file.type == "application/json":
        file_text = uploaded_file.read().decode("utf-8")
        with st.expander("📄 Preview Text Content"):
            st.text_area("Text Preview", file_text.strip(), height=300)

    else:
        st.info("ℹ️ Preview not available for this file type.")

    # ---- AI Submission ----
    if st.button("🔍 Submit to AI"):
        with st.spinner("🤖 AI is reviewing your submission..."):
            # Convert to PDF bytes in memory
            pdf_bytes = convert_text_to_pdf(file_text)

            # Simulate progress
            progress = st.progress(0)
            for i in range(100):
                time.sleep(0.005)
                progress.progress(i + 1)
            time.sleep(0.3)

            try:
                files = {
                    "file": ("converted_text.pdf", pdf_bytes, "application/pdf")
                }

                # Send to ai-agent container on Docker network
                res = request.post("http://ai-agent:8000/upload", files=files)
                res.raise_for_status()
                response_json = res.json()

                # Format AI response
                ai_prediction = {
                    "category": "🧠 LLM Judgment",
                    "novelty_score": round((1 - response_json['matched_patent']['similarity_score']) * 100, 2),
                    "recommended_action": "✅ Approve" if response_json["is_unique"] else "⚠️ Needs Review"
                }
                prediction_ready = True
                st.balloons()

            except Exception as e:
                st.error(f"❌ AI agent failed: {str(e)}")

# ---- AI Results ----
if prediction_ready and ai_prediction:
    st.markdown("---")
    st.subheader("🧠 AI Review Outcome")
    st.write(f"**📂 Category:** {ai_prediction['category']}")
    st.write(f"**📊 Novelty Score:** {ai_prediction['novelty_score']}%")
    st.write(f"**📌 Recommendation:** {ai_prediction['recommended_action']}")

    reviewer_approved = st.checkbox("✅ I approve this patent for blockchain submission")

    if reviewer_approved:
        if st.button("🚀 Push to Blockchain"):
            with st.spinner("🔗 Uploading to Blockchain..."):
                time.sleep(2)
                # Place actual blockchain logic here if needed
            st.success("🎉 Patent successfully pushed to the blockchain.")
            st.snow()
    else:
        st.warning("⚠️ Please approve the submission before pushing to blockchain.")
