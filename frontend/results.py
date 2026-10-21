
import streamlit as st


def show_results():
    st.title("🔍 Debugging Results")
    st.divider()

    result = st.session_state.get("analysis_result")
    code = st.session_state.get("analysis_code", "")

    # Use the language selected during analysis.
    language = st.session_state.get(
        "analysis_language", "Python"
    )

    language_map = {
        "python": "python",
        "c": "c",
        "c++": "cpp",
        "cpp": "cpp",
        "java": "java",
        "javascript": "javascript",
        "js": "javascript",
    }

    display_language = language_map.get(
        str(language).lower(), "text"
    )

    if result is None:
        st.warning("No analysis result available.")

        if st.button("← Back to Dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()

        return

    if not isinstance(result, dict):
        st.write(result)
    else:
        success = result.get("success", False)

        if success:
            st.success("✅ No errors found!")
        else:
            st.error("❌ Errors detected")

        error_type = result.get("error_type")
        error_line = result.get("error_line")
        error_message = result.get("error_message")
        suggestion = result.get("suggestion")

        if error_type:
            st.subheader("Error Type")
            st.code(str(error_type), language="text")

        if error_line is not None:
            st.subheader("Error Line")
            st.write(error_line)

        if error_message:
            st.subheader("Error Message")
            st.code(str(error_message), language="text")

        if suggestion:
            st.subheader("Suggestion")
            st.info(suggestion)

        # Display AI analysis when supplied by the backend.
        ai_sections = [
            ("ai_explanation", "🤖 AI Error Explanation"),
            ("error_explanation", "🤖 AI Error Explanation"),
            ("why_it_happened", "Why Did It Happen?"),
            ("how_to_fix", "How to Fix It"),
            ("ai_suggestion", "AI Suggestion"),
        ]

        displayed_sections = set()

        for key, heading in ai_sections:
            value = result.get(key)

            if value and key not in displayed_sections:
                st.subheader(heading)
                st.markdown(str(value))
                displayed_sections.add(key)

        # Support an AI analysis returned as a single text field.
        ai_analysis = result.get("ai_analysis")

        if ai_analysis:
            st.subheader("🤖 AI Debugging Analysis")
            st.markdown(str(ai_analysis))

        corrected_code = result.get("corrected_code")

        if corrected_code:
            st.subheader("✅ Corrected Code")
            st.code(str(corrected_code), language=display_language)

            st.download_button(
                "Download Corrected Code",
                data=str(corrected_code),
                file_name=f"corrected_code.{{
                    'python': 'py',
                    'c': 'c',
                    'c++': 'cpp',
                    'cpp': 'cpp',
                    'java': 'java',
                    'javascript': 'js',
                    'js': 'js',
                }}.get(str(language).lower(), 'txt')}",
                mime="text/plain",
                use_container_width=True,
            )

    st.divider()
    st.subheader("Analyzed Code")

    st.code(
        code if code else "No code available.",
        language=display_language
    )

    st.divider()

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
