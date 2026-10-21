import streamlit as st
from pathlib import Path

def show_home():

    # =========================
    # GLOBAL STYLING
    # =========================
    st.markdown(
        """
        <style>
        /* Force App Background */
        .stApp {
            background-color: #F3E8FF !important;
        }

        /* Base Typography Colors */
        .stApp p, .stApp label, .stApp span, .stApp div {
            color: #3B0764 !important;
        }

        /* Headings Specific Colors */
        h1, h2, h3, [data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2, [data-testid="stMarkdownContainer"] h3 {
            color: #2D064E !important;
            font-weight: 800 !important;
        }

        /* Secondary Headings / Subtitles */
        h4, h5, h6, [data-testid="stMarkdownContainer"] h4 {
            color: #581C87 !important;
        }

        /* Muted / Accent Subtext */
        .muted-purple {
            color: #7E22CE !important;
            font-weight: 600;
        }
        
        /* Captions */
        .stCaption {
            color: #6B21A8 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # =========================
    # HEADER
    # =========================

    col1, col2, col3 = st.columns([2.5, 3, 2])

    with col1:
        st.markdown("<h2 style='color: #2D064E;'>🐞 DebugGenie</h2>", unsafe_allow_html=True)

    with col2:

        n1, n2, n3 = st.columns(3)

        with n1:
            if st.button("Home", key="home_button"):
                st.session_state.page = "home"
                st.rerun()

        with n2:
            if st.button("Features", key="features_button"):
                st.session_state.scroll_features = True

        with n3:
            if st.button("About", key="about_button"):
                st.session_state.scroll_about = True

    with col3:

        l1, l2 = st.columns(2)

        with l1:
            if st.button(
                "Login",
                key="header_login",
                use_container_width=True
            ):
                st.session_state.page = "login"
                st.rerun()

        with l2:
            if st.button(
                "Sign Up",
                key="header_signup",
                use_container_width=True
            ):
                st.session_state.page = "register"
                st.rerun()

    st.divider()

    
    # =========================
    # HERO SECTION
    # =========================

    st.write("")
    lamp_path = Path(__file__).resolve().parent / "assets" / "genie_lamp.png"

    image_col, content_col = st.columns([2, 3], gap="large")

    with image_col:
        if lamp_path.exists():
            st.image(str(lamp_path), use_container_width=True)
        else:
            st.info("Add genie_lamp.png to the assets folder.")

    with content_col:
        st.markdown("<p class='muted-purple'>✨ <b>Powered by LLM Intelligence</b></p>", unsafe_allow_html=True)

        st.markdown("<h1 style='color: #2D064E;'>Your AI Pair Programmer for Smarter Debugging</h1>", unsafe_allow_html=True)

        st.markdown(
            "<p style='color: #581C87;'>DebugGenie helps you identify errors, "
            "understand your code and find intelligent solutions faster.</p>",
            unsafe_allow_html=True
        )

        st.write("")

        if st.button(
            "Start Debugging →",
            key="start_debugging",
            use_container_width=True
        ):
            st.session_state.page = "login"
            st.rerun()

        if st.button(
            "Explore Features",
            key="explore_features",
            use_container_width=True
        ):
            st.session_state.scroll_features = True


    # =========================
    # FEATURES
    # =========================

    st.markdown("<h4 class='muted-purple'>POWERFUL FEATURES</h4>", unsafe_allow_html=True)

    st.markdown("<h1 style='color: #2D064E;'>Everything you need to debug better</h1>", unsafe_allow_html=True)

    st.markdown(
        "<p style='color: #581C87;'>Intelligent tools designed to make your coding and debugging experience easier.</p>",
        unsafe_allow_html=True
    )

    st.write("")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("<h3 style='color: #3B0764;'>💻 Multi-Language</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #581C87;'>Analyze and debug code written in multiple programming languages.</p>", unsafe_allow_html=True)

    with c2:
        st.markdown("<h3 style='color: #3B0764;'>🔍 Deep Analysis</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #581C87;'>Detect programming errors with detailed analysis.</p>", unsafe_allow_html=True)

    with c3:
        st.markdown("<h3 style='color: #3B0764;'>✨ LLM Insights</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #581C87;'>Get AI-powered explanations and intelligent suggestions.</p>", unsafe_allow_html=True)

    st.write("")

    c4, c5, c6 = st.columns(3)

    with c4:
        st.markdown("<h3 style='color: #3B0764;'>📊 Reports</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #581C87;'>Understand your debugging results through clear reports.</p>", unsafe_allow_html=True)

    with c5:
        st.markdown("<h3 style='color: #3B0764;'>🕘 History</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #581C87;'>Keep track of your previous debugging sessions.</p>", unsafe_allow_html=True)

    with c6:
        st.markdown("<h3 style='color: #3B0764;'>🔒 Secure & Private</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #581C87;'>Your code and debugging history are handled securely.</p>", unsafe_allow_html=True)

    st.write("")
    st.write("")

    # =========================
    # ABOUT
    # =========================

    st.markdown("<h4 class='muted-purple'>ABOUT DEBUGGENIE</h4>", unsafe_allow_html=True)

    st.markdown("<h1 style='color: #2D064E;'>Debug Smarter. Code Better. Ship Faster.</h1>", unsafe_allow_html=True)

    st.markdown(
        """
        <p style='color: #581C87;'>
        DebugGenie is an AI-powered code debugging assistant designed to help developers 
        understand errors, analyze code and solve programming problems more efficiently.
        </p>
        """,
        unsafe_allow_html=True
    )

    st.write("")
    st.divider()

    # =========================
    # FOOTER
    # =========================

    st.caption("DebugGenie — AI-Powered Code Debugging Assistant")