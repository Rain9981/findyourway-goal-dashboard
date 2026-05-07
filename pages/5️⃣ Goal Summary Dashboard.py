import streamlit as st
st.image("logo2Find_You_Way.png", width=250)

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from openai import OpenAI

client_ai = OpenAI(api_key=st.secrets["openai"]["api_key"])


def read_latest_sheet_row(tab_name):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = json.loads(st.secrets["google_sheets"]["service_account"])
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds, scope)
        client_gsheets = gspread.authorize(credentials)
        sheet = client_gsheets.open_by_key(st.secrets["google_sheets"]["sheet_id"])
        worksheet = sheet.worksheet(tab_name)

        values = worksheet.get_all_values()

        if len(values) < 2:
            return {}

        headers = values[0]
        last_row = values[-1]

        return {
            headers[i]: last_row[i] if i < len(last_row) else ""
            for i in range(len(headers))
        }

    except Exception:
        return {}


def get_value(session_key, sheet_data, sheet_key, default="..."):
    value = st.session_state.get(session_key, "")
    if value:
        return value
    if isinstance(sheet_data, dict):
        return sheet_data.get(sheet_key, default)
    return default


def run():
    st.title("📊 Goal Summary Dashboard V2")
    st.caption("Review your SMART goal, 90-day progress, long-term vision, and reflection in one place.")

    st.sidebar.header("📊 Dashboard Guide")
    st.sidebar.markdown("""
**What this dashboard does:**
- reads current session data first
- safely attempts to load latest saved Google Sheets data
- shows SMART, 90-day, vision, and reflection summaries
- avoids crashing if Sheets are unavailable

**Important:**
Session data resets when the app/browser resets. Saved Google Sheets data is the permanent fallback.
""")

    smart_data = read_latest_sheet_row("SMART Goal Planner")
    tracker_data = read_latest_sheet_row("90-Day Tracker")
    vision_data = read_latest_sheet_row("Long-Term Vision")
    reflection_data = read_latest_sheet_row("Reflection & Insight")

    st.subheader("🎯 SMART Goal Summary")

    smart_specific = get_value("specific", smart_data, "Specific")
    smart_measurable = get_value("measurable", smart_data, "Measurable")
    smart_achievable = get_value("achievable", smart_data, "Achievable")
    smart_relevant = get_value("relevant", smart_data, "Relevant")
    smart_time_bound = get_value("time_bound", smart_data, "Time-Bound")

    st.markdown(f"**Specific:** {smart_specific}")
    st.markdown(f"**Measurable:** {smart_measurable}")
    st.markdown(f"**Achievable:** {smart_achievable}")
    st.markdown(f"**Relevant:** {smart_relevant}")
    st.markdown(f"**Time-Bound:** {smart_time_bound}")

    if smart_data.get("Goal Score"):
        st.info(
            f"**Goal Score:** {smart_data.get('Goal Score')} | "
            f"**Readiness:** {smart_data.get('Execution Readiness', '...')}"
        )

    st.divider()

    st.subheader("📅 90-Day Action Tracker")

    goal_description = (
        st.session_state.get("goal_input", "")
        or tracker_data.get("Goal Description", "...")
    )

    st.markdown(f"**Goal:** {goal_description}")

    completed_weeks = 0

    for i in range(1, 13):
        session_done = st.session_state.get(f"week_{i}_done", False)
        sheet_done = str(tracker_data.get(f"Week {i} Complete", "")).lower() in ["true", "yes", "1"]

        if session_done or sheet_done:
            completed_weeks += 1

    progress_percent = int((completed_weeks / 12) * 100)

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Weeks Complete", f"{completed_weeks}/12")

    with col2:
        st.metric("Progress", f"{progress_percent}%")

    st.progress(progress_percent / 100)

    with st.expander("View all 12 weeks", expanded=True):
        for i in range(1, 13):
            week_value = (
                st.session_state.get(f"week_{i}", "")
                or tracker_data.get(f"Week {i}", "...")
            )

            done_value = (
                st.session_state.get(f"week_{i}_done", False)
                or str(tracker_data.get(f"Week {i} Complete", "")).lower() in ["true", "yes", "1"]
            )

            status = "✅ Complete" if done_value else "⬜ Not Complete"

            st.markdown(f"**Week {i}: {status}**")
            st.markdown(week_value if week_value else "...")

    if tracker_data.get("GPT Review"):
        st.markdown("**Latest GPT Review:**")
        st.info(tracker_data.get("GPT Review"))

    st.divider()

    st.subheader("🚀 Long-Term Vision Overview")

    vision_source = (
        st.session_state.get("vision_input", "")
        or vision_data.get("Source Goal", "...")
    )

    one_year = (
        st.session_state.get("one_year", "")
        or vision_data.get("1-Year", "...")
    )

    three_year = (
        st.session_state.get("three_year", "")
        or vision_data.get("3-Year", "...")
    )

    five_year = (
        st.session_state.get("five_year", "")
        or vision_data.get("5-Year", "...")
    )

    future_self = (
        st.session_state.get("future_self", "")
        or vision_data.get("Future Self", "")
    )

    st.markdown(f"**Source Goal:** {vision_source}")
    st.markdown(f"**1-Year Goal:** {one_year}")
    st.markdown(f"**3-Year Goal:** {three_year}")
    st.markdown(f"**5-Year Goal:** {five_year}")

    if future_self:
        st.markdown("**Message from Future Self:**")
        st.info(future_self)

    st.divider()

    st.subheader("🧠 Latest Reflection & Insight")

    reflection = (
        st.session_state.get("journal", "")
        or reflection_data.get("Reflection", "...")
    )

    insight = (
        st.session_state.get("insight", "")
        or reflection_data.get("Insight", "...")
    )

    reframe = (
        st.session_state.get("reframe", "")
        or reflection_data.get("Reframe", "...")
    )

    next_action = (
        st.session_state.get("next_action", "")
        or reflection_data.get("Next Action", "...")
    )

    st.markdown(f"**Reflection:** {reflection}")
    st.markdown(f"**Insight:** {insight}")
    st.markdown(f"**Reframe:** {reframe}")
    st.markdown(f"**Next Action:** {next_action}")

    st.divider()

    st.subheader("🧠 AI Goal Coach Summary")

    if "goal_coach_summary" not in st.session_state:
        st.session_state["goal_coach_summary"] = ""

    if st.button("🧠 Analyze My Full Goal Journey"):
        with st.spinner("Analyzing full goal journey..."):
            try:
                response = client_ai.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an AI goal coach. Give clear, motivating, practical feedback."
                        },
                        {
                            "role": "user",
                            "content": f"""
Analyze this full goal journey:

SMART Goal:
Specific: {smart_specific}
Measurable: {smart_measurable}
Achievable: {smart_achievable}
Relevant: {smart_relevant}
Time-Bound: {smart_time_bound}

90-Day Goal:
{goal_description}

90-Day Progress:
{completed_weeks}/12 weeks complete, {progress_percent}%

Long-Term Vision:
Source Goal: {vision_source}
1-Year: {one_year}
3-Year: {three_year}
5-Year: {five_year}
Future Self: {future_self}

Latest Reflection:
{reflection}

Insight:
{insight}

Reframe:
{reframe}

Next Action:
{next_action}

Return:
1. Current Progress
2. Main Pattern
3. Biggest Risk
4. Best Next Move
5. Motivational Coaching Note
"""
                        }
                    ],
                    temperature=0.75
                )

                st.session_state["goal_coach_summary"] = response.choices[0].message.content
                st.success("✅ Goal Coach Summary generated.")

            except Exception as e:
                st.error(f"❌ GPT Error: {e}")

    if st.session_state.get("goal_coach_summary"):
        st.info(st.session_state["goal_coach_summary"])

    st.divider()

    st.markdown("### 🧭 Quick Access to Tabs")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.page_link("pages/1️⃣ SMART Goal Planner.py", label="Edit SMART Goal")

    with col2:
        st.page_link("pages/2️⃣ 90-Day Tracker.py", label="Edit 90-Day Plan")

    with col3:
        st.page_link("pages/3️⃣ Long-Term Vision.py", label="Edit Vision")

    with col4:
        st.page_link("pages/4️⃣ Reflection & Insight.py", label="Reflect Again")


if __name__ == "__main__":
    run()