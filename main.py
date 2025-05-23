import streamlit as st

# ---- Title ----
st.title("📜 Patents on BlockChain")

# ---- Display Metrics (Dummy Data) ----
col1, col2, col3 = st.columns(3)
col1.metric("Total Patents", "128")
col2.metric("Unique Submissions", "122")
col3.metric("Pending Approvals", "6")

st.markdown("---")

# ---- Region Selection ----
region = st.selectbox(
    "Choose Your Region",
    ["North America", "Europe", "Asia", "South America", "Africa", "Australia"],
    index=1
)

uploaded_file = st.file_uploader("Upload Your Patent Document", type=["pdf", "txt", "json"])

# ---- File Upload Section ----
if uploaded_file is not None:
    st.success("File uploaded successfully!")
    st.write("**Filename:**", uploaded_file.name)
    st.write("**Selected Region:**", region)

    # Optional: Display file content (if text)
    if uploaded_file.type.startswith("text"):
        content = uploaded_file.read().decode("utf-8")
        st.text_area("File Preview", content, height=300)
    else:
        st.info("Preview not available for this file type.")
