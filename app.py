import streamlit as st
st.write("VERSION TEST 123")
from ai_workout import generate_workout

st.set_page_config(page_title="AI Workout Generator", page_icon="💪")

st.title("AI Workout Generator 💪")
st.write("Create a personalized workout plan in seconds.")

goal = st.selectbox(
    "Select your goal",
    ["fat loss", "muscle gain", "strength"]
)

experience = st.selectbox(
    "Select your experience level",
    ["beginner", "intermediate", "advanced"]
)

equipment = st.selectbox(
    "Select available equipment",
    ["bodyweight", "gym", "dumbbells"]
)

days = st.slider("Number of days", 1, 7, 3)

st.caption("Tip: Click regenerate to explore different workout variations.")

if st.button("Generate Workout") or st.button("Regenerate 🔄"):
    with st.spinner("Generating your workout plan..."):
        result = generate_workout(goal, experience, equipment, days)

    st.write(result)

    if "error" in result:
        st.error("The workout plan could not be generated correctly.")
        st.write(result)
    else:
        st.success("Your workout plan is ready.")
        st.subheader("Your Workout Plan")

        for day, details in result.items():
            st.markdown(f"### {day.upper()}")
            st.write(f"**Warmup:** {details['warmup']}")
            st.write(f"**Main workout:** {details['main_workout']}")
            st.write(f"**Finisher:** {details['finisher']}")
            st.write(f"**Note:** {details['note']}")
            st.write(f"**Main workout:** {details['main_workout']}")
            st.write(f"**Finisher:** {details['finisher']}")
            st.write(f"**Note:** {details['note']}")
