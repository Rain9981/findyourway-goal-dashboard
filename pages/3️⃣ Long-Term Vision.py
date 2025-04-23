# ✅ Import path fix for backend folder
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
    st.title("🚀 Long-Term Vision Planner")

    for key in ["one_year", "three_year", "five_year", "future_self", "vision_input"]:
        if key not in st.session_state:
            st.session_state[key] = ""

    st.sidebar.header("🧠 How to Use This Tab")
    st.sidebar.markdown("""
    **Vision Planning Steps:**
    1. Choose your main goal input source.
    2. Click ✨ Autofill to generate 1, 3, and 5-year goals.
    3. Get a message from your future self based on your journey.
    4. Save your vision to Google Sheets or export as PDF.
    """)

    st.markdown("### Select your long-term focus goal:")
    goal_source = st.selectbox("Source of your main goal", ["Custom Input", "SMART Goal", "90-Day Goal"])

    if goal_source == "Custom Input":
        vision_input = st.text_area("Describe your long-term goal:", value=st.session_state["vision_input"])
    elif goal_source == "SMART Goal":
        vision_input = st.session_state.get("specific", "Grow my brand")
    else:
        vision_input = st.session_state.get("goal_input", "Launch a personal brand")

    st.session_state["vision_input"] = vision_input

    show_raw = st.checkbox("Show GPT raw output (debug)", value=False)

    if st.button("✨ Autofill Vision Goals with GPT"):
        with st.spinner("Generating 1/3/5-year goals and vision message..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You're a visionary coach. Use the provided goal to create a 1-year, 3-year, and 5-year goal. Then write a short motivational reflection from the person's future self in 5 years."},
                        {"role": "user", "content": f"Goal: {vision_input}\nGenerate a clear and inspiring 1-year, 3-year, and 5-year goal. Then write a paragraph message from their future self explaining how they succeeded."}
                    ]
                )
                content = response.choices[0].message.content
                if show_raw:
                    st.markdown("#### 🔍 GPT Raw Output")
                    st.code(content)

                parts = content.split("\n")
                fs_lines = []
                for p in parts:
                    lower = p.lower()
                    if lower.startswith("1-year"):
                        value = p.split(":", 1)[1].strip() if ":" in p else "TBD – define 1-year goal"
                        st.session_state["one_year"] = value or "TBD – define 1-year goal"
                    elif lower.startswith("3-year"):
                        value = p.split(":", 1)[1].strip() if ":" in p else "TBD – define 3-year goal"
                        st.session_state["three_year"] = value or "TBD – define 3-year goal"
                    elif lower.startswith("5-year"):
                        value = p.split(":", 1)[1].strip() if ":" in p else "TBD – define 5-year goal"
                        st.session_state["five_year"] = value or "TBD – define 5-year goal"
                    elif lower.startswith("message") or "future self" in lower or lower.startswith("you made it"):
                        fs_lines.append(p.strip())
                if fs_lines:
                    st.session_state["future_self"] = "\n".join(fs_lines)
                elif not st.session_state["future_self"]:
                    st.session_state["future_self"] = f"You made it because you followed through on your 1-year plan ({st.session_state['one_year']}), your 3-year strategy ({st.session_state['three_year']}), and your long-term commitment ({st.session_state['five_year']})."
                st.success("✅ Vision goals and reflection filled in successfully!")
            except Exception as e:
                st.error(f"❌ GPT Error: {e}")

    one_year = st.text_area("1-Year Goal", value=st.session_state["one_year"])
    three_year = st.text_area("3-Year Goal", value=st.session_state["three_year"])
    five_year = st.text_area("5-Year Goal", value=st.session_state["five_year"])
    future_self = st.text_area("🪞 Message from Your Future Self", value=st.session_state["future_self"])

    if st.button("✅ Save to Google Sheets"):
        save_data("Long-Term Vision", {
            "1-Year": one_year,
            "3-Year": three_year,
            "5-Year": five_year,
            "Future Self": future_self,
            "Source Goal": vision_input,
            "Date": str(datetime.date.today())
        }, sheet_tab="Long-Term Vision")
        st.success("Saved to Google Sheets ✅")

    if st.button("📄 Export as PDF"):
        buffer = io.BytesIO()
        pdf = pdf_canvas.Canvas(buffer, pagesize=letter)
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, 750, "Long-Term Vision Plan")
        pdf.setFont("Helvetica", 12)
        y = 720
        pdf.drawString(50, y, f"Main Goal: {vision_input[:100]}")
        y -= 30
        pdf.drawString(50, y, f"1-Year Goal: {one_year[:100] if one_year else 'N/A'}")
        y -= 30
        pdf.drawString(50, y, f"3-Year Goal: {three_year[:100] if three_year else 'N/A'}")
        y -= 30
        pdf.drawString(50, y, f"5-Year Goal: {five_year[:100] if five_year else 'N/A'}")
        y -= 30
        pdf.drawString(50, y, "Message from Future Self:")
        y -= 20
        for line in future_self.split("\n"):
            pdf.drawString(50, y, line[:100])
            y -= 20
            if y < 100:
                pdf.showPage()
                y = 750
        pdf.save()
        st.download_button("📥 Download Vision PDF", data=buffer.getvalue(), file_name="long_term_vision.pdf")

if __name__ == "__main__":
    run()
