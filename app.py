import streamlit as st
import csv
import os
import json
from datetime import datetime
from ai_workout import generate_workout

if "screen" not in st.session_state:
    st.session_state.screen = "form"

if "workout_result" not in st.session_state:
    st.session_state.workout_result = None

def render_exercise_card(item):
    exercise = item.get("exercise", "Unknown exercise")
    details = item.get("details", "")
    image_url = item.get("image")

    st.markdown(
        f"""
        <div style="
            padding: 18px;
            border-radius: 18px;
            background-color: rgba(128, 128, 128, 0.12);
            border: 1px solid rgba(128, 128, 128, 0.25);
            margin-bottom: 14px;
        ">
            <h3 style="margin-bottom: 6px; color: inherit;">{exercise.title()}</h3>
            <p style="font-size: 16px; margin-top: 0; color: inherit;">
                <b>{details}</b>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if image_url:
        st.image(image_url, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)


def format_plan_as_text(plan):
    lines = []

    for day, details in plan.items():
        if not isinstance(details, dict):
            continue

        lines.append(f"{day.upper()}")

        lines.append("Warmup:")
        for item in details["warmup"]:
            lines.append(f"- {item.get('exercise', '')}: {item.get('details', '')}")

        lines.append("Main workout:")
        for item in details["main_workout"]:
            lines.append(f"- {item.get('exercise', '')}: {item.get('details', '')}")

        lines.append("Finisher:")
        for item in details["finisher"]:
            lines.append(f"- {item.get('exercise', '')}: {item.get('details', '')}")

        lines.append(f"Note: {details['note']}")
        lines.append("")

    return "\n".join(lines)

st.set_page_config(page_title="AI Workout Generator", page_icon="💪")

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, rgba(120,120,120,0.10), rgba(0,0,0,0));
    }

    div[data-testid="stVerticalBlock"] {
        gap: 0.75rem;
    }

    div.stButton > button {
        width: 100%;
        border-radius: 999px;
        padding: 0.75rem 1rem;
        font-weight: 700;
        border: 1px solid rgba(128,128,128,0.25);
    }

    div[data-baseweb="select"] > div,
    div[data-testid="stTextInput"] input {
        border-radius: 14px;
    }

    .premium-hero {
        padding: 22px;
        border-radius: 24px;
        background: rgba(128,128,128,0.12);
        border: 1px solid rgba(128,128,128,0.25);
        margin-bottom: 18px;
    }

    .premium-hero h1 {
        margin-bottom: 6px;
        font-size: 2rem;
    }

    .premium-hero p {
        margin-top: 0;
        opacity: 0.75;
        font-size: 1rem;
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 1rem;
    }

    header[data-testid="stHeader"] {
        height: 0rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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




if "workout_result" not in st.session_state:
    st.session_state.workout_result = None

if "loaded_user" not in st.session_state:
    st.session_state.loaded_user = ""

st.markdown(
    """
    <div class="premium-hero">
        <h1>AI Workout Generator 💪</h1>
        <p>Create a personalized workout plan in seconds.</p>
    </div>
    """,
    unsafe_allow_html=True
)

if st.session_state.screen == "form":

    user_id = st.text_input(
        "Enter your email or username to save your plans",
        key="user_id_input"
    ).strip().lower()

    st.write("Create a personalized workout plan")

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

    with st.expander("Advanced personalization"):

        age = st.number_input(
            "Age",
            min_value=13,
            max_value=90,
            value=30
        )

        height = st.number_input(
            "Height (cm)",
            min_value=120,
            max_value=230,
            value=175
        )

        weight = st.number_input(
            "Weight (kg)",
            min_value=35,
            max_value=250,
            value=75
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

    if st.button("Generate Workout 💪"):
        with st.spinner("Generating your workout plan..."):
            result = generate_workout(
                goal,
                experience,
                equipment,
                days,
                duration,
                focus_area,
                age,
                height,
                weight,
                limitations,
                exclude
            )

        st.session_state.workout_result = result
        st.session_state.user_inputs = {
            "goal": goal,
            "experience": experience,
            "duration": duration,
            "focus_area": focus_area
        }
        
        st.session_state.screen = "results"
        st.rerun()

elif st.session_state.screen == "results":
    
    st.markdown("## Your Workout Plan 💪")

    if st.button("▶️ Start Workout"):
        st.session_state.screen = "workout"
        st.session_state.current_step = 0
        st.rerun()

elif st.session_state.screen == "workout":

    result = st.session_state.workout_result

    # flatten exercises into a list
    steps = []

    for day, details in result.items():
        if not isinstance(details, dict):
            continue

        for section in ["warmup", "main_workout", "finisher"]:
            for item in details[section]:
                steps.append(item)

    current = st.session_state.current_step

    if current < len(steps):
        item = steps[current]

        st.markdown("### 🏋️ Workout Mode")
        st.caption(f"Exercise {current + 1} of {len(steps)}")
        st.progress((current + 1) / len(steps))

        exercise = item.get("exercise", "Unknown exercise")
        details = item.get("details", "")
        image_url = item.get("image")

        st.markdown(f"## {exercise.title()}")
        st.markdown(f"**{details}**")

        if image_url:
            st.image(image_url, use_container_width=True)

        nav_left, nav_space, nav_right = st.columns([1, 1, 1])

        with nav_left:
            if st.button("⬅️ Previous", use_container_width=True, disabled=current == 0):
                st.session_state.current_step -= 1
                st.rerun()

        with nav_right:
            if st.button("Next ➡️", use_container_width=True):
                st.session_state.current_step += 1
                st.rerun()

    else:
        st.success("Workout complete! 🎉")

        if st.button("Back to Plan"):
            st.session_state.screen = "results"
            st.rerun()
    

    inputs = st.session_state.get("user_inputs", {})

    if inputs:
        st.markdown(
            f"""
            <div style="
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
                margin-bottom: 16px;
            ">
                <span style="padding:6px 12px;border-radius:999px;background:rgba(128,128,128,0.15);">
                    🎯 {inputs.get('goal','').title()}
                </span>
                <span style="padding:6px 12px;border-radius:999px;background:rgba(128,128,128,0.15);">
                    ⏱️ {inputs.get('duration','')} min
                </span>
                <span style="padding:6px 12px;border-radius:999px;background:rgba(128,128,128,0.15);">
                    🏋️ {inputs.get('focus_area','').title()}
                </span>
                <span style="padding:6px 12px;border-radius:999px;background:rgba(128,128,128,0.15);">
                    ⚡ {inputs.get('experience','').title()}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

    result = st.session_state.workout_result

    st.markdown("## Your Workout Plan 💪")
    st.caption("Built around your goal, experience, equipment, and preferences.")

    # your existing result display code goes here

    if st.button("🔄 Create New Workout"):
        st.session_state.screen = "form"
        st.session_state.workout_result = None
        st.rerun()

# Auto-load latest saved plan when user changes
if user_id != st.session_state.loaded_user:
    user_plans = get_user_plans(user_id) if user_id else []
    st.session_state.workout_result = user_plans[0]["plan"] if user_plans else None
    st.session_state.loaded_user = user_id

    st.session_state.workout_result = result

    if user_id and "error" not in result:
        inputs = {
            "age": age,
            "height": height,
            "weight": weight,
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

            st.markdown("### 🔥 Warmup")
            for item in details["warmup"]:
                render_exercise_card(item)

            st.markdown("### 🏋️ Main workout")
            for item in details["main_workout"]:
                render_exercise_card(item)

            st.markdown("### ⚡ Finisher")
            for item in details["finisher"]:
                render_exercise_card(item)

            st.caption(f"💡 {details['note']}")

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

        st.success("Feedback saved. Thank you 💪")

admin_password = st.text_input("Admin Access", type="password")

if admin_password == "345y4((355.":  # change this
    if st.checkbox("Show Feedback (Admin)"):
        if os.path.exists(FEEDBACK_FILE):
            with open(FEEDBACK_FILE, "r", encoding="utf-8") as file:
                st.text(file.read())
        else:
            st.info("No feedback yet.")
