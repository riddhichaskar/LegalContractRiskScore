import os
import streamlit as st
from components.sidebar import render_sidebar
from components.dashboard import render_dashboard
from components.document_viewer import render_document_viewer
from components.clause_inspector import render_clause_inspector
from components.analytics import render_analytics

# Page Configuration
st.set_page_config(
    page_title="Contract Risk Intelligence",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Duo-Tone CSS Stylesheet
css_path = os.path.join(os.path.dirname(__file__), "assets", "styles.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Session State Initialization
if "results" not in st.session_state:
    st.session_state.results = None

if "contract_text" not in st.session_state:
    st.session_state.contract_text = ""

if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = ""

if "selected_nav" not in st.session_state:
    st.session_state.selected_nav = "Dashboard"

def main():
    render_sidebar()
    route = st.session_state.selected_nav

    if route == "Dashboard":
        render_dashboard()
    elif route == "Document Viewer":
        render_document_viewer()
    elif route == "Clause Inspector":
        render_clause_inspector()
    elif route == "Advanced Analytics":
        render_analytics()

if __name__ == "__main__":
    main()