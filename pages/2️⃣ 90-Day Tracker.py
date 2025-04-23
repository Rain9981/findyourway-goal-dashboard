# ✅ Import path fix for backend folder
st.image("logo2Find_You_Way.png", width=250)
import streamlit as st

import streamlit as st

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from openai import OpenAI
from backend.google_sheets import save_data
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.pagesizes import letter
import datetime
import io
import json

# OpenAI client
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

def run():
    st.title("📅 90-Day Tracker")

    # Initialize session state for all 12 weeks
    for i in range(1, 13):
        key = f"week_{i}"
        if key not in st.session_state:
            st.session_state[key] = ""

    st.sidebar.header("🧠 How to Use This Tab")
    st.sidebar.markdown("""
    **90-Day Goal Tracker:**
    - Describe your 90-day goal
    - Use ✨ Autofill to generate a weekly plan
    - Save or export your plan for easy review

    **Bonus Features:**
    - GPT can suggest pacing or gaps
    - Export to PDF or Google Sheets
    """)

    st.markdown("### Describe your 90-day goal:")
    goal_input = st.text_area("Your 90-day goal", placeholder="e.g., Launch a personal brand with strong online presence")

    st.markdown("### Plan your 90-day (12-week) action steps:")

    if st.button("✨ Autofill All Weeks with AI"):
        if not goal_input.strip():
            st.warning("Please enter a 90-day goal above before generating the weekly plan.")
        else:
            with st.spinner("Generating 12-week plan..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "You're a business goal planner."},
                            {"role": "user", "content": f"Break this 90-day goal into 12 clearly labeled weekly steps. Each week must include a task. If unsure, say 'Check in and adjust.'\nGoal: {goal_input}"}
                        ]
                    )
                    content = response.choices[0].message.content.strip()
                    lines = content.split("\n")
                    for i in range(12):
                        if i < len(lines):
                            text = lines[i].split(":", 1)[-1].strip() if ":" in lines[i] else lines[i].strip()
                            st.session_state[f"week_{i+1}"] = text if text else "TBD – define this week's task"
                        else:
                            st.session_state[f"week_{i+1}"] = "TBD – define this week's task"
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ GPT Error: {e}")

    weeks = {}
    for i in range(1, 13):
        label = f"Week {i}"
        key = f"week_{i}"
        weeks[key] = st.text_area(label, value=st.session_state[key])

    if st.button("🧠 Get GPT Review & Pacing Tips"):
        with st.spinner("Reviewing your weekly breakdown..."):
            try:
                combined_plan = "\n".join([f"Week {i}: {weeks[f'week_{i}']}" for i in range(1, 13)])
                review = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You review goal pacing and consistency."},
                        {"role": "user", "content": f"Review this 90-day plan and give suggestions:\n{combined_plan}"}
                    ]
                )
                st.success("✅ GPT Review:")
                st.info(review.choices[0].message.content)
            except Exception as e:
                st.error(f"❌ GPT Error: {e}")

    if st.button("✅ Save to Google Sheets"):
        save_data("90-Day Tracker", {
            **{f"Week {i}": weeks[f"week_{i}"] for i in range(1, 13)},
            "Goal Description": goal_input,
            "Date": str(datetime.date.today())
        }, sheet_tab="90-Day Tracker")
        st.success("Saved to Google Sheets ✅")

    if st.button("📄 Export as PDF"):
        buffer = io.BytesIO()
        pdf = pdf_canvas.Canvas(buffer, pagesize=letter)
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, 750, "90-Day Tracker Plan")
        pdf.setFont("Helvetica", 12)
        y = 720
        pdf.drawString(50, y, f"Goal: {goal_input[:100]}")
        y -= 30
        for i in range(1, 13):
            pdf.drawString(50, y, f"Week {i}: {weeks[f'week_{i}'][:100] if weeks[f'week_{i}'] else 'N/A'}")
            y -= 40
            if y < 100:
                pdf.showPage()
                y = 750
        pdf.save()
        st.download_button("📥 Download 90-Day Plan PDF", data=buffer.getvalue(), file_name="90_day_plan.pdf")

if __name__ == "__main__":
    run()
