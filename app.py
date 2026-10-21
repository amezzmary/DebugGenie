
import os
import sqlite3
from datetime import datetime
from backend.database import get_all_users, delete_user_account
import streamlit as st

from backend.c_debugger import check_c_code
from backend.cpp_debugger import check_cpp_code
from backend.debugger import check_python_code
from backend.local_llm import get_ai_debugging_help
from backend.database import login_user, register_user

from frontend.styles import load_styles
from frontend.dashboard import show_dashboard

from frontend.components import (
    render_footer,
    render_file_information,
    render_success_result,
    render_error_result,
    render_ai_analysis,
    render_submitted_code,
    render_empty_state,
    render_user_history_item,
    render_admin_history_item,
)

from frontend.pages import (
    render_home_header,
    render_home_hero,
    render_home_features,
    render_login_page_title,
    render_register_page_title,
    render_admin_stats,
    render_login_header,
    render_register_header,
    render_analyze_page_title,
    render_results_page_title,
    render_history_page_title,
    render_admin_page_title,
    render_admin_users_page_title,
    render_admin_history_page_title,
)


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="DebugGenie",
    page_icon="🐞",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DB_NAME = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "debuggenie.db",
)


# ==================================================
# SESSION STATE
# ==================================================

DEFAULT_STATE = {
    "page": "home",
    "logged_in": False,
    "user_id": None,
    "username": "",
    "user_email": "",
    "user_role": "user",
    "analysis_result": None,
    "analysis_code": "",
    "analysis_filename": "Pasted Code",
    "analysis_language": "Python",
    "analysis_suggestion": "",
    "ai_debugging_help": "",
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


def show_admin_users_page():
    st.title("👥 User Management")

    # Verify the logged-in user's role
    if st.session_state.get("user_role") != "admin":
        st.error("Access denied. Admin privileges required.")
        return

    users = get_all_users()

    if not users:
        st.info("No registered users found.")
        return

    # Display account information, never password hashes
    st.dataframe(
        [
            {
                "ID": u["id"],
                "Name": u["name"],
                "Email": u["email"],
                "Role": u["role"],
                "Created At": u["created_at"],
            }
            for u in users
        ],
        use_container_width=True,
        hide_index=True,
    )

    # Only allow deletion of non-admin accounts
    admin_id = st.session_state.get("user_id")
    deletable_users = [
        u for u in users
        if u["role"] != "admin"
        and str(u["id"]) != str(admin_id)
    ]

    if not deletable_users:
        st.info("There are no user accounts available to delete.")
        return

    st.subheader("Delete a user account")

    selected_user = st.selectbox(
        "Select a user",
        deletable_users,
        format_func=lambda u: f'{u["name"]} — {u["email"]}',
        key="admin_delete_user",
    )

    confirm = st.checkbox(
        f'Delete {selected_user["email"]} and all their analysis history?',
        key="confirm_delete_user",
    )

    if st.button("🗑️ Delete Selected User", type="primary"):
        if not confirm:
            st.warning("Please confirm before deleting this account.")
            return

        success, message = delete_user_account(
            selected_user["id"],
            admin_id,
        )

        if success:
            st.success(message)
            st.rerun()
        else:
            st.error(message)

# ==================================================
# DATABASE AND ANALYSIS HISTORY
# ==================================================

def get_connection():
    return sqlite3.connect(DB_NAME)


def init_history():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                user_email TEXT,
                file_name TEXT,
                language TEXT,
                code TEXT,
                success INTEGER,
                error_type TEXT,
                error_message TEXT,
                error_line TEXT,
                suggestion TEXT,
                analyzed_at TEXT
            )
        """)


def save_history(result, code, file_name, language, suggestion):
    if not st.session_state.get("logged_in"):
        return

    success = bool(result.get("success", False))
    error_type = result.get(
        "error_type", result.get("type", "")
    )
    error_message = result.get(
        "error_message", result.get("message", "")
    )
    error_line = result.get(
        "error_line", result.get("line", "")
    )

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO analysis_history (
                user_id, user_email, file_name, language, code,
                success, error_type, error_message, error_line,
                suggestion, analyzed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            st.session_state.user_id,
            st.session_state.user_email,
            file_name,
            language,
            code,
            int(success),
            str(error_type),
            str(error_message),
            str(error_line),
            str(suggestion),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ))


def user_history():
    user_id = st.session_state.get("user_id")

    if user_id is None:
        return []

    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT *
            FROM analysis_history
            WHERE user_id = ?
            ORDER BY id DESC
        """, (user_id,)).fetchall()

    return [dict(row) for row in rows]


def all_history():
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT *
            FROM analysis_history
            ORDER BY id DESC
        """).fetchall()

    return [dict(row) for row in rows]


def stats_for_user():
    user_id = st.session_state.get("user_id")

    if user_id is None:
        return 0, 0

    with get_connection() as conn:
        row = conn.execute("""
            SELECT
                COUNT(*),
                COALESCE(
                    SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END),
                    0
                )
            FROM analysis_history
            WHERE user_id = ?
        """, (user_id,)).fetchone()

    return int(row[0]), int(row[1])


def stats_all():
    with get_connection() as conn:
        user_count = conn.execute(
            "SELECT COUNT(*) FROM users"
        ).fetchone()[0]

        analysis_count = conn.execute(
            "SELECT COUNT(*) FROM analysis_history"
        ).fetchone()[0]

        error_count = conn.execute("""
            SELECT COUNT(*)
            FROM analysis_history
            WHERE success = 0
        """).fetchone()[0]

    return int(user_count), int(analysis_count), int(error_count)


init_history()
load_styles()


# ==================================================
# HOME PAGE
# ==================================================

def home():
    render_home_header()
    render_home_hero()

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if st.button(
            "📤 Analyze Code",
            key="home_analyze_code",
            width="stretch",
        ):
            if st.session_state.get("logged_in", False):
                st.session_state.page = "analyze"
            else:
                st.session_state.page = "login"

            st.rerun()

    render_home_features()


# ==================================================
# LOGIN PAGE
# ==================================================

def login_page():
    render_login_header()
    render_login_page_title()

    with st.form("login_form"):
        email = st.text_input("Email address")
        password = st.text_input(
            "Password",
            type="password",
        )

        submitted = st.form_submit_button(
            "Login",
            width="stretch",
        )

    if submitted:
        if not email.strip() or not password:
            st.warning("Please enter your email and password.")
        else:
            try:
                user = login_user(email.strip(), password)

                if isinstance(user, dict) and user.get("success"):
                    if isinstance(user, dict):
                        user_id = user.get(
                            "id", user.get("user_id")
                        )
                        username = user.get(
                            "name", user.get("username", "User")
                        )
                        user_email = user.get(
                            "email", email.strip()
                        )
                        role = user.get("role", "user")
                    else:
                        user_id = user[0]
                        username = (
                            user[1] if len(user) > 1 else "User"
                        )
                        user_email = (
                            user[2] if len(user) > 2
                            else email.strip()
                        )
                        role = user[3] if len(user) > 3 else "user"

                    st.session_state.logged_in = True
                    st.session_state.user_id = user_id
                    st.session_state.username = username
                    st.session_state.user_email = user_email
                    st.session_state.user_role = role

                    if str(role).lower() == "admin":
                        st.session_state.page = "admin"
                    else:
                        st.session_state.page = "dashboard"

                    st.rerun()
                else:
                    st.error("Invalid email or password.")

            except Exception as error:
                st.error(f"Login failed: {error}")

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "Create an account",
            key="login_register",
        ):
            st.session_state.page = "register"
            st.rerun()

    with col2:
        if st.button(
            "Back to Home",
            key="login_home",
        ):
            st.session_state.page = "home"
            st.rerun()


# ==================================================
# REGISTRATION PAGE
# ==================================================

def register_page():
    render_register_header()
    render_register_page_title()

    with st.form("register_form"):
        name = st.text_input("Full name")
        email = st.text_input("Email address")
        password = st.text_input(
            "Password",
            type="password",
        )
        confirm_password = st.text_input(
            "Confirm password",
            type="password",
        )

        submitted = st.form_submit_button(
            "Sign Up",
            width="stretch",
        )

    if submitted:
        if not name.strip() or not email.strip() or not password:
            st.warning("Please fill in all required fields.")

        elif password != confirm_password:
            st.error("Passwords do not match.")

        else:
            try:
                result = register_user(
                    name.strip(),
                    email.strip(),
                    password,
                )

                if result:
                    st.success(
                        "Registration completed. Please log in."
                    )
                    st.session_state.page = "login"
                    st.rerun()
                else:
                    st.error(
                        "Registration was not completed. "
                        "The email may already be registered."
                    )

            except Exception as error:
                st.error(f"Registration failed: {error}")

    if st.button(
        "Already have an account? Login",
        key="register_login",
    ):
        st.session_state.page = "login"
        st.rerun()


# ==================================================
# DASHBOARD PAGE
# ==================================================

def dashboard():
    # Dashboard and progress report remain in the existing module.
    show_dashboard()


# ==================================================
# ANALYZE CODE PAGE
# ==================================================

def analyze_page():
    render_analyze_page_title()

    language = st.selectbox(
        "Programming Language",
        ["Python", "C", "C++", "Java", "JavaScript"],
        key="analysis_language_select",
    )

    extensions = {
        "Python": ["py"],
        "C": ["c", "h"],
        "C++": ["cpp", "cc", "cxx", "h", "hpp"],
        "Java": ["java"],
        "JavaScript": ["js", "mjs", "cjs"],
    }

    method = st.radio(
        "Choose Input Method",
        ["Paste Code", "Upload File"],
        horizontal=True,
        key="analysis_method",
    )

    code = ""
    filename = "Pasted Code"

    if method == "Paste Code":
        code = st.text_area(
            "Enter your code",
            height=350,
            placeholder="Paste your code here...",
            key="analysis_editor",
        )

    else:
        uploaded_file = st.file_uploader(
            f"Upload a {language} file",
            type=extensions[language],
            key="analysis_upload",
        )

        if uploaded_file is not None:
            filename = uploaded_file.name

            try:
                code = uploaded_file.getvalue().decode("utf-8")
                st.success(f"Loaded file: {filename}")
                st.code(code, language=language.lower())

            except UnicodeDecodeError:
                st.error(
                    "Unable to read this file. "
                    "Please upload a UTF-8 text file."
                )
                return

    # Fixed: Replaced `width="stretch"` with `use_container_width=True`
    if st.button(
        "🔍 Start Analysis",
        key="analyze_btn",
        use_container_width=True,
    ):
        if not code or not code.strip():
            st.warning("Please enter your code or upload a file first.")

        else:
            try:
                # 1. Execute Language-Specific Local Debugger
                with st.spinner("Debugging code with local analyzer..."):
                    if language == "Python":
                        result = check_python_code(code)

                    elif language == "C":
                        result = check_c_code(code)

                    elif language == "C++":
                        result = check_cpp_code(code)

                    elif language == "Java":
                        from backend.java_debugger import check_java_code
                        result = check_java_code(code)

                    elif language == "JavaScript":
                        from backend.javascript_debugger import (
                            check_javascript_code
                        )
                        result = check_javascript_code(code)

                    else:
                        st.error("Unsupported programming language.")
                        return

                if not isinstance(result, dict):
                    raise TypeError(
                        "The debugger did not return a valid dictionary result."
                    )

                # 2. Extract Suggestion
                if result.get("success", False):
                    suggestion = "No errors detected by the local debugger."
                else:
                    suggestion = result.get(
                        "suggestion",
                        result.get(
                            "error_message",
                            result.get("message", "Review the reported error."),
                        ),
                    )

                # 3. Generate AI Debugging Assistance (With Exception Fallback)
                ai_help = ""
                with st.spinner("Generating AI explanation..."):
                    try:
                        ai_help = get_ai_debugging_help(
                            code=code,
                            error_type=result.get(
                                "error_type", result.get("type", "")
                            ),
                            error_message=result.get(
                                "error_message", result.get("message", "")
                            ),
                            line=str(
                                result.get(
                                    "error_line", result.get("line", "")
                                )
                            ),
                            language=language,
                        )
                    except Exception as ai_err:
                        ai_help = f"AI analysis failed or unavailable: {ai_err}"

                # 4. Save Session State Data
                st.session_state["analysis_result"] = result
                st.session_state["analysis_code"] = code
                st.session_state["analysis_filename"] = filename
                st.session_state["analysis_language"] = language
                st.session_state["analysis_suggestion"] = suggestion
                st.session_state["ai_debugging_help"] = ai_help

                # 5. Persist Record to SQLite History
                try:
                    save_history(
                        result,
                        code,
                        filename,
                        language,
                        suggestion,
                    )
                except Exception as history_error:
                    st.warning(
                        f"Analysis completed, but saving history failed: {history_error}"
                    )

                # 6. Redirect to Results Page
                st.session_state["page"] = "results"
                st.rerun()

            except Exception as error:
                st.error(f"Code analysis failed: {error}")

# ==================================================
# RESULTS PAGE
# ==================================================

def results_page():
    render_results_page_title()

    result = st.session_state.get("analysis_result")
    code = st.session_state.get("analysis_code", "")
    filename = st.session_state.get("analysis_filename", "Pasted Code")
    language = st.session_state.get("analysis_language", "Python")
    suggestion = st.session_state.get("analysis_suggestion", "")
    ai_help = st.session_state.get("ai_debugging_help", "")

    if result is None:
        st.info("No analysis results are available yet.")
        if st.button("Analyze Code", key="results_start_analysis"):
            st.session_state.page = "analyze"
            st.rerun()
        return

    # Call component functions defensively
    try:
        render_file_information(filename, language)
    except TypeError:
        render_file_information(filename)

    if result.get("success", False):
        try:
            render_success_result(result)
        except TypeError:
            render_success_result()
    else:
        try:
            render_error_result(result, suggestion)
        except TypeError:
            try:
                render_error_result(result)
            except TypeError:
                render_error_result()

    if ai_help:
        try:
            render_ai_analysis(ai_help)
        except TypeError:
            st.subheader("🤖 AI Debugging Analysis")
            st.write(ai_help)

    try:
        render_submitted_code(code, language)
    except TypeError:
        try:
            render_submitted_code(code)
        except TypeError:
            st.code(code)

    report_text = f"""
DEBUGGENIE - ANALYSIS REPORT
============================

File: {filename}
Language: {language}

Analysis Status: {"Success" if result.get("success", False) else "Error"}

Error Type: {result.get("error_type", result.get("type", ""))}
Error Message: {result.get("error_message", result.get("message", ""))}
Error Line: {result.get("error_line", result.get("line", ""))}

Suggestion:
{suggestion}

AI DEBUGGING ANALYSIS:
{ai_help}

SUBMITTED CODE:
{code}
"""

    st.download_button(
        "📥 Download Analysis Report",
        data=report_text,
        file_name="debuggenie_analysis_report.txt",
        mime="text/plain",
        key="download_analysis_report",
        use_container_width=True,
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔍 Analyze Another", key="results_analyze_another", use_container_width=True):
            st.session_state.page = "analyze"
            st.rerun()

    with col2:
        if st.button("📋 View History", key="results_view_history", use_container_width=True):
            st.session_state.page = "history"
            st.rerun()

    with col3:
        if st.button("🏠 Dashboard", key="results_dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()
# ==================================================
# USER HISTORY PAGE
# ==================================================

def history_page():
    render_history_page_title()

    records = user_history()

    if not records:
        render_empty_state()
        return

    st.write(f"Your total analyses: **{len(records)}**")

    for item in records:
        render_user_history_item(item)


# ==================================================
# ADMIN DASHBOARD
# ==================================================

def admin_page():
    render_admin_page_title()

    total_users, total_analyses, total_errors = stats_all()

    render_admin_stats(
        total_users,
        total_analyses,
        total_errors,
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "👥 Manage Users",
            key="admin_manage_users",
            width="stretch",
        ):
            st.session_state.page = "admin_users"
            st.rerun()

    with col2:
        if st.button(
            "📋 Analysis History",
            key="admin_analysis_history",
            width="stretch",
        ):
            st.session_state.page = "admin_history"
            st.rerun()


# ==================================================
# ADMIN USER MANAGEMENT
# ==================================================
DB = "debuggenie.db"
def admin_users():

    render_admin_users_page_title()

    admin_id = st.session_state.get("user_id")

    # Read registered users
    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row

        users = conn.execute("""
            SELECT id, name, email, role, created_at
            FROM users
            ORDER BY id DESC
        """).fetchall()

    if not users:
        st.info("No registered users found.")
        return

    # Display users without password information
    st.dataframe(
        [
            {
                "ID": u["id"],
                "Name": u["name"],
                "Email": u["email"],
                "Role": u["role"],
                "Created At": u["created_at"],
            }
            for u in users
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.divider()
    st.subheader("🗑️ Delete User Account")

    # Exclude admin accounts and the current admin
    deletable_users = [
        u for u in users
        if u["role"] != "admin"
        and str(u["id"]) != str(admin_id)
    ]

    if not deletable_users:
        st.info("No eligible user accounts to delete.")
        return

    # Convert SQLite Row objects into normal dictionaries
    deletable_users = [dict(u) for u in deletable_users]

    # Select a user using a simple string option
    user_options = {
      f'{u["name"]} — {u["email"]} (ID: {u["id"]})': u
     for u in deletable_users
    }

    selected_label = st.selectbox(
     "Select a user to delete",
        list(user_options.keys()),
        key="delete_user_selection",
    )

    selected = user_options[selected_label]

    confirm = st.checkbox(
        f'Confirm deletion of {selected["email"]} '
        "and all their analysis history",
        key="confirm_user_deletion",
    )

    if st.button(
        "🗑️ Delete Selected User",
        type="primary",
        key="delete_selected_user",
    ):
        if not confirm:
            st.warning("Please confirm before deleting.")
            return

        try:
            with sqlite3.connect(DB) as conn:
                # Recheck the target immediately before deletion
                target = conn.execute(
                    "SELECT role FROM users WHERE id = ?",
                    (selected["id"],),
                ).fetchone()

                if target is None:
                    st.error("User no longer exists.")
                    return

                if target[0] == "admin":
                    st.error("Admin accounts cannot be deleted here.")
                    return

                if str(selected["id"]) == str(admin_id):
                    st.error("You cannot delete your own account.")
                    return

                # Both deletions commit together
                conn.execute(
                    "DELETE FROM analysis_history WHERE user_id = ?",
                    (selected["id"],),
                )

                cursor = conn.execute(
                    "DELETE FROM users WHERE id = ?",
                    (selected["id"],),
                )

                if cursor.rowcount != 1:
                    raise RuntimeError("User deletion failed.")

            st.success(
                f'User {selected["email"]} and their '
                "analysis history were deleted."
            )
            st.rerun()

        except sqlite3.Error as ex:
            st.error(f"Database error: {ex}")


# ==================================================
# ADMIN ANALYSIS HISTORY
# ==================================================

def admin_history():
    render_admin_history_page_title()

    records = all_history()

    if not records:
        st.info("No analysis records were found.")
        return

    st.write(f"Total analyses: **{len(records)}**")

    for item in records:
        render_admin_history_item(item)


# ==================================================
# LOGOUT
# ==================================================

def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    for key, value in DEFAULT_STATE.items():
        st.session_state[key] = value

    st.rerun()


# ==================================================
# SIDEBAR NAVIGATION
# ==================================================

def render_sidebar():
    if not st.session_state.get("logged_in"):
        return

    with st.sidebar:
        st.markdown("## 🐞 DebugGenie")
        st.write(f"Welcome, {st.session_state.username}")

        role = str(
            st.session_state.get("user_role", "user")
        ).lower()

        if role == "admin":
            if st.button(
                "Admin Dashboard",
                key="nav_admin",
                width="stretch",
            ):
                st.session_state.page = "admin"
                st.rerun()

            if st.button(
                "User Management",
                key="nav_admin_users",
                width="stretch",
            ):
                st.session_state.page = "admin_users"
                st.rerun()

            if st.button(
                "Analysis History",
                key="nav_admin_history",
                width="stretch",
            ):
                st.session_state.page = "admin_history"
                st.rerun()

        else:
            if st.button(
                "Dashboard",
                key="nav_dashboard",
                width="stretch",
            ):
                st.session_state.page = "dashboard"
                st.rerun()

            if st.button(
                "Analyze Code",
                key="nav_analyze",
                width="stretch",
            ):
                st.session_state.page = "analyze"
                st.rerun()

            if st.button(
                "Latest Result",
                key="nav_results",
                width="stretch",
            ):
                st.session_state.page = "results"
                st.rerun()

            if st.button(
                "History",
                key="nav_history",
                width="stretch",
            ):
                st.session_state.page = "history"
                st.rerun()

        if st.button(
            "Home",
            key="nav_home",
            width="stretch",
        ):
            st.session_state.page = "home"
            st.rerun()

        if st.button(
            "Logout",
            key="nav_logout",
            width="stretch",
        ):
            logout()


# ==================================================
# MAIN PAGE ROUTING
# ==================================================

render_sidebar()

page = st.session_state.get("page", "home")

if page == "home":
    home()

elif page == "login":
    login_page()

elif page == "register":
    register_page()

elif page == "dashboard" and st.session_state.logged_in:
    dashboard()

elif page == "analyze" and st.session_state.logged_in:
    analyze_page()

elif page == "results" and st.session_state.logged_in:
    results_page()

elif page == "history" and st.session_state.logged_in:
    history_page()

elif (
    page == "admin"
    and st.session_state.logged_in
    and str(st.session_state.user_role).lower() == "admin"
):
    admin_page()

elif (
    page == "admin_users"
    and st.session_state.logged_in
    and str(st.session_state.user_role).lower() == "admin"
):
    admin_users()

elif (
    page == "admin_history"
    and st.session_state.logged_in
    and str(st.session_state.user_role).lower() == "admin"
):
    admin_history()

else:
    st.session_state.page = "home"
    st.rerun()

render_footer()
