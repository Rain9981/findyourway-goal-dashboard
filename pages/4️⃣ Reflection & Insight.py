# ✅ Import path fix for backend folder
import streamlit as st
st.image("logo2Find_You_Way.png", width=250)

import streamlit as st
st.image("logo2Find_You_Way.png", width=250)

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

client = OpenAI(api_key=st.secrets["openai"]["api_key"])

def run():
    st.title("🧠 Reflection & AI Insight")

    if "journal" not in st.session_state:
        st.session_state["journal"] = ""
    if "insight" not in st.session_state:
        st.session_state["insight"] = ""
    if "reframe" not in st.session_state:
        st.session_state["reframe"] = ""

    st.sidebar.header("🧘 How to Use This Tab")
    st.sidebar.markdown("""
    - Write a reflection or journal entry.
    - Click ✨ Get Insight to receive motivational feedback.
    - Save or export your entry for future tracking.
    """)

    journal = st.text_area("📝 Weekly Reflection", value=st.session_state["journal"], height=200)

    if st.button("✨ Get AI Insight"):
        with st.spinner("Analyzing your reflection..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": "You're a motivational coach who gives structured feedback. Always respond with exactly two parts:\n\nInsight: [Give uplifting feedback]\nReframe: [Suggest a mental reframe for the week]"
                        },
                        {
                            "role": "user",
                            "content": f"My weekly reflection: {journal}"
                        }
                    ]
                )
                content = response.choices[0].message.content

                insight = ""
                reframe = ""

                # Clean parsing based on labels
                if "Insight:" in content:
                    insight = content.split("Insight:")[1].split("Reframe:")[0].strip()
                if "Reframe:" in content:
                    reframe = content.split("Reframe:")[1].strip()

                st.session_state["journal"] = journal
                st.session_state["insight"] = insight
                st.session_state["reframe"] = reframe
                st.success("✅ AI Insight and Mindset Tune-Up ready!")
            except Exception as e:
                st.error(f"❌ GPT Error: {e}")

    insight = st.text_area("💬 AI Insight Feedback", value=st.session_state["insight"], height=150)
    reframe = st.text_area("🧘 Mindset Tune-Up Suggestion", value=st.session_state["reframe"], height=100)

    if st.button("✅ Save to Google Sheets"):
        save_data("Reflection & Insight", {
            "Reflection": journal,
            "Insight": insight,
            "Reframe": reframe,
            "Date": str(datetime.date.today())
        }, sheet_tab="Reflection & Insight")
        st.success("Saved to Google Sheets ✅")

    if st.button("📄 Export as PDF"):
        buffer = io.BytesIO()
        pdf = pdf_canvas.Canvas(buffer, pagesize=letter)
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, 750, "Reflection & AI Insight")
        pdf.setFont("Helvetica", 12)
        y = 720
        pdf.drawString(50, y, f"Date: {str(datetime.date.today())}")
        y -= 30
        pdf.drawString(50, y, "Weekly Reflection:")
        y -= 20
        for line in journal.split("\n"):
            pdf.drawString(50, y, line[:100])
            y -= 20
        y -= 10
        pdf.drawString(50, y, "AI Insight Feedback:")
        y -= 20
        for line in insight.split("\n"):
            pdf.drawString(50, y, line[:100])
            y -= 20
        y -= 10
        pdf.drawString(50, y, "Mindset Reframe Suggestion:")
        y -= 20
        for line in reframe.split("\n"):
            pdf.drawString(50, y, line[:100])
            y -= 20
        pdf.save()
        st.download_button("📥 Download Reflection PDF", data=buffer.getvalue(), file_name="reflection_insight.pdf")

if __name__ == "__main__":
    run()
