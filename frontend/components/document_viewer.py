import streamlit as st
from utils.helpers import highlight_keywords

def render_document_viewer():
    st.title("Document Viewer")
    st.caption("Full contract text reader with active clause cross-referencing.")

    if not st.session_state.contract_text.strip():
        st.info("No active document loaded. Upload or paste a contract on the Dashboard.")
        return

    st.markdown(f"**Document Name:** `{st.session_state.uploaded_filename or 'Pasted Text Document'}`")

    doc_search = st.text_input("Search Document Text", placeholder="Type keywords to locate in text...")

    content = st.session_state.contract_text
    if doc_search.strip():
        content = highlight_keywords(content)

    st.markdown("##### Full Document Text")
    st.markdown(
        f"<div class='document-preview-box'>{content}</div>",
        unsafe_allow_html=True
    )