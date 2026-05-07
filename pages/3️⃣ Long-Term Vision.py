import streamlit as st
st.image("logo2Find_You_Way.png", width=250)

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
import textwrap

client = OpenAI(api_key=st.secrets["openai"]["api_key"])


def clean_json(content):
    return content.replace("```json", "").replace("```", "").strip()


def pdf_lines(pdf, text, x, y, width=95, line_height=14):
    for paragraph in str(text).split("\n"):
        for line in textwrap.wrap(str(paragraph), width=width):
            if y < 70:
                pdf.showPage()
                pdf.setFont("Helvetica", 10)
                y = 750
            pdf.drawString(x, y, line)
            y -= line_height
        y -= 4
    return y


def build_fallback_vision(goal):
    return {
        "one_year": f"Within 1 year, build strong momentum toward: {goal}",
        "three_year": f"Within 3 years, expand this goal into a stable system with stronger habits, structure, and measurable progress.",
        "five_year": f"Within 5 years, turn this vision into a mature lifestyle, business, or personal achievement with lasting impact.",
        "future_self": "You made it because you stopped treating the goal like an idea and started treating it like a commitment. You built structure, followed through week by week, adjusted when needed, and became the type of person who could sustain the vision."
    }


def run():
    st.title("🚀 Long-Term Vision Planner V2")
    st.caption("Build a 1-year, 3-year, and 5-year vision with a future-self reflection.")

    for key in ["one_year", "three_year", "five_year", "future_self", "vision_input"]:
        if key not in st.session_state:
            st.session_state[key] = ""

    st.sidebar.header("🧠 Long-Term Vision Guide")
    st.sidebar.markdown("""
**What this tab does:**
- builds a 1-year, 3-year, and 5-year vision
- creates a future-self message
- can pull from SMART Goal or 90-Day Goal if those were entered during this session

**Important:**
If you refreshed the app or opened this page first, session data from SMART/90-Day may not exist yet. In that case, use Custom Input.
""")

    goal_source = st.selectbox(
        "Source of your main goal",
        ["Custom Input", "SMART Goal", "90-Day Goal"],
        key="vision_goal_source"
    )

    smart_goal = st.session_state.get("specific", "")
    ninety_day_goal = st.session_state.get("goal_input", "")

    if goal_source == "SMART Goal":
        if smart_goal:
            st.session_state["vision_input"] = smart_goal
            st.success("SMART Goal found from this session.")
        else:
            st.warning("No SMART Goal found in this session. Enter a custom goal below or return to SMART Goal Planner first.")

    elif goal_source == "90-Day Goal":
        if ninety_day_goal:
            st.session_state["vision_input"] = ninety_day_goal
            st.success("90-Day Goal found from this session.")
        else:
            st.warning("No 90-Day Goal found in this session. Enter a custom goal below or return to 90-Day Tracker first.")

    vision_input = st.text_area(
        "Main Vision Goal",
        key="vision_input",
        height=120,
        placeholder="Describe the long-term goal you want to build toward."
    )

    show_raw = st.checkbox("Show GPT raw output/debug", value=False)

    if st.button("✨ Autofill Vision Goals with GPT"):
        if not vision_input.strip():
            st.warning("Please enter or select a goal first.")
        else:
            with st.spinner("Generating long-term vision..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a visionary goal coach. Return ONLY valid JSON. No markdown, no code fences, no explanation."
                            },
                            {
                                "role": "user",
                                "content": f"""
Create a 1-year, 3-year, and 5-year vision plan from this goal.

Goal:
{vision_input}

Return EXACTLY this JSON:

{{
  "one_year": "clear 1-year goal",
  "three_year": "clear 3-year goal",
  "five_year": "clear 5-year goal",
  "future_self": "motivational paragraph from the user's future self"
}}

Rules:
- Return JSON only.
- Fill every field.
- Make the vision inspiring but practical.
"""
                            }
                        ],
                        temperature=0.65
                    )

                    raw = response.choices[0].message.content.strip()

                    if show_raw:
                        st.markdown("#### 🔍 GPT Raw Output")
                        st.code(raw)

                    try:
                        data = json.loads(clean_json(raw))
                    except Exception:
                        st.warning("GPT did not return clean JSON. Using fallback structure.")
                        data = build_fallback_vision(vision_input)

                    st.session_state["one_year"] = data.get("one_year") or build_fallback_vision(vision_input)["one_year"]
                    st.session_state["three_year"] = data.get("three_year") or build_fallback_vision(vision_input)["three_year"]
                    st.session_state["five_year"] = data.get("five_year") or build_fallback_vision(vision_input)["five_year"]
                    st.session_state["future_self"] = data.get("future_self") or build_fallback_vision(vision_input)["future_self"]

                    st.success("✅ Vision goals and reflection filled successfully.")
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ GPT Error: {e}")

    one_year = st.text_area("1-Year Goal", key="one_year", height=100)
    three_year = st.text_area("3-Year Goal", key="three_year", height=100)
    five_year = st.text_area("5-Year Goal", key="five_year", height=100)
    future_self = st.text_area("🪞 Message from Your Future Self", key="future_self", height=160)

    st.divider()
    st.info("Next: Go to **Reflection & Insight** to review progress and receive weekly coaching feedback.")

    if st.button("✅ Save to Google Sheets"):
        try:
            save_data("Long-Term Vision", {
                "Source Goal": vision_input,
                "1-Year": one_year,
                "3-Year": three_year,
                "5-Year": five_year,
                "Future Self": future_self,
                "Date": str(datetime.date.today())
            }, sheet_tab="Long-Term Vision")
            st.success("Saved to Google Sheets ✅")
        except Exception as e:
            st.warning(f"Could not save to Google Sheets: {e}")

    if st.button("📄 Export as PDF"):
        buffer = io.BytesIO()
        pdf = pdf_canvas.Canvas(buffer, pagesize=letter)

        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, 750, "Long-Term Vision Plan V2")
        pdf.setFont("Helvetica", 10)

        y = 720
        y = pdf_lines(pdf, f"Main Goal: {vision_input}", 50, y)
        y = pdf_lines(pdf, f"1-Year Goal: {one_year}", 50, y)
        y = pdf_lines(pdf, f"3-Year Goal: {three_year}", 50, y)
        y = pdf_lines(pdf, f"5-Year Goal: {five_year}", 50, y)
        y = pdf_lines(pdf, f"Message from Future Self:\n{future_self}", 50, y)

        pdf.save()
        st.download_button("📥 Download Vision PDF", data=buffer.getvalue(), file_name="long_term_vision_v2.pdf")


if __name__ == "__main__":
    run()