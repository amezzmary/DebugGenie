import streamlit as st


def show_results():

    st.title("🔍 Debugging Results")

    st.divider()

    result = st.session_state.get(
        "analysis_result",
        None
    )

    code = st.session_state.get(
        "analysis_code",
        ""
    )

    if result is None:

        st.warning(
            "No analysis result available."
        )

        if st.button("← Back to Dashboard"):

            st.session_state.page = "dashboard"
            st.rerun()

        return

    # =========================
    # RESULT
    # =========================

    if isinstance(result, dict):

        success = result.get(
            "success",
            False
        )

        if success:

            st.success(
                "✅ No errors found!"
            )

        else:

            st.error(
                "❌ Errors detected"
            )

        if result.get("error_type"):

            st.subheader("Error Type")

            st.write(
                result.get("error_type")
            )

        if result.get("error_message"):

            st.subheader("Error Message")

            st.write(
                result.get("error_message")
            )

        if result.get("error_line"):

            st.subheader("Error Line")

            st.write(
                result.get("error_line")
            )

        if result.get("suggestion"):

            st.subheader("Suggestion")

            st.info(
                result.get("suggestion")
            )

    else:

        st.write(result)

    # =========================
    # CODE
    # =========================

    st.subheader("Analyzed Code")

    st.code(
        code,
        language="python"
    )

    st.write("")

    # =========================
    # BUTTONS
    # =========================

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "🐞 Analyze Another Code",
            use_container_width=True
        ):

            st.session_state.page = "analyze"
            st.rerun()

    with col2:

        if st.button(
            "← Dashboard",
            use_container_width=True
        ):

            st.session_state.page = "dashboard"
            st.rerun()