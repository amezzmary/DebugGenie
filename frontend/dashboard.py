
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "debuggenie.db"


# =========================================================
# DATABASE HELPERS
# =========================================================

def get_connection():
    """Connect to the existing DebugGenie SQLite database."""
    return sqlite3.connect(str(DB_PATH))


def get_history():
    """
    Fetch only the logged-in user's analysis history.

    Expected columns:
    id, user_id, user_email, file_name, language, code,
    success, error_type, error_message, error_line,
    suggestion, analyzed_at
    """

    user_id = st.session_state.get("user_id")
    user_email = st.session_state.get("user_email")

    if user_id is None and not user_email:
        return []

    try:
        with get_connection() as conn:
            conn.row_factory = sqlite3.Row

            if user_id is not None:
                rows = conn.execute(
                    """
                    SELECT
                        id,
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
                    FROM analysis_history
                    WHERE user_id = ?
                    ORDER BY analyzed_at DESC
                    """,
                    (user_id,),
                ).fetchall()

            else:
                rows = conn.execute(
                    """
                    SELECT
                        id,
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
                    FROM analysis_history
                    WHERE LOWER(user_email) = LOWER(?)
                    ORDER BY analyzed_at DESC
                    """,
                    (user_email,),
                ).fetchall()

            return [dict(row) for row in rows]

    except sqlite3.Error as error:
        st.error(f"Could not load analysis history: {error}")
        return []


# =========================================================
# DATA HELPERS
# =========================================================

def is_success(value):
    """Convert database success values into a reliable Boolean."""

    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        return value == 1

    return str(value).strip().lower() in {
        "1",
        "1.0",
        "true",
        "yes",
        "success",
        "successful",
    }


def parse_datetime(value):
    """Parse common SQLite timestamp formats."""

    if not value:
        return None

    if isinstance(value, datetime):
        return value

    value = str(value).strip()

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        pass

    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%d-%m-%Y %H:%M:%S",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except (ValueError, TypeError):
            continue

    return None


def prepare_progress_data(history):
    """Prepare analysis history for tables and charts."""

    records = []

    for row in history:
        analyzed_at = parse_datetime(row.get("analyzed_at"))

        records.append(
            {
                "Date": analyzed_at,
                "File": row.get("file_name") or "Pasted Code",
                "Language": row.get("language") or "Unknown",
                "Status": (
                    "Success"
                    if is_success(row.get("success"))
                    else "Error"
                ),
                "Error Type": row.get("error_type") or "None",
                "Error Message": row.get("error_message") or "",
            }
        )

    return pd.DataFrame(records)


# =========================================================
# ERROR PROGRESS CALCULATION
# =========================================================

def compare_error_progress(history):
    """
    Compare the latest 7 days against the preceding 7 days.

    Error rate = analyses with errors / all analyses * 100
    Reduction = (previous rate - current rate) / previous rate * 100
    """

    now = datetime.now().astimezone()
    current_start = now - timedelta(days=7)
    previous_start = now - timedelta(days=14)

    current_total = 0
    current_errors = 0

    previous_total = 0
    previous_errors = 0

    for row in history:
        analyzed_at = parse_datetime(row.get("analyzed_at"))

        if analyzed_at is None:
            continue

        # Convert timezone-aware timestamps to the same timezone.
        if analyzed_at.tzinfo is None:
            analyzed_at = analyzed_at.astimezone()
        else:
            analyzed_at = analyzed_at.astimezone()

        has_error = not is_success(row.get("success"))

        if current_start <= analyzed_at <= now:
            current_total += 1

            if has_error:
                current_errors += 1

        elif previous_start <= analyzed_at < current_start:
            previous_total += 1

            if has_error:
                previous_errors += 1

    current_rate = (
        current_errors / current_total * 100
        if current_total
        else 0
    )

    previous_rate = (
        previous_errors / previous_total * 100
        if previous_total
        else 0
    )

    reduction = None

    if previous_total > 0 and previous_rate > 0:
        reduction = (
            (previous_rate - current_rate) / previous_rate
        ) * 100

    return {
        "current_total": current_total,
        "current_errors": current_errors,
        "current_rate": current_rate,
        "previous_total": previous_total,
        "previous_errors": previous_errors,
        "previous_rate": previous_rate,
        "reduction": reduction,
    }


# =========================================================
# CSV REPORT
# =========================================================

def create_csv_report(history):
    """Create a downloadable report for the logged-in user."""

    columns = [
        "id",
        "file_name",
        "language",
        "success",
        "error_type",
        "error_message",
        "error_line",
        "suggestion",
        "analyzed_at",
    ]

    report_rows = [
        {column: row.get(column) for column in columns}
        for row in history
    ]

    return pd.DataFrame(report_rows, columns=columns).to_csv(
        index=False
    ).encode("utf-8")


# =========================================================
# MAIN DASHBOARD
# =========================================================

def show_dashboard():

    st.title("📊 DebugGenie Dashboard")
    st.caption(
        "Track your coding progress, review errors, "
        "and monitor improvement over time."
    )

    # -----------------------------------------------------
    # LOAD CURRENT USER'S HISTORY
    # -----------------------------------------------------

    user_name = (
        st.session_state.get("username")
        or st.session_state.get("user_name")
        or "User"
    )

    st.write(f"Welcome, **{user_name}**!")

    history = get_history()
    progress = prepare_progress_data(history)

    # -----------------------------------------------------
    # OVERALL STATISTICS
    # -----------------------------------------------------

    st.header("📌 Your Analysis Summary")

    total_analyses = len(history)
    successful_analyses = sum(
        1 for row in history if is_success(row.get("success"))
    )
    errors_found = total_analyses - successful_analyses

    success_rate = (
        successful_analyses / total_analyses * 100
        if total_analyses
        else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Analyses", total_analyses)
    col2.metric("Successful", successful_analyses)
    col3.metric("Errors Found", errors_found)
    col4.metric("Success Rate", f"{success_rate:.1f}%")

    st.divider()

    if not history:
        st.info(
            "No analysis history was found for this account. "
            "Analyse some code first to start your progress report."
        )
        return

    # -----------------------------------------------------
    # ERROR REDUCTION PROGRESS
    # -----------------------------------------------------

    st.header("📉 Error Reduction Progress")

    st.caption(
        "Compares your latest 7 days of activity with the "
        "previous 7 days. Only your own analysis records are used."
    )

    comparison = compare_error_progress(history)

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Previous 7-Day Errors",
        comparison["previous_errors"],
    )

    col2.metric(
        "Latest 7-Day Errors",
        comparison["current_errors"],
    )

    reduction = comparison["reduction"]

    if reduction is not None:
        col3.metric(
            "Error-Rate Reduction",
            f"{reduction:+.1f}%",
            delta=f"{reduction:+.1f}%",
            help=(
                "Positive means the error rate decreased. "
                "Negative means the error rate increased."
            ),
        )
    else:
        col3.metric("Error-Rate Reduction", "N/A")

    st.write(
        f"**Previous 7 days:** "
        f"{comparison['previous_errors']} errors from "
        f"{comparison['previous_total']} analyses "
        f"({comparison['previous_rate']:.1f}% error rate)"
    )

    st.write(
        f"**Latest 7 days:** "
        f"{comparison['current_errors']} errors from "
        f"{comparison['current_total']} analyses "
        f"({comparison['current_rate']:.1f}% error rate)"
    )

    if comparison["previous_total"] == 0:
        st.info(
            "Not enough analysis history from the previous "
            "7-day period to calculate a reduction yet. "
            "Continue using DebugGenie and check again later."
        )

    elif comparison["previous_rate"] == 0:
        st.info(
            "There were no errors in the previous 7-day period, "
            "so a percentage reduction cannot be calculated."
        )

    elif reduction is not None and reduction > 0:
        st.success(
            f"Good progress! Your error rate decreased by "
            f"{reduction:.1f}% compared with the previous period."
        )

    elif reduction is not None and reduction < 0:
        st.warning(
            f"Your error rate increased by "
            f"{abs(reduction):.1f}% compared with the previous period. "
            "Review the error details and keep practising."
        )

    else:
        st.info(
            "Your error rate stayed the same across both periods."
        )

    # Chart comparing error counts and analysis totals.
    comparison_chart = pd.DataFrame(
        [
            {
                "Period": "Previous 7 Days",
                "Errors": comparison["previous_errors"],
                "Successful": (
                    comparison["previous_total"]
                    - comparison["previous_errors"]
                ),
            },
            {
                "Period": "Latest 7 Days",
                "Errors": comparison["current_errors"],
                "Successful": (
                    comparison["current_total"]
                    - comparison["current_errors"]
                ),
            },
        ]
    )

    st.subheader("Errors by Period")
    st.bar_chart(
        comparison_chart.set_index("Period")[["Errors", "Successful"]]
    )

    st.divider()

    # -----------------------------------------------------
    # ERROR AND SUCCESS DISTRIBUTION
    # -----------------------------------------------------

    st.header("📈 Analysis Insights")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Success vs Errors")

        status_counts = pd.DataFrame(
            {
                "Result": ["Successful", "Errors"],
                "Count": [successful_analyses, errors_found],
            }
        )

        st.bar_chart(
            status_counts.set_index("Result")
        )

    with col2:
        st.subheader("Analyses by Language")

        language_counts = {}

        for row in history:
            language = row.get("language") or "Unknown"
            language_counts[language] = (
                language_counts.get(language, 0) + 1
            )

        language_df = pd.DataFrame(
            [
                {"Language": language, "Analyses": count}
                for language, count in language_counts.items()
            ]
        )

        if not language_df.empty:
            st.bar_chart(
                language_df.set_index("Language")
            )
        else:
            st.info("No language statistics are available.")

    st.divider()

    # -----------------------------------------------------
    # RECENT ACTIVITY
    # -----------------------------------------------------

    st.header("🕒 Recent Analysis History")

    recent_rows = []

    for row in history[:10]:
        recent_rows.append(
            {
                "Date": row.get("analyzed_at") or "Unknown",
                "File": row.get("file_name") or "Pasted Code",
                "Language": row.get("language") or "Unknown",
                "Status": (
                    "✅ Success"
                    if is_success(row.get("success"))
                    else "❌ Error"
                ),
                "Error Type": row.get("error_type") or "None",
                "Error Message": row.get("error_message") or "",
            }
        )

    if recent_rows:
        st.dataframe(
            pd.DataFrame(recent_rows),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No recent activity is available.")

    # -----------------------------------------------------
    # DOWNLOAD REPORT
    # -----------------------------------------------------

    st.header("📥 Download Your Progress Report")

    st.download_button(
        label="Download Analysis Report (CSV)",
        data=create_csv_report(history),
        file_name="debuggenie_progress_report.csv",
        mime="text/csv",
    )

    st.caption(
        "DebugGenie — Debug Smarter. Code Better. Ship Faster."
    )


# Support projects that call a differently named dashboard function.
def render_dashboard():
    show_dashboard()
