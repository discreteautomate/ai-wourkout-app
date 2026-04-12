import streamlit as st
from ai_workout import generate_workout
import csv
import os

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

generate_clicked = st.button("Generate Workout")
regenerate_clicked = st.button("Regenerate 🔄")
clear_clicked = st.button("Clear Workout")

if clear_clicked:
    st.session_state.workout_result = None

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

            st.write("**Warmup:**")
            for item in details["warmup"].split(", "):
                st.markdown(f"- {item}")

            st.write("**Main workout:**")
            for item in details["main_workout"].split(", "):
                st.markdown(f"- {item}")

            st.write("**Finisher:**")
            for item in details["finisher"].split(", "):
                st.markdown(f"- {item}")

            st.write(f"**Note:** {details['note']}")

    st.divider()
    st.subheader("Quick Feedback")

    useful = st.radio(
        "Was this workout useful?",
        ["Yes", "No"]
    )

    feedback_text = st.text_input(
        "Anything you'd improve? (optional)"
    )

    if st.button("Submit Feedback"):
        file_exists = os.path.isfile("feedback.csv")

    with open("feedback.csv", mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # Write header only once
        if not file_exists:
            writer.writerow([
                "goal",
                "experience",
                "equipment",
                "days",
                "duration",
                "focus_area",
                "limitations",
                "useful",
                "feedback"
            ])

        writer.writerow([
            goal,
            experience,
            equipment,
            days,
            duration,
            focus_area,
            limitations,
            useful,
            feedback_text
        ])

    st.success("Feedback saved. Thank you 🙌")
