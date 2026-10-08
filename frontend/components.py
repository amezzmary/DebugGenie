import streamlit as st


# ============================================================
# FOOTER
# ============================================================

def render_footer():
    st.markdown(
        """
        <div style="
            text-align:center;
            padding:30px 10px 15px 10px;
            color:#777;
            font-size:13px;
        ">
            DebugGenie • AI-Powered Code Debugging Assistant
            <br>
            Debug Smarter. Code Better. Ship Faster.
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# FILE INFORMATION
# ============================================================

def render_file_information(filename, language):
    st.markdown("### 📄 File Information")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**File:**")
        st.write(filename if filename else "Pasted Code")

    with col2:
        st.write("**Language:**")
        st.write(language)


# ============================================================
# SUCCESS RESULT
# ============================================================

def render_success_result(message):
    st.success("✅ No Error Detected")

    st.markdown("### Analysis Result")

    st.info(
        message if message else
        "No syntax or undefined-variable errors were detected."
    )


# ============================================================
# ERROR RESULT
# ============================================================

def render_error_result(
    error_type,
    line,
    message,
    code="",
    suggestion=""
):
    st.error("❌ Error Detected")

    st.markdown("### Error Details")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Error Type**")
        st.code(str(error_type))

    with col2:
        st.write("**Line**")
        st.code(str(line))

    st.write("**Error Message**")

    st.error(
        message if message else "An error was detected."
    )

    if suggestion:
        st.markdown("### 💡 Suggestion")
        st.info(suggestion)


# ============================================================
# AI ANALYSIS
# ============================================================

def render_ai_analysis(ai_help):
    st.markdown("### 🤖 AI Debugging Analysis")

    if ai_help:
        st.markdown(ai_help)
    else:
        st.info(
            "Gemini AI analysis is not available for this analysis."
        )


# ============================================================
# SUBMITTED CODE
# ============================================================

def render_submitted_code(code):
    st.markdown("### 💻 Submitted Code")

    if code:
        st.code(code, language="python")
    else:
        st.info("No code was submitted.")


# ============================================================
# EMPTY STATE
# ============================================================

def render_empty_state(
    title="No Analysis Yet",
    message="Submit Python code to start debugging."
):
    st.info(f"### {title}\n\n{message}")


# ============================================================
# USER HISTORY ITEM
# ============================================================

def render_user_history_item(item):
    with st.expander(
        f"📄 {item.get('file_name', 'Pasted Code')} "
        f"• {item.get('analyzed_at', '')}"
    ):
        success = item.get("success", False)

        if success:
            st.success("✅ No Error Detected")
        else:
            st.error(
                f"❌ {item.get('error_type', 'Error')}"
            )

        st.write(
            f"**Language:** "
            f"{item.get('language', 'Python')}"
        )

        if not success:
            st.write(
                f"**Line:** "
                f"{item.get('error_line', 'Unknown')}"
            )

            st.write(
                f"**Message:** "
                f"{item.get('error_message', '')}"
            )

            if item.get("suggestion"):
                st.info(
                    f"💡 {item.get('suggestion')}"
                )

        if item.get("code"):
            st.code(
                item.get("code"),
                language="python"
            )


# ============================================================
# ADMIN HISTORY ITEM
# ============================================================

def render_admin_history_item(item):
    with st.expander(
        f"👤 {item.get('user_email', 'Unknown User')} "
        f"• {item.get('file_name', 'Pasted Code')} "
        f"• {item.get('analyzed_at', '')}"
    ):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.write("**User**")
            st.write(
                item.get("user_email", "Unknown")
            )

        with col2:
            st.write("**Language**")
            st.write(
                item.get("language", "Python")
            )

        with col3:
            if item.get("success"):
                st.success("Success")
            else:
                st.error("Error")

        if not item.get("success"):
            st.write(
                "**Error Type:** "
                + str(item.get("error_type", ""))
            )

            st.write(
                "**Error Message:** "
                + str(item.get("error_message", ""))
            )

            st.write(
                "**Line:** "
                + str(item.get("error_line", ""))
            )

            if item.get("suggestion"):
                st.info(
                    "💡 " + str(item.get("suggestion"))
                )

        if item.get("code"):
            st.code(
                item.get("code"),
                language="python"
            )