import streamlit as st


def show_home():

    # =========================
    # HEADER
    # =========================

    col1, col2, col3 = st.columns([2.5, 3, 2])

    with col1:
        st.markdown("## DebugGenie")

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

    st.markdown(
        "✨ **Powered by LLM Intelligence**"
    )

    st.title(
        "Your AI Pair Programmer for Smarter Debugging"
    )

    st.write(
        """
        DebugGenie helps you identify errors,
        understand your code and find intelligent
        solutions faster.
        """
    )

    st.write("")

    b1, b2 = st.columns(2)

    with b1:
        if st.button(
            "Start Debugging →",
            key="start_debugging",
            use_container_width=True
        ):
            st.session_state.page = "login"
            st.rerun()

    with b2:
        if st.button(
            "Explore Features",
            key="explore_features",
            use_container_width=True
        ):
            st.session_state.scroll_features = True

    st.write("")
    st.write("")

    # =========================
    # FEATURES
    # =========================

    st.subheader("POWERFUL FEATURES")

    st.title("Everything you need to debug better")

    st.write(
        "Intelligent tools designed to make your coding "
        "and debugging experience easier."
    )

    st.write("")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader("💻 Multi-Language")
        st.write(
            "Analyze and debug code written in "
            "multiple programming languages."
        )

    with c2:
        st.subheader("🔍 Deep Analysis")
        st.write(
            "Detect programming errors with "
            "detailed analysis."
        )

    with c3:
        st.subheader("✨ LLM Insights")
        st.write(
            "Get AI-powered explanations and "
            "intelligent suggestions."
        )

    st.write("")

    c4, c5, c6 = st.columns(3)

    with c4:
        st.subheader("📊 Reports")
        st.write(
            "Understand your debugging results "
            "through clear reports."
        )

    with c5:
        st.subheader("🕘 History")
        st.write(
            "Keep track of your previous "
            "debugging sessions."
        )

    with c6:
        st.subheader("🔒 Secure & Private")
        st.write(
            "Your code and debugging history "
            "are handled securely."
        )

    st.write("")
    st.write("")

    # =========================
    # ABOUT
    # =========================

    st.subheader("ABOUT DEBUGGENIE")

    st.title("Debug Smarter. Code Better. Ship Faster.")

    st.write(
        """
        DebugGenie is an AI-powered code debugging
        assistant designed to help developers
        understand errors, analyze code and solve
        programming problems more efficiently.
        """
    )

    st.write("")
    st.divider()

    # =========================
    # FOOTER
    # =========================

    st.caption(
        "DebugGenie — AI-Powered Code Debugging Assistant"
    )