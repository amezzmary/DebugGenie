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

import streamlit as st

def render_file_information(filename, language="Python"):
    st.markdown(f"**File:** `{filename}` | **Language:** `{language}`")

def render_success_result(result=None):
    st.success("🎉 Code compiled and executed successfully! No errors detected.")

def render_error_result(result=None, suggestion=""):
    st.error("❌ Errors detected during execution/analysis.")
    if isinstance(result, dict):
        err_type = result.get("error_type", result.get("type", "Error"))
        err_msg = result.get("error_message", result.get("message", "Unknown error"))
        err_line = result.get("error_line", result.get("line", "N/A"))
        
        st.markdown(f"**Error Type:** `{err_type}`")
        st.markdown(f"**Error Message:** `{err_msg}`")
        st.markdown(f"**Line Number:** `{err_line}`")
        
    if suggestion:
        st.info(f"**Suggestion:** {suggestion}")

def render_ai_analysis(ai_help=""):
    st.subheader("🤖 AI Debugging Analysis")
    st.write(ai_help)

def render_submitted_code(code="", language="Python"):
    st.subheader("📄 Submitted Code")
    st.code(code, language=str(language).lower())


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