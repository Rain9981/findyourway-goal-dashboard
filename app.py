import streamlit as st

st.set_page_config(page_title="🎯 AI Goal Setting Dashboard", layout="wide")

st.image("logo2Find_You_Way.png", width=250)

st.title("🎯 Welcome to Your AI Goal Dashboard")
st.caption("A guided goal-setting system built to help you define, plan, track, reflect, and grow.")

st.markdown("""
This dashboard helps you move from **idea → structure → execution → reflection → progress review**.

Instead of treating goals like random notes, this system helps you build a complete goal journey.
""")

st.divider()

st.markdown("## 🔄 Goal Journey Flow")

st.markdown("""
**SMART Goal → 90-Day Tracker → Long-Term Vision → Reflection → Summary Dashboard**

- **SMART Goal Planner:** clarify the goal
- **90-Day Tracker:** break it into weekly execution
- **Long-Term Vision:** connect it to your 1, 3, and 5-year future
- **Reflection & Insight:** review progress and adjust
- **Summary Dashboard:** see everything in one place
""")

st.divider()

st.markdown("## 🚀 Start Here")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("**New Goal?** Start with the SMART Goal Planner.")

with col2:
    st.info("**Need Action Steps?** Move to the 90-Day Tracker.")

with col3:
    st.info("**Need Review?** Open the Summary Dashboard.")

st.divider()

st.markdown("## 🧠 What This App Helps You Do")

st.markdown("""
- Create clearer goals
- Turn goals into weekly action
- Build long-term vision
- Reflect with AI feedback
- Track progress over time
- Stay aligned with your future self
""")

st.success("Use the left sidebar to begin. Start with the SMART Goal Planner if you're new.")