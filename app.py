import streamlit as st
from ai_workout import generate_workout

st.set_page_config(page_title="AI Workout Generator", page_icon="💪")

if "workout_result" not in st.session_state:
    st.session_state.workout_result = None

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

duration = st.selectbox(
    "Workout duration (minutes)",
    [20, 30, 45, 60]
)

focus_area = st.selectbox(
    "Focus area",
    ["full body", "upper body", "lower body", "core"]
)

limitations = st.text_input(
    "Limitations or injuries",
    value="none"
)

st.caption("Tip: Click regenerate to explore different workout variations.")

col1, col2 = st.columns(2)

with col1:
    generate_clicked = st.button("Generate Workout")

with col2:
    regenerate_clicked = st.button("Regenerate 🔄")

if generate_clicked or regenerate_clicked:
    with st.spinner("Generating your workout plan..."):
        result = generate_workout(
            goal,
            experience,
            equipment,
            days,
            duration,
            focus_area,
            limitations
        )

    st.session_state.workout_result = result

if st.session_state.workout_result is not None:
    result = st.session_state.workout_result

    if "error" in result:
        st.error("The workout plan could not be generated correctly. Please try again.")
    else:
        st.success("Your workout plan is ready.")
        st.subheader("Your Workout Plan")

        for day, details in result.items():
            st.markdown(f"### {day.upper()}")
            st.write(f"**Warmup:** {details['warmup']}")
            st.write(f"**Main workout:** {details['main_workout']}")
            st.write(f"**Finisher:** {details['finisher']}")
            st.write(f"**Note:** {details['note']}")
