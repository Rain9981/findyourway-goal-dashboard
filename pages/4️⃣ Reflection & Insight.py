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
        for line in textwrap.wrap(paragraph, width=width):
            if y < 70:
                pdf.showPage()
                pdf.setFont("Helvetica", 10)
                y = 750
            pdf.drawString(x, y, line)
            y -= line_height
        y -= 4
    return y


def run():
    st.title("🧠 Reflection & AI Insight V2")
    st.caption("Reflect weekly, identify patterns, reset your mindset, and choose your next action.")

    defaults = {
        "journal": "",
        "weekly_win": "",
        "weekly_block": "",
        "next_week_focus": "",
        "confidence_level": 7,
        "insight": "",
        "reframe": "",
        "next_action": "",
        "pattern_detected": "",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    st.sidebar.header("🧘 Reflection Guide")
    st.sidebar.markdown("""
**What this tab does:**
- captures weekly reflection
- identifies wins and blockers
- gives AI insight and mindset reframe
- recommends the next action

**Next step after this tab:**
Go to **Goal Summary Dashboard** to review your full journey.
""")

    st.markdown("### 📥 Weekly Check-In")

    journal = st.text_area(
        "📝 Weekly Reflection",
        key="journal",
        height=160,
        placeholder="What happened this week? What progress, challenges, emotions, or lessons showed up?"
    )

    weekly_win = st.text_area(
        "✅ What did you complete or improve this week?",
        key="weekly_win",
        height=90
    )

    weekly_block = st.text_area(
        "⚠️ What blocked or slowed you down?",
        key="weekly_block",
        height=90
    )

    next_week_focus = st.text_area(
        "🎯 What should your focus be next week?",
        key="next_week_focus",
        height=90
    )

    confidence_level = st.slider(
        "Confidence Level for Next Week",
        1,
        10,
        key="confidence_level"
    )

    if st.button("✨ Get AI Weekly Insight"):
        if not journal.strip() and not weekly_win.strip() and not weekly_block.strip():
            st.warning("Please enter your reflection or weekly check-in details first.")
        else:
            with st.spinner("Analyzing your weekly reflection..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a motivational goal coach. Return ONLY valid JSON. No markdown."
                            },
                            {
                                "role": "user",
                                "content": f"""
Analyze this weekly reflection.

Reflection:
{journal}

Weekly Win:
{weekly_win}

Weekly Block:
{weekly_block}

Next Week Focus:
{next_week_focus}

Confidence Level:
{confidence_level}/10

Return JSON:
{{
  "insight": "uplifting but honest feedback",
  "reframe": "mindset reframe",
  "pattern_detected": "pattern or theme noticed",
  "next_action": "one clear action for next week"
}}
"""
                            }
                        ],
                        temperature=0.75
                    )

                    data = json.loads(clean_json(response.choices[0].message.content))

                    st.session_state["insight"] = data.get("insight", "")
                    st.session_state["reframe"] = data.get("reframe", "")
                    st.session_state["pattern_detected"] = data.get("pattern_detected", "")
                    st.session_state["next_action"] = data.get("next_action", "")

                    st.success("✅ AI Insight and Mindset Tune-Up ready.")

                except Exception as e:
                    st.error(f"❌ GPT Error: {e}")

    st.markdown("### 💬 AI Coaching Feedback")

    insight = st.text_area("AI Insight Feedback", key="insight", height=130)
    reframe = st.text_area("Mindset Reframe", key="reframe", height=100)
    pattern_detected = st.text_area("Pattern Detected", key="pattern_detected", height=90)
    next_action = st.text_area("Next Best Action", key="next_action", height=90)

    st.divider()
    st.markdown("### ✅ Recommended Next Step")
    st.info("Next: Go to **Goal Summary Dashboard** to review your SMART goal, 90-day progress, long-term vision, and latest reflection together.")

    if st.button("✅ Save to Google Sheets"):
        save_data("Reflection & Insight", {
            "Reflection": journal,
            "Weekly Win": weekly_win,
            "Weekly Block": weekly_block,
            "Next Week Focus": next_week_focus,
            "Confidence Level": confidence_level,
            "Insight": insight,
            "Reframe": reframe,
            "Pattern Detected": pattern_detected,
            "Next Action": next_action,
            "Date": str(datetime.date.today())
        }, sheet_tab="Reflection & Insight")
        st.success("Saved to Google Sheets ✅")

    if st.button("📄 Export as PDF"):
        buffer = io.BytesIO()
        pdf = pdf_canvas.Canvas(buffer, pagesize=letter)

        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, 750, "Reflection & AI Insight V2")

        pdf.setFont("Helvetica", 10)
        y = 720

        sections = [
            ("Date", str(datetime.date.today())),
            ("Weekly Reflection", journal),
            ("Weekly Win", weekly_win),
            ("Weekly Block", weekly_block),
            ("Next Week Focus", next_week_focus),
            ("Confidence Level", f"{confidence_level}/10"),
            ("AI Insight", insight),
            ("Mindset Reframe", reframe),
            ("Pattern Detected", pattern_detected),
            ("Next Action", next_action)
        ]

        for label, content in sections:
            pdf.setFont("Helvetica-Bold", 11)
            if y < 80:
                pdf.showPage()
                y = 750
            pdf.drawString(50, y, label)
            y -= 16
            pdf.setFont("Helvetica", 10)
            y = pdf_lines(pdf, content if content else "N/A", 50, y)

        pdf.save()
        st.download_button("📥 Download Reflection PDF", data=buffer.getvalue(), file_name="reflection_insight_v2.pdf")


if __name__ == "__main__":
    run()