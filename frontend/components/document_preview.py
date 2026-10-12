import requests
import streamlit as st
from utils.helpers import extract_text_from_file, highlight_keywords

API_URL = "http://127.0.0.1:8000/predict"

def render_document_preview():
    st.subheader("1. Document Input & Ingestion")

    uploaded_file = st.file_uploader(
        "Upload Contract Document",
        type=["pdf", "docx", "txt"],
        help="Supported formats: PDF, DOCX, TXT (Max 200MB)"
    )

    if uploaded_file is not None and uploaded_file.name != st.session_state.uploaded_filename:
        try:
            st.session_state.contract_text = extract_text_from_file(uploaded_file)
            st.session_state.uploaded_filename = uploaded_file.name
            st.session_state.results = None
            st.rerun()
        except Exception as e:
            st.error(f"Error parsing uploaded file: {str(e)}")

    st.session_state.contract_text = st.text_area(
        "Extracted Contract Text",
        value=st.session_state.contract_text,
        height=220,
        placeholder="Extracted contract text will appear here...",
        help="Editable text area containing the full contract content for model ingestion."
    )

    # Dynamic Analysis State CTAs
    if st.session_state.is_analyzing:
        st.button("Analyzing Contract...", disabled=True, type="primary", width='stretch')
    elif st.session_state.results is not None:
        if st.button("Re-analyze Contract", type="primary", width='stretch'):
            trigger_analysis()
    else:
        if st.button("Analyze Contract", type="primary", width='stretch'):
            trigger_analysis()

    if st.session_state.contract_text:
        st.markdown("##### Document Reader Preview")
        active_clause = st.session_state.get("active_clause_text", "")
        
        display_content = st.session_state.contract_text
        if active_clause:
            # Highlight selected active clause in document preview
            display_content = display_content.replace(active_clause, f"<mark class='keyword-highlight'>{active_clause}</mark>")
        
        st.markdown(
            f"<div class='document-preview-box'>{display_content}</div>",
            unsafe_allow_html=True
        )

def trigger_analysis():
    if not st.session_state.contract_text.strip():
        st.warning("Please upload or enter contract text before initiating analysis.")
        return

    st.session_state.is_analyzing = True
    try:
        resp = requests.post(API_URL, json={"text": st.session_state.contract_text}, timeout=120)
        if resp.status_code == 200:
            st.session_state.results = resp.json()["results"]
            st.success("Analysis completed successfully!")
        else:
            st.error(f"Backend API returned error code: {resp.status_code}")
    except requests.exceptions.ConnectionError:
        st.error("Could not reach FastAPI inference server on port 8000.")
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
    finally:
        st.session_state.is_analyzing = False
        st.rerun()