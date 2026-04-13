import json
from openai import OpenAI

EXERCISE_IMAGES = {
    "push-ups": "https://raw.githubusercontent.com/discreteautomate/ai-wourkout-app/refs/heads/main/images/Push-up%20form%20demonstration%20in%20stages.png",
    "squats": "https://raw.githubusercontent.com/discreteautomate/ai-wourkout-app/refs/heads/main/images/Bodyweight%20squat%20demonstration%20in%20two%20stages.png",
    "plank": "https://raw.githubusercontent.com/discreteautomate/ai-wourkout-app/refs/heads/main/images/Plank%20exercise%20demonstration%20stages.png",
    "glute bridge": "https://raw.githubusercontent.com/discreteautomate/ai-wourkout-app/refs/heads/main/images/Glute%20bridge%20exercise%20demonstration.png",
    "burpees": "https://raw.githubusercontent.com/discreteautomate/ai-wourkout-app/refs/heads/main/images/Burpee%20exercise%20progression%20demonstration.png",
    "dumbbell chest press": "https://raw.githubusercontent.com/discreteautomate/ai-wourkout-app/refs/heads/main/images/Dumbbell%20chest%20press%20exercise%20demonstration.png",
    "dumbbell shoulder press": "https://raw.githubusercontent.com/discreteautomate/ai-wourkout-app/refs/heads/main/images/Dumbbell%20shoulder%20press%20demonstration%20steps.png",
    "lunges": "https://raw.githubusercontent.com/discreteautomate/ai-wourkout-app/refs/heads/main/images/Forward%20lunge%20exercise%20demonstration.png"
}

client = OpenAI()


def attach_images(data):
    for day in data.values():
        if isinstance(day, dict):
            text = " ".join([
                day.get("warmup", ""),
                day.get("main_workout", ""),
                day.get("finisher", ""),
                day.get("note", "")
            ]).lower()

            matched_images = []

            for exercise, url in EXERCISE_IMAGES.items():
                if exercise in text:
                    matched_images.append({
                        "exercise": exercise,
                        "url": url
                    })

            day["images"] = matched_images

    return data


def generate_workout(goal, experience, equipment, days, duration, focus_area, limitations, exclude):
    schema = {
        "name": "workout_plan",
        "schema": {
            "type": "object",
            "properties": {
                **{
                    f"day{i}": {
                        "type": "object",
                        "properties": {
                            "warmup": {"type": "string"},
                            "main_workout": {"type": "string"},
                            "finisher": {"type": "string"},
                            "note": {"type": "string"}
                        },
                        "required": ["warmup", "main_workout", "finisher", "note"],
                        "additionalProperties": False
                    }
                    for i in range(1, days + 1)
                }
            },
            "required": [f"day{i}" for i in range(1, days + 1)],
            "additionalProperties": False
        }
    }

    prompt = f"""
You are a workout plan generator.

Generate a workout plan for exactly {days} days.

You must return exactly these keys:
{", ".join([f"day{i}" for i in range(1, days + 1)])}

Generate the workout plan for this user:

- Goal: {goal}
- Experience: {experience}
- Equipment: {equipment}
- Duration: {duration} minutes
- Focus area: {focus_area}
- Limitations: {limitations}
- Exclude these exercises: {", ".join(exclude) if exclude else "none"}

Keep each day practical and realistic for the user's level, available time, equipment, focus area, and limitations.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You generate structured workout plans."},
            {"role": "user", "content": prompt}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": schema
        }
    )

    output = response.choices[0].message.content

    try:
        data = json.loads(output)

        expected_day_keys = [f"day{i}" for i in range(1, days + 1)]
        expected_section_keys = ["warmup", "main_workout", "finisher", "note"]

        for day_key in expected_day_keys:
            if day_key not in data or not isinstance(data[day_key], dict):
                return {
                    "error": "Invalid structure from AI",
                    "raw_output": output
                }

            for section_key in expected_section_keys:
                if section_key not in data[day_key] or not data[day_key][section_key]:
                    return {
                        "error": "Invalid structure from AI",
                        "raw_output": output
                    }

        data = attach_images(data)
        return data

    except json.JSONDecodeError:
        return {
            "error": "Invalid JSON from AI",
            "raw_output": output
        }
