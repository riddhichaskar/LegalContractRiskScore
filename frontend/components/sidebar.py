import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.markdown("### ContractAI")
        st.caption("Legal Analytics & Risk Intelligence")
        st.write("")

        nav_options = [
            "Dashboard",
            "Document Viewer",
            "Clause Inspector",
            "Advanced Analytics"
        ]

        current_route = st.session_state.get("selected_nav", "Dashboard")
        if current_route not in nav_options:
            current_route = "Dashboard"

        route_index = nav_options.index(current_route)

        selection = st.radio(
            "Navigation Menu",
            nav_options,
            index=route_index,
            key="navigation_radio",
            label_visibility="collapsed"
        )

        if selection != st.session_state.selected_nav:
            st.session_state.selected_nav = selection
            st.rerun()

        st.markdown("---")
        st.caption("DOCUMENT STATUS")
        
        # State Synchronization
        if st.session_state.uploaded_filename and st.session_state.results is not None:
            st.markdown(f"🟢 **Active**  \n`{st.session_state.uploaded_filename}`")
            st.caption(f"{len(st.session_state.results)} clauses analyzed")
        elif st.session_state.contract_text.strip() and st.session_state.results is not None:
            st.markdown("🟢 **Active**  \nPasted Contract Text")
            st.caption(f"{len(st.session_state.results)} clauses analyzed")
        else:
            st.markdown("⚪ **No active document**")
            st.caption("Upload or submit text to begin.")