import streamlit as st
st.image("logo2Find_You_Way.png", width=250)
# ✅ Import path fix for backend folder


import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
    st.title("📌 SMART Goal Planner")

    # ✅ Initialize session state to avoid blank autofill
    for key in ["specific", "measurable", "achievable", "relevant", "time_bound"]:
        if key not in st.session_state:
            st.session_state[key] = ""

    st.sidebar.header("🧠 How to Use This Tab")
    st.sidebar.markdown("""
    **Step-by-step:**
    1. Define each SMART field below.
    2. Use ✨ Autofill to generate a sample.
    3. Click **Save to Sheets** or **Export PDF**.
    4. (Optional) Get AI Suggestions on your inputs.

    **SMART Breakdown:**
    - **S**pecific: What do you want to accomplish?
    - **M**easurable: How will you know it’s done?
    - **A**chievable: Is it realistic?
    - **R**elevant: Why does it matter?
    - **T**ime-bound: What’s the deadline?
    """)

    st.markdown("Enter your SMART goal components below:")

    if st.button("✨ Autofill with AI"):
        with st.spinner("Generating example SMART goal..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You're a SMART goal assistant. Respond only in JSON format."},
                        {"role": "user", "content": "Give me a business SMART goal as JSON with keys: Specific, Measurable, Achievable, Relevant, Time-Bound."}
                    ]
                )
                content = response.choices[0].message.content.strip()
                content = content.replace("```json", "").replace("```", "")
                data = json.loads(content)

                st.session_state["specific"] = data.get("Specific", "")
                st.session_state["measurable"] = data.get("Measurable", "")
                st.session_state["achievable"] = data.get("Achievable", "")
                st.session_state["relevant"] = data.get("Relevant", "")
                st.session_state["time_bound"] = data.get("Time-Bound", "")

                st.rerun()

            except Exception as e:
                st.error(f"❌ GPT Error: {e}")

    specific = st.text_area("Specific", value=st.session_state.get("specific", ""))
    measurable = st.text_area("Measurable", value=st.session_state.get("measurable", ""))
    achievable = st.text_area("Achievable", value=st.session_state.get("achievable", ""))
    relevant = st.text_area("Relevant", value=st.session_state.get("relevant", ""))
    time_bound = st.text_area("Time-Bound", value=st.session_state.get("time_bound", ""))

    if st.button("🧠 Get AI Suggestions"):
        with st.spinner("Analyzing your SMART goal for improvements..."):
            try:
                suggestion = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a SMART goal reviewer. Check if the following goal is specific, measurable, achievable, relevant, and time-bound."},
                        {"role": "user", "content": f"Specific: {specific}\nMeasurable: {measurable}\nAchievable: {achievable}\nRelevant: {relevant}\nTime-Bound: {time_bound}"}
                    ]
                )
                st.success("✅ Suggestion Received:")
                st.info(suggestion.choices[0].message.content)
            except Exception as e:
                st.error(f"❌ GPT Error: {e}")

    if st.button("✅ Save to Google Sheets"):
        save_data("SMART Goal Planner", {
            "Specific": specific,
            "Measurable": measurable,
            "Achievable": achievable,
            "Relevant": relevant,
            "Time-Bound": time_bound,
            "Date": str(datetime.date.today())
        }, sheet_tab="SMART Goal Planner")
        st.success("Saved to Google Sheets ✅")


    if st.button("📄 Export as PDF"):
        buffer = io.BytesIO()
        pdf = pdf_canvas.Canvas(buffer, pagesize=letter)
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, 750, "SMART Goal Planner")
        pdf.setFont("Helvetica", 12)
        y = 720
        for label, content in [
            ("Specific", specific),
            ("Measurable", measurable),
            ("Achievable", achievable),
            ("Relevant", relevant),
            ("Time-Bound", time_bound)
        ]:
            pdf.drawString(50, y, f"{label}: {content[:100]}" if content else f"{label}: N/A")
            y -= 40
        pdf.save()
        st.download_button("📥 Download SMART Goal PDF", data=buffer.getvalue(), file_name="smart_goal.pdf")

if __name__ == "__main__":
    run()
