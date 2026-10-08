import streamlit as st
import sqlite3


# ==========================================
# DATABASE
# ==========================================

DB_PATH = "debuggenie.db"


def get_history():

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        user_id = st.session_state.get("user_id")
        user_email = st.session_state.get("user_email")

        # Get history for logged-in user
        if user_id is not None:

            cursor.execute(
                """
                SELECT
                    id,
                    language,
                    success,
                    error_type,
                    error_message,
                    error_line,
                    analyzed_at
                FROM analysis_history
                WHERE user_id = ?
                ORDER BY id DESC
                """,
                (user_id,)
            )

        elif user_email:

            cursor.execute(
                """
                SELECT
                    id,
                    language,
                    success,
                    error_type,
                    error_message,
                    error_line,
                    analyzed_at
                FROM analysis_history
                WHERE user_email = ?
                ORDER BY id DESC
                """,
                (user_email,)
            )

        else:

            conn.close()
            return []

        rows = cursor.fetchall()

        conn.close()

        return rows

    except Exception as e:

        st.error(f"Could not load history: {e}")
        return []


# ==========================================
# DASHBOARD
# ==========================================

def show_dashboard():

    # ==========================================
    # HEADER
    # ==========================================

    st.title("🧞 DebugGenie Dashboard")

    username = st.session_state.get(
        "username",
        "User"
    )

    st.write(f"Welcome back, **{username}**!")

    st.divider()

    # ==========================================
    # NAVIGATION
    # ==========================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        if st.button(
            "🏠 Home",
            use_container_width=True
        ):

            st.session_state.page = "home"
            st.rerun()

    with col2:

        if st.button(
            "🔍 Analyze",
            use_container_width=True
        ):

            st.session_state.page = "analyze"
            st.rerun()

    with col3:

        if st.button(
            "📜 History",
            use_container_width=True
        ):

            st.session_state.show_history = True
            st.rerun()

    with col4:

        if st.button(
            "🚪 Logout",
            use_container_width=True
        ):

            st.session_state.logged_in = False
            st.session_state.page = "home"

            # Clear user information
            for key in [
                "user_id",
                "username",
                "user_email",
                "user_role",
                "analysis_result",
                "analysis_code"
            ]:

                if key in st.session_state:
                    del st.session_state[key]

            st.rerun()

    st.divider()

    # ==========================================
    # STATISTICS
    # ==========================================

    history = get_history()

    total = len(history)

    successful = sum(
        1 for row in history
        if row[2] == 1
    )

    errors = total - successful

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Total Analyses",
            total
        )

    with col2:

        st.metric(
            "Successful",
            successful
        )

    with col3:

        st.metric(
            "Errors Found",
            errors
        )

    st.divider()

    # ==========================================
    # QUICK ANALYZE
    # ==========================================

    st.subheader("🔍 Start Debugging")

    st.write(
        "Analyze your Python code and let DebugGenie "
        "identify errors and provide suggestions."
    )

    if st.button(
        "Analyze New Code →",
        use_container_width=True
    ):

        st.session_state.page = "analyze"
        st.rerun()

    st.divider()

    # ==========================================
    # HISTORY
    # ==========================================

    st.subheader("📜 Recent Analysis History")

    if not history:

        st.info(
            "No analysis history yet. "
            "Analyze some Python code to see it here."
        )

    else:

        for row in history[:10]:

            analysis_id = row[0]
            language = row[1]
            success = row[2]
            error_type = row[3]
            error_message = row[4]
            error_line = row[5]
            analyzed_at = row[6]

            if success == 1:

                status = "✅ No Error"

            else:

                status = f"❌ {error_type}"

            with st.container(border=True):

                col1, col2 = st.columns([3, 1])

                with col1:

                    st.write(
                        f"**Analysis #{analysis_id}**"
                    )

                    st.write(
                        f"Language: {language}"
                    )

                    st.write(
                        f"Status: {status}"
                    )

                    if error_message:

                        st.write(
                            f"Error: {error_message}"
                        )

                    if error_line:

                        st.write(
                            f"Line: {error_line}"
                        )

                with col2:

                    st.caption(
                        str(analyzed_at)
                    )

    st.divider()

    # ==========================================
    # REFRESH
    # ==========================================

    if st.button(
        "🔄 Refresh Dashboard",
        use_container_width=True
    ):

        st.rerun()