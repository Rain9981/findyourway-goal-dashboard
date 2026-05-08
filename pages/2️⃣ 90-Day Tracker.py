import streamlit as st
st.image("logo2Find_You_Way.png", width=250)

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from openai import OpenAI
from backend.google_sheets import save_data
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.pagesizes import letter
import datetime
import io
import textwrap

client = OpenAI(api_key=st.secrets["openai"]["api_key"])


def write_pdf_lines(pdf, text, x, y, width=95, line_height=14):
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
    st.title("📅 90-Day Tracker V2")
    st.caption("Break one goal into a complete 12-week execution plan with progress tracking.")

    if "goal_input" not in st.session_state:
        st.session_state["goal_input"] = ""

    if "tracker_review" not in st.session_state:
        st.session_state["tracker_review"] = ""

    for i in range(1, 13):
        if f"week_{i}" not in st.session_state:
            st.session_state[f"week_{i}"] = ""
        if f"week_{i}_done" not in st.session_state:
            st.session_state[f"week_{i}_done"] = False

    st.sidebar.header("🧠 90-Day Tracker Guide")
    st.sidebar.markdown("""
**What this tab does:**
- turns one goal into 12 weekly milestones
- tracks weekly completion
- gives pacing tips with AI
- saves to Google Sheets
- exports to PDF
""")

    goal_input = st.text_area(
        "Your 90-day goal",
        key="goal_input",
        height=120,
        placeholder="Example: Launch a personal brand with strong online presence and consistent lead flow."
    )

    if st.button("✨ Autofill 12-Week Plan with AI"):
        if not goal_input.strip():
            st.warning("Please enter a 90-day goal first.")
        else:
            try:
                with st.spinner("Generating 12-week plan..."):
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a 90-day goal planner. Create exactly 12 labeled weeks. Keep each week practical and clear."
                            },
                            {
                                "role": "user",
                                "content": (
                                    "Create a 12-week plan for this goal. "
                                    "Use exactly this format for each week:\n\n"
                                    "Week 1:\nFocus:\nAction Steps:\n- \n- \n- \nSuccess Marker:\n\n"
                                    "Continue through Week 12. Do not skip weeks.\n\n"
                                    f"Goal: {goal_input}"
                                )
                            }
                        ],
                        temperature=0.7
                    )

                    content = response.choices[0].message.content

                    for i in range(1, 13):
                        start_marker = f"Week {i}:"
                        end_marker = f"Week {i + 1}:" if i < 12 else None

                        if start_marker in content:
                            start_index = content.find(start_marker)
                            if end_marker and end_marker in content:
                                end_index = content.find(end_marker)
                                week_text = content[start_index:end_index].strip()
                            else:
                                week_text = content[start_index:].strip()

                            st.session_state[f"week_{i}"] = week_text
                        else:
                            st.session_state[f"week_{i}"] = (
                                f"Week {i}:\n"
                                f"Focus: Build momentum toward the 90-day goal.\n"
                                f"Action Steps:\n"
                                f"- Define the most important action for this week.\n"
                                f"- Complete one measurable task tied to the goal.\n"
                                f"- Review progress and prepare for the next week.\n"
                                f"Success Marker: Week {i} progress is documented."
                            )

                        st.session_state[f"week_{i}_done"] = False

                    st.success("✅ 12-week plan generated.")
                    st.rerun()

            except Exception as e:
                st.error(f"❌ GPT Error: {e}")

    completed_weeks = sum(
        1 for i in range(1, 13)
        if st.session_state.get(f"week_{i}_done", False)
    )

    progress_percent = int((completed_weeks / 12) * 100)

    st.markdown("### 📊 Progress Overview")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Weeks Complete", f"{completed_weeks}/12")
    with col2:
        st.metric("Progress", f"{progress_percent}%")

    st.progress(progress_percent / 100)

    st.markdown("### 📋 12-Week Action Plan")

    weeks = {}

    for i in range(1, 13):
        st.markdown(f"#### Week {i}")

        weeks[f"week_{i}"] = st.text_area(
            f"Plan for Week {i}",
            key=f"week_{i}",
            height=140
        )

        st.checkbox(
            f"Week {i} Complete",
            key=f"week_{i}_done"
        )

    if st.button("🧠 Get GPT Review & Pacing Tips"):
        try:
            with st.spinner("Reviewing your plan..."):
                combined_plan = "\n\n".join(
                    [
                        f"Week {i} | Complete: {st.session_state.get(f'week_{i}_done', False)}\n{weeks[f'week_{i}']}"
                        for i in range(1, 13)
                    ]
                )

                review = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": "You review 90-day plans for pacing, realism, progress, and execution strength."
                        },
                        {
                            "role": "user",
                            "content": (
                                f"Goal: {goal_input}\n"
                                f"Progress: {completed_weeks}/12 weeks complete\n\n"
                                f"{combined_plan}\n\n"
                                "Return:\n"
                                "1. Current Progress Read\n"
                                "2. Pacing Strength\n"
                                "3. Missing or Weak Areas\n"
                                "4. Best Next Adjustment\n"
                                "5. Encouraging Coaching Note"
                            )
                        }
                    ],
                    temperature=0.7
                )

                st.session_state["tracker_review"] = review.choices[0].message.content
                st.success("✅ Review complete.")

        except Exception as e:
            st.error(f"❌ GPT Error: {e}")

    if st.session_state.get("tracker_review"):
        st.markdown("### 🧠 Latest Review")
        st.info(st.session_state["tracker_review"])

    st.divider()
    st.info("Next: Go to **Long-Term Vision** to connect this 90-day plan to your 1-year, 3-year, and 5-year path.")

    if st.button("✅ Save to Google Sheets"):
        try:
            completed_weeks = sum(
                1 for i in range(1, 13)
                if st.session_state.get(f"week_{i}_done", False)
            )
            progress_percent = int((completed_weeks / 12) * 100)

            save_data(
                "90-Day Tracker",
                {
                    "Goal Description": goal_input,
                    **{f"Week {i}": weeks[f"week_{i}"] for i in range(1, 13)},
                    **{f"Week {i} Complete": st.session_state.get(f"week_{i}_done", False) for i in range(1, 13)},
                    "Weeks Complete": completed_weeks,
                    "Progress Percent": progress_percent,
                    "GPT Review": st.session_state.get("tracker_review", ""),
                    "Date": str(datetime.date.today())
                },
                sheet_tab="90-Day Tracker"
            )

            st.success("Saved to Google Sheets ✅")

        except Exception as e:
            st.error(f"Google Sheets save failed: {e}")

    if st.button("📄 Export as PDF"):
        buffer = io.BytesIO()
        pdf = pdf_canvas.Canvas(buffer, pagesize=letter)

        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, 750, "90-Day Tracker Plan V2")
        pdf.setFont("Helvetica", 10)

        y = 720
        y = write_pdf_lines(pdf, f"Goal: {goal_input}", 50, y)
        y = write_pdf_lines(pdf, f"Progress: {completed_weeks}/12 weeks complete ({progress_percent}%)", 50, y)

        for i in range(1, 13):
            if y < 90:
                pdf.showPage()
                y = 750

            status = "Complete" if st.session_state.get(f"week_{i}_done", False) else "Not Complete"

            pdf.setFont("Helvetica-Bold", 11)
            pdf.drawString(50, y, f"Week {i} - {status}")
            y -= 16

            pdf.setFont("Helvetica", 10)
            y = write_pdf_lines(pdf, weeks[f"week_{i}"], 50, y)

        if st.session_state.get("tracker_review"):
            if y < 90:
                pdf.showPage()
                y = 750

            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(50, y, "GPT Review")
            y -= 18

            pdf.setFont("Helvetica", 10)
            y = write_pdf_lines(pdf, st.session_state["tracker_review"], 50, y)

        pdf.save()

        st.download_button(
            "📥 Download 90-Day Plan PDF",
            data=buffer.getvalue(),
            file_name="90_day_plan_v2.pdf"
        )


if __name__ == "__main__":
    run()