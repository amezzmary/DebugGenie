import streamlit as st
import sqlite3
from datetime import datetime
from backend.c_debugger import check_c_code

# ==========================================
# DATABASE
# ==========================================

DB_PATH = "debuggenie.db"


def save_analysis_to_history(code, result):
    """
    Save the analysis result into analysis_history table.
    """

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Get logged-in user's information
        user_id = st.session_state.get("user_id")
        user_email = st.session_state.get("user_email", "")

        # Values from debugger result
        success = result.get("success", False)
        error_type = result.get("error_type")
        error_message = result.get("error_message")
        error_line = result.get("error_line")
        suggestion = result.get("suggestion")

        cursor.execute(
            """
            INSERT INTO analysis_history
            (
                user_id,
                user_email,
                file_name,
                language,
                code,
                success,
                error_type,
                error_message,
                error_line,
                suggestion,
                analyzed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                user_email,
                "Pasted Code",
                "Python",
                code,
                1 if success else 0,
                error_type,
                error_message,
                error_line,
                suggestion,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )

        conn.commit()
        conn.close()

        return True, None

    except Exception as e:

        return False, str(e)


# ==========================================
# ANALYZE PAGE
# ==========================================

def show_analyze():

    st.title("🧞 Debug Your Code")

    st.write(
        "Paste your Python code below and let DebugGenie "
        "analyze it for errors."
    )

    st.divider()

    # ==========================================
    # CODE INPUT
    # ==========================================

    code = st.text_area(
        "Python Code",
        height=350,
        placeholder="""Example:

x = 10
print(x)
"""
    )

    st.write("")

    col1, col2 = st.columns(2)

    # ==========================================
    # ANALYZE BUTTON
    # ==========================================

    with col1:

        if st.button(
            "🔍 Analyze Code",
            use_container_width=True
        ):

            if not code.strip():

                st.warning(
                    "Please enter some Python code first."
                )

            else:

                try:

                    # Import debugger
                    from backend.debugger import check_python_code

                    # Analyze code
                    result = check_python_code(code)

                    # ==================================
                    # SAVE RESULT IN SESSION
                    # ==================================

                    st.session_state.analysis_result = result
                    st.session_state.analysis_code = code

                    # ==================================
                    # SAVE RESULT TO DATABASE
                    # ==================================

                    saved, error = save_analysis_to_history(
                        code,
                        result
                    )

                    if not saved:

                        st.error(
                            f"Analysis worked, but history "
                            f"could not be saved: {error}"
                        )

                    # ==================================
                    # GO TO RESULTS
                    # ==================================

                    st.session_state.page = "results"

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Analysis error: {e}"
                    )

    # ==========================================
    # BACK BUTTON
    # ==========================================

    with col2:

        if st.button(
            "← Back to Dashboard",
            use_container_width=True
        ):

            st.session_state.page = "dashboard"
            st.rerun()