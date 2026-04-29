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
- adds action steps and success markers
- tracks weekly completion
- gives pacing tips with AI

**Next step after this tab:**
Go to **Long-Term Vision** to connect this 90-day goal to your future path.
""")

    goal_input = st.text_area(
        "Your 90-day goal",
        key="goal_input",
        height=120,
        placeholder="Example: Launch a personal brand with strong online presence and consistent lead flow."
    )

    show_raw = st.checkbox("Show GPT raw output/debug", value=False)

    if st.button("✨ Autofill 12-Week Plan with AI"):
        if not goal_input.strip():
            st.warning("Please enter a 90-day goal first.")
        else:
            with st.spinner("Generating complete 12-week plan..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a 90-day goal planner. Return ONLY valid JSON. Do not include markdown, explanations, bullets outside JSON, or code fences."
                            },
                            {
                                "role": "user",
                                "content": f"""
Create a complete 12-week plan for this 90-day goal.

Goal:
{goal_input}

Return EXACTLY this JSON structure:

{{
  "weeks": [
    {{
      "week": 1,
      "focus": "short focus title",
      "action_steps": ["step 1", "step 2", "step 3"],
      "success_marker": "what proves this week moved forward"
    }},
    {{
      "week": 2,
      "focus": "short focus title",
      "action_steps": ["step 1", "step 2", "step 3"],
      "success_marker": "what proves this week moved forward"
    }},
    {{
      "week": 3,
      "focus": "short focus title",
      "action_steps": ["step 1", "step 2", "step 3"],
      "success_marker": "what proves this week moved forward"
    }},
    {{
      "week": 4,
      "focus": "short focus title",
      "action_steps": ["step 1", "step 2", "step 3"],
      "success_marker": "what proves this week moved forward"
    }},
    {{
      "week": 5,
      "focus": "short focus title",
      "action_steps": ["step 1", "step 2", "step 3"],
      "success_marker": "what proves this week moved forward"
    }},
    {{
      "week": 6,
      "focus": "short focus title",
      "action_steps": ["step 1", "step 2", "step 3"],
      "success_marker": "what proves this week moved forward"
    }},
    {{
      "week": 7,
      "focus": "short focus title",
      "action_steps": ["step 1", "step 2", "step 3"],
      "success_marker": "what proves this week moved forward"
    }},
    {{
      "week": 8,
      "focus": "short focus title",
      "action_steps": ["step 1", "step 2", "step 3"],
      "success_marker": "what proves this week moved forward"
    }},
    {{
      "week": 9,
      "focus": "short focus title",
      "action_steps": ["step 1", "step 2", "step 3"],
      "success_marker": "what proves this week moved forward"
    }},
    {{
      "week": 10,
      "focus": "short focus title",
      "action_steps": ["step 1", "step 2", "step 3"],
      "success_marker": "what proves this week moved forward"
    }},
    {{
      "week": 11,
      "focus": "short focus title",
      "action_steps": ["step 1", "step 2", "step 3"],
      "success_marker": "what proves this week moved forward"
    }},
    {{
      "week": 12,
      "focus": "short focus title",
      "action_steps": ["step 1", "step 2", "step 3"],
      "success_marker": "what proves this week moved forward"
    }}
  ]
}}

Rules:
- MUST include weeks 1 through 12.
- Do not skip any week.
- Every week must include focus, exactly 3 action steps, and a success marker.
- Return JSON only.
"""
                            }
                        ],
                        temperature=0.4
                    )

                    raw = response.choices[0].message.content.strip()

                    if show_raw:
                        st.markdown("### 🔍 Raw GPT Output")
                        st.code(raw)

                    weeks = []

                    try:
                        data = json.loads(clean_json(raw))
                        weeks = data.get("weeks", [])
                    except Exception:
                        st.warning("⚠️ GPT did not return clean JSON. Fallback structure was used.")

                    # Guaranteed fill for all 12 weeks
                    for i in range(1, 13):
                        item = next(
                            (
                                w for w in weeks
                                if str(w.get("week", "")).strip() == str(i)
                            ),
                            {}
                        )

                        focus = item.get("focus", f"Week {i} Execution Focus")
                        actions = item.get("action_steps", [])

                        if not isinstance(actions, list) or len(actions) < 3:
                            actions = [
                                f"Clarify the most important task for week {i}.",
                                f"Complete the main action step connected to the 90-day goal.",
                                f"Review progress and prepare the next step."
                            ]

                        marker = item.get(
                            "success_marker",
                            f"Week {i} progress is documented and the next move is clear."
                        )

                        formatted = f"Focus: {focus}\n"
                        formatted += "Action Steps:\n"
                        formatted += f"- {actions[0]}\n"
                        formatted += f"- {actions[1]}\n"
                        formatted += f"- {actions[2]}\n"
                        formatted += f"Success Marker: {marker}"

                        st.session_state[f"week_{i}"] = formatted
                        st.session_state[f"week_{i}_done"] = False

                    st.success("✅ Full 12-week plan generated.")
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ GPT Error: {e}")

    st.markdown("### 📊 Progress Overview")

    completed_weeks = sum(
        1 for i in range(1, 13)
        if st.session_state.get(f"week_{i}_done", False)
    )
    progress_percent = int((completed_weeks / 12) * 100)

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
            height=135
        )

        st.checkbox(
            f"Week {i} Complete",
            key=f"week_{i}_done"
        )

    if st.button("🧠 Get GPT Review & Pacing Tips"):
        with st.spinner("Reviewing your 90-day plan..."):
            try:
                completed_weeks = sum(
                    1 for i in range(1, 13)
                    if st.session_state.get(f"week_{i}_done", False)
                )

                combined_plan = "\n\n".join([
                    f"Week {i} | Complete: {st.session_state.get(f'week_{i}_done', False)}\n{weeks[f'week_{i}']}"
                    for i in range(1, 13)
                ])

                review = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": "You review 90-day plans for pacing, realism, progress, missing steps, and execution strength."
                        },
                        {
                            "role": "user",
                            "content": f"""
Review this 90-day plan and give clear pacing tips.

Goal:
{goal_input}

Progress:
{completed_weeks}/12 weeks complete

Plan:
{combined_plan}

Return:
1. Current Progress Read
2. Pacing Strength
3. Missing or Weak Areas
4. Best Next Adjustment
5. Encouraging Coaching Note
"""
                        }
                    ],
                    temperature=0.7
                )

                st.session_state["tracker_review"] = review.choices[0].message.content

                st.success("✅ Review complete.")
                st.info(st.session_state["tracker_review"])

            except Exception as e:
                st.error(f"❌ GPT Error: {e}")

    if st.session_state.get("tracker_review"):
        st.markdown("### 🧠 Latest Review")
        st.info(st.session_state["tracker_review"])

    st.divider()

    st.markdown("### ✅ Recommended Next Step")
    st.info("Next: Go to **Long-Term Vision** to connect this 90-day plan to your 1-year, 3-year, and 5-year path.")

    if st.button("✅ Save to Google Sheets"):
        completed_weeks = sum(
            1 for i in range(1, 13)
            if st.session_state.get(f"week_{i}_done", False)
        )
        progress_percent = int((completed_weeks / 12) * 100)

        save_data("90-Day Tracker", {
            "Goal Description": goal_input,
            **{f"Week {i}": weeks[f"week_{i}"] for i in range(1, 13)},
            **{f"Week {i} Complete": st.session_state.get(f"week_{i}_done", False) for i in range(1, 13)},
            "Weeks Complete": completed_weeks,
            "Progress Percent": progress_percent,
            "GPT Review": st.session_state.get("tracker_review", ""),
            "Date": str(datetime.date.today())
        }, sheet_tab="90-Day Tracker")

        st.success("Saved to Google Sheets ✅")

    if st.button("📄 Export as PDF"):
        buffer = io.BytesIO()
        pdf = pdf_canvas.Canvas(buffer, pagesize=letter)

        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, 750, "90-Day Tracker Plan V2")
        pdf.setFont("Helvetica", 10)

        y = 720

        completed_weeks = sum(
            1 for i in range(1, 13)
            if st.session_state.get(f"week_{i}_done", False)
        )
        progress_percent = int((completed_weeks / 12) * 100)

        y = pdf_lines(pdf, f"Goal: {goal_input}", 50, y)
        y = pdf_lines(pdf, f"Progress: {completed_weeks}/12 weeks complete ({progress_percent}%)", 50, y)

        for i in range(1, 13):
            pdf.setFont("Helvetica-Bold", 11)

            if y < 90:
                pdf.showPage()
                y = 750

            status = "Complete" if st.session_state.get(f"week_{i}_done", False) else "Not Complete"
            pdf.drawString(50, y, f"Week {i} - {status}")
            y -= 16

            pdf.setFont("Helvetica", 10)
            y = pdf_lines(pdf, weeks[f"week_{i}"], 50, y)

        if st.session_state.get("tracker_review"):
            pdf.setFont("Helvetica-Bold", 12)

            if y < 90:
                pdf.showPage()
                y = 750

            pdf.drawString(50, y, "GPT Review")
            y -= 18

            pdf.setFont("Helvetica", 10)
            y = pdf_lines(pdf, st.session_state["tracker_review"], 50, y)

        pdf.save()

        st.download_button(
            "📥 Download 90-Day Plan PDF",
            data=buffer.getvalue(),
            file_name="90_day_plan_v2.pdf"
        )


if __name__ == "__main__":
    run()