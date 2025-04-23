import streamlit as st
st.image("logo2Find_You_Way.png", width=250)
# ✅ Import path fix for backend folder


import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# ✅ Helper to read from Google Sheets
def read_data(tab_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = json.loads(st.secrets["google_sheets"]["service_account"])
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds, scope)
    client = gspread.authorize(credentials)
    sheet = client.open_by_key(st.secrets["google_sheets"]["sheet_id"])
    try:
        worksheet = sheet.worksheet(tab_name)
        data = worksheet.get_all_records()
        return data[-1] if data else {}
    except Exception:
        return {}

def run():
    st.title("📊 Goal Summary Dashboard")

    st.markdown("""
    This is your all-in-one view of your goal progress:
    - 🔍 Review SMART goals
    - 📅 Track 90-day milestones
    - 🚀 Stay aligned with long-term vision
    - 🧠 Reflect on your latest insight
    """)

    # 🔁 Load last entries from session or fallback to Google Sheets
    smart_data = st.session_state.get("specific") or read_data("SMART Goal Planner")
    tracker_data = st.session_state.get("Week 1") or read_data("90-Day Tracker")
    vision_data = st.session_state.get("one_year") or read_data("Long-Term Vision")
    reflection_data = st.session_state.get("journal") or read_data("Reflection & Insight")

    # 🧩 SMART Goal Summary
    st.subheader("🎯 SMART Goal Summary")
    if isinstance(smart_data, dict):
        for key in ["Specific", "Measurable", "Achievable", "Relevant", "Time-Bound"]:
            st.markdown(f"**{key}:** {smart_data.get(key, '...')}")
    else:
        st.markdown(f"**Specific:** {smart_data}")

    # 📅 90-Day Preview
    st.subheader("📅 90-Day Action Tracker")
    if isinstance(tracker_data, dict):
        for i in range(1, 13):
            st.markdown(f"**Week {i}:** {tracker_data.get(f'Week {i}', '...')}")
    else:
        st.markdown("90-Day plan data not found.")

    # 🚀 Long-Term Vision
    st.subheader("🚀 Long-Term Vision Overview")
    if isinstance(vision_data, dict):
        st.markdown(f"**1-Year Goal:** {vision_data.get('1-Year', '...')}")
        st.markdown(f"**3-Year Goal:** {vision_data.get('3-Year', '...')}")
        st.markdown(f"**5-Year Goal:** {vision_data.get('5-Year', '...')}")
    else:
        st.markdown(f"**1-Year Goal:** {vision_data}")

    # 🧠 Most Recent Reflection
    st.subheader("🧠 Latest Reflection & Insight")
    if isinstance(reflection_data, dict):
        st.markdown(f"**Reflection:** {reflection_data.get('Reflection', '...')}")
        st.markdown(f"**Insight:** {reflection_data.get('Insight', '...')}")
        st.markdown(f"**Reframe:** {reflection_data.get('Reframe', '...')}")
    else:
        st.markdown(f"**Reflection:** {reflection_data}")

    # 🔗 Navigation buttons
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
