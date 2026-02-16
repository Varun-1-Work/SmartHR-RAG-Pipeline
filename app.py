# This will act as your "Frontend" and talk to your FastAPI backend using the requests library.

import streamlit as st
import requests

st.set_page_config(page_title="Smart HR Screener", layout="wide")

st.title("🤖 Smart HR Resume Screener")
st.markdown("Upload multiple resumes and find the best candidates using AI.")

# 1. Sidebar for Uploads
with st.sidebar:
    st.header("Upload Center")
    uploaded_files = st.file_uploader("Choose PDF Resumes", accept_multiple_files=True, type="pdf")
    
    if st.button("Index Resumes"):
        if uploaded_files:
            for file in uploaded_files:
                files = {"files": (file.name, file.getvalue(), "application/pdf")}
                # Change the URL to match your FastAPI upload endpoint
                response = requests.post("http://127.0.0.1:8000/upload-resumes/", files=files)
            st.success("✅ Resumes indexed successfully!")
        else:
            st.warning("Please select files first.")

# 2. Main Search Area
st.header("🔍 Search Candidates")
jd = st.text_area("Paste the Job Description here:", height=200)

if st.button("Rank Candidates"):
    if jd:
        with st.spinner("AI is analyzing resumes..."):
            # Call your FastAPI search endpoint
            response = requests.post(f"http://127.0.0.1:8000/search/?job_description={jd}")
            results = response.json().get("best_matches", [])
            
            if results:
                st.subheader("Top Matches found:")
                for i, match in enumerate(results):
                    with st.expander(f"Rank #{i+1} - AI Analysis", expanded=True):
                        st.markdown(match)
            else:
                st.error("No matches found.")