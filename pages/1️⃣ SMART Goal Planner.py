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


def write_wrapped_pdf(pdf, label, content, y):
    pdf.setFont("Helvetica-Bold", 11)

    if y < 80:
        pdf.showPage()
        y = 750

    pdf.drawString(50, y, label)
    y -= 16

    pdf.setFont("Helvetica", 10)
    text = str(content) if content else "N/A"

    for line in textwrap.wrap(text, width=90):
        if y < 70:
            pdf.showPage()
            pdf.setFont("Helvetica", 10)
            y = 750
        pdf.drawString(50, y, line)
        y -= 14

    y -= 8
    return y


def run():
    st.title("📌 SMART Goal Planner V2")
    st.caption("Build a goal that is clear, measurable, realistic, relevant, and time-bound.")

    for key in [
        "specific",
        "measurable",
        "achievable",
        "relevant",
        "time_bound",
        "smart_review",
        "goal_score",
        "execution_readiness",
        "main_risk",
        "best_next_action"
    ]:
        if key not in st.session_state:
            st.session_state[key] = ""

    st.sidebar.header("🧠 SMART Goal Guide")
    st.sidebar.markdown("""
**What this tab does:**
- helps define a strong SMART goal
- gives AI feedback on clarity and execution
- creates readiness scores and next steps

**Next step after this tab:**
Go to **90-Day Tracker** to break this goal into 12 weekly action steps.
""")

    if st.button("✨ Autofill with AI"):
        with st.spinner("Generating example SMART goal..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a SMART goal strategist. Return ONLY valid JSON. No markdown."
                        },
                        {
                            "role": "user",
                            "content": """
Create a strong business SMART goal.

Return JSON only:
{
  "specific": "",
  "measurable": "",
  "achievable": "",
  "relevant": "",
  "time_bound": ""
}
"""
                        }
                    ],
                    temperature=0.7
                )

                data = json.loads(clean_json(response.choices[0].message.content))

                st.session_state["specific"] = data.get("specific", "")
                st.session_state["measurable"] = data.get("measurable", "")
                st.session_state["achievable"] = data.get("achievable", "")
                st.session_state["relevant"] = data.get("relevant", "")
                st.session_state["time_bound"] = data.get("time_bound", "")

                st.success("✅ SMART goal example filled.")
                st.rerun()

            except Exception as e:
                st.error(f"❌ GPT Error: {e}")

    st.markdown("### 📥 SMART Goal Components")

    specific = st.text_area("Specific", key="specific", height=90)
    measurable = st.text_area("Measurable", key="measurable", height=90)
    achievable = st.text_area("Achievable", key="achievable", height=90)
    relevant = st.text_area("Relevant", key="relevant", height=90)
    time_bound = st.text_area("Time-Bound", key="time_bound", height=90)

    if st.button("🧠 Get AI Goal Review"):
        with st.spinner("Reviewing your SMART goal..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a SMART goal reviewer and execution coach. Return ONLY valid JSON."
                        },
                        {
                            "role": "user",
                            "content": f"""
Review this SMART goal.

Specific: {specific}
Measurable: {measurable}
Achievable: {achievable}
Relevant: {relevant}
Time-Bound: {time_bound}

Return JSON:
{{
  "goal_score": "score out of 10",
  "execution_readiness": "Low, Medium, or High",
  "main_risk": "main risk",
  "best_next_action": "best next action",
  "review": "short but powerful review"
}}
"""
                        }
                    ],
                    temperature=0.7
                )

                data = json.loads(clean_json(response.choices[0].message.content))

                st.session_state["goal_score"] = data.get("goal_score", "")
                st.session_state["execution_readiness"] = data.get("execution_readiness", "")
                st.session_state["main_risk"] = data.get("main_risk", "")
                st.session_state["best_next_action"] = data.get("best_next_action", "")
                st.session_state["smart_review"] = data.get("review", "")

                st.success("✅ Goal review complete.")

            except Exception as e:
                st.error(f"❌ GPT Error: {e}")

    if st.session_state.get("smart_review"):
        st.markdown("### 🧠 AI Goal Review")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Goal Clarity Score", st.session_state.get("goal_score", ""))
        with col2:
            st.metric("Execution Readiness", st.session_state.get("execution_readiness", ""))

        st.warning(f"**Main Risk:** {st.session_state.get('main_risk', '')}")
        st.success(f"**Best Next Action:** {st.session_state.get('best_next_action', '')}")
        st.info(st.session_state.get("smart_review", ""))

    st.divider()
    st.markdown("### ✅ Recommended Next Step")
    st.info("Next: Go to **90-Day Tracker** to turn this SMART goal into a 12-week action plan.")

    if st.button("✅ Save to Google Sheets"):
        try:
            save_data("SMART Goal Planner", {
                "Specific": specific,
                "Measurable": measurable,
                "Achievable": achievable,
                "Relevant": relevant,
                "Time-Bound": time_bound,
                "Goal Score": st.session_state.get("goal_score", ""),
                "Execution Readiness": st.session_state.get("execution_readiness", ""),
                "Main Risk": st.session_state.get("main_risk", ""),
                "Best Next Action": st.session_state.get("best_next_action", ""),
                "AI Review": st.session_state.get("smart_review", ""),
                "Date": str(datetime.date.today())
            }, sheet_tab="SMART Goal Planner")
            st.success("Saved to Google Sheets ✅")
        except Exception as e:
            st.warning(f"Could not save to Google Sheets: {e}")

    if st.button("📄 Export as PDF"):
        buffer = io.BytesIO()
        pdf = pdf_canvas.Canvas(buffer, pagesize=letter)

        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, 750, "SMART Goal Planner V2")

        y = 720

        sections = [
            ("Specific", specific),
            ("Measurable", measurable),
            ("Achievable", achievable),
            ("Relevant", relevant),
            ("Time-Bound", time_bound),
            ("Goal Score", st.session_state.get("goal_score", "")),
            ("Execution Readiness", st.session_state.get("execution_readiness", "")),
            ("Main Risk", st.session_state.get("main_risk", "")),
            ("Best Next Action", st.session_state.get("best_next_action", "")),
            ("AI Review", st.session_state.get("smart_review", ""))
        ]

        for label, content in sections:
            y = write_wrapped_pdf(pdf, label, content, y)

        pdf.save()

        st.download_button(
            "📥 Download SMART Goal PDF",
            data=buffer.getvalue(),
            file_name="smart_goal_v2.pdf"
        )


if __name__ == "__main__":
    run()