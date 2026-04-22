import streamlit as st
import csv
import os
import json
from datetime import datetime
from ai_workout import generate_workout, EXERCISE_IMAGES

def find_exercise_image(exercise_text):
    exercise_text = exercise_text.lower()

    for exercise_name, image_url in EXERCISE_IMAGES.items():
        if exercise_name in exercise_text:
            return exercise_name, image_url

    return None, None

def render_exercise_card(item):
    exercise = item.get("exercise", "Unknown exercise")
    details = item.get("details", "")
    image_url = item.get("image")

    col1, col2 = st.columns([1, 2])

    with col1:
        if image_url:
            st.image(image_url, use_container_width=True)

    with col2:
        st.markdown(f"**{exercise.title()}**")
        st.write(details)

    st.markdown("---")


def section_to_text(items):
    lines = []
    for item in items:
        exercise = item.get("exercise", "")
        details = item.get("details", "")
        lines.append(f"- {exercise}: {details}")
    return lines

st.set_page_config(page_title="AI Workout Generator", page_icon="💪")

SAVED_PLANS_FILE = "saved_plans.json"
FEEDBACK_FILE = "feedback.csv"


def load_saved_plans():
    if os.path.exists(SAVED_PLANS_FILE):
        try:
            with open(SAVED_PLANS_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return {}
    return {}


def save_saved_plans(data):
    with open(SAVED_PLANS_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def save_plan_for_user(user_id, inputs, plan):
    all_plans = load_saved_plans()

    if user_id not in all_plans:
        all_plans[user_id] = []

    new_entry = {
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "inputs": inputs,
        "plan": plan
    }

    all_plans[user_id].insert(0, new_entry)
    all_plans[user_id] = all_plans[user_id][:3]

    save_saved_plans(all_plans)


def get_user_plans(user_id):
    all_plans = load_saved_plans()
    return all_plans.get(user_id, [])


def clear_user_plans(user_id):
    all_plans = load_saved_plans()
    if user_id in all_plans:
        del all_plans[user_id]
        save_saved_plans(all_plans)


def format_plan_as_text(plan):
    lines = []

    for day, details in plan.items():
        if not isinstance(details, dict):
            continue

        lines.append(f"{day.upper()}")
        lines.append("Warmup:")
        for item in details["warmup"].split(", "):
            lines.append(f"- {item}")

        lines.append("Main workout:")
        for item in details["main_workout"].split(", "):
            lines.append(f"- {item}")

        lines.append("Finisher:")
        for item in details["finisher"].split(", "):
            lines.append(f"- {item}")

        lines.append(f"Note: {details['note']}")
        lines.append("")

    return "\n".join(lines)


if "workout_result" not in st.session_state:
    st.session_state.workout_result = None

if "loaded_user" not in st.session_state:
    st.session_state.loaded_user = ""

st.title("AI Workout Generator 💪")
st.write("Create a personalized workout plan in seconds.")

user_id = st.text_input("Enter your email or username to save your plans").strip().lower()

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

exclude = st.multiselect(
    "Exclude exercises",
    ["plank", "burpees", "squats", "lunges", "push-ups"]
)

st.caption("Tip: Click regenerate to explore different workout variations.")

# Auto-load latest saved plan when user changes
if user_id != st.session_state.loaded_user:
    user_plans = get_user_plans(user_id) if user_id else []
    st.session_state.workout_result = user_plans[0]["plan"] if user_plans else None
    st.session_state.loaded_user = user_id

col1, col2, col3, col4 = st.columns(4)

with col1:
    generate_clicked = st.button("Generate Workout", use_container_width=True)

with col2:
    regenerate_clicked = st.button("Regenerate 🔄", use_container_width=True)

with col3:
    clear_current_clicked = st.button("Clear Workout", use_container_width=True)

with col4:
    clear_saved_clicked = st.button("Clear Saved", use_container_width=True)

if clear_current_clicked:
    st.session_state.workout_result = None
    st.success("Current workout cleared.")

if clear_saved_clicked:
    if user_id:
        clear_user_plans(user_id)
        st.session_state.workout_result = None
        st.success("Saved plans cleared.")
    else:
        st.warning("Enter your email or username first.")

if generate_clicked or regenerate_clicked:
    with st.spinner("Generating your workout plan..."):
        result = generate_workout(
            goal,
            experience,
            equipment,
            days,
            duration,
            focus_area,
            limitations,
            exclude
        )

    st.session_state.workout_result = result

    if user_id and "error" not in result:
        inputs = {
            "goal": goal,
            "experience": experience,
            "equipment": equipment,
            "days": days,
            "duration": duration,
            "focus_area": focus_area,
            "limitations": limitations,
            "exclude": exclude
        }
        save_plan_for_user(user_id, inputs, result)

if st.session_state.workout_result is not None:
    result = st.session_state.workout_result

    if "error" in result:
        st.error("The workout plan could not be generated correctly. Please try again.")
        if "raw_output" in result:
            with st.expander("Show raw AI output"):
                st.code(result["raw_output"], language="json")
    else:
        st.success("Your workout plan is ready.")
        st.subheader("Your Workout Plan")

        for day, details in result.items():
            if not isinstance(details, dict):
                continue

            st.markdown(f"### {day.upper()}")

            st.write("**Warmup:**")
            for item in details["warmup"]:
                render_exercise_card(item)

                exercise_name, image_url = find_exercise_image(item)
                if image_url:
                    st.image(image_url, width=220)
                    st.caption(exercise_name.title())

            st.write("**Main workout:**")
            for item in details["main_workout"]:
                render_exercise_card(item)

            st.write("**Finisher:**")
            for item in details["finisher"]:
                render_exercise_card(item)

                exercise_name, image_url = find_exercise_image(item)
                if image_url:
                    st.image(image_url, width=220)
                    st.caption(exercise_name.title())

            st.write(f"**Note:** {details['note']}")

        st.divider()

        download_col1, download_col2 = st.columns(2)

        with download_col1:
            st.download_button(
                label="Download Current Plan as JSON",
                data=json.dumps(result, indent=2, ensure_ascii=False),
                file_name="workout_plan.json",
                mime="application/json",
                use_container_width=True
            )

        with download_col2:
            st.download_button(
                label="Download Current Plan as TXT",
                data=format_plan_as_text(result),
                file_name="workout_plan.txt",
                mime="text/plain",
                use_container_width=True
            )

if user_id:
    saved_plans = get_user_plans(user_id)

    if saved_plans:
        st.divider()
        st.subheader("Saved Plans")

        for index, entry in enumerate(saved_plans):
            title = f"Plan {index + 1} — {entry['created_at']}"

            with st.expander(title):
                inputs = entry["inputs"]

                st.write(
                    f"**Goal:** {inputs['goal']} | "
                    f"**Experience:** {inputs['experience']} | "
                    f"**Equipment:** {inputs['equipment']} | "
                    f"**Days:** {inputs['days']} | "
                    f"**Duration:** {inputs['duration']} min | "
                    f"**Focus:** {inputs['focus_area']}"
                )

                st.write(f"**Limitations:** {inputs['limitations']}")
                st.write(
                    f"**Excluded exercises:** "
                    f"{', '.join(inputs['exclude']) if inputs['exclude'] else 'None'}"
                )

                if st.button(f"Load Plan {index + 1}", key=f"load_plan_{index}"):
                    st.session_state.workout_result = entry["plan"]
                    st.success(f"Plan {index + 1} loaded.")

if st.session_state.workout_result is not None:
    st.divider()
    st.subheader("Quick Feedback")

    useful = st.radio(
        "Was this workout useful?",
        ["Yes", "No"],
        horizontal=True
    )

    feedback_text = st.text_input("Anything you'd improve? (optional)")

    if st.button("Submit Feedback"):
        file_exists = os.path.isfile(FEEDBACK_FILE)

        with open(FEEDBACK_FILE, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

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
