import json
from openai import OpenAI

EXERCISE_IMAGES = {
    "push-ups": "https://raw.githubusercontent.com/discreteautomate/ai-wourkout-app/refs/heads/main/images/Push-up%20form%20demonstration%20in%20stages.png",
    "push up": "https://raw.githubusercontent.com/discreteautomate/ai-wourkout-app/refs/heads/main/images/Push-up%20form%20demonstration%20in%20stages.png",
    "pushups": "https://raw.githubusercontent.com/discreteautomate/ai-wourkout-app/refs/heads/main/images/Push-up%20form%20demonstration%20in%20stages.png",

    "squats": "https://raw.githubusercontent.com/discreteautomate/ai-wourkout-app/refs/heads/main/images/Bodyweight%20squat%20demonstration%20in%20two%20stages.png",
    "squat": "https://raw.githubusercontent.com/discreteautomate/ai-wourkout-app/refs/heads/main/images/Bodyweight%20squat%20demonstration%20in%20two%20stages.png",
    "bodyweight squat": "https://raw.githubusercontent.com/discreteautomate/ai-wourkout-app/refs/heads/main/images/Bodyweight%20squat%20demonstration%20in%20two%20stages.png",

    "plank": "https://raw.githubusercontent.com/discreteautomate/ai-wourkout-app/refs/heads/main/images/planks%20explained%20large%20letters.png",
    "high plank": "https://raw.githubusercontent.com/discreteautomate/ai-wourkout-app/refs/heads/main/images/planks%20explained%20large%20letters.png",
    "forearm plank": "https://raw.githubusercontent.com/discreteautomate/ai-wourkout-app/refs/heads/main/images/planks%20explained%20large%20letters.png",

    "glute bridge": "https://raw.githubusercontent.com/discreteautomate/ai-wourkout-app/refs/heads/main/images/Glute%20bridge%20exercise%20demonstration.png",
    "glute bridges": "https://raw.githubusercontent.com/discreteautomate/ai-wourkout-app/refs/heads/main/images/Glute%20bridge%20exercise%20demonstration.png",

    "burpees": "https://raw.githubusercontent.com/discreteautomate/ai-wourkout-app/refs/heads/main/images/Burpee%20exercise%20progression%20demonstration.png",
    "burpee": "https://raw.githubusercontent.com/discreteautomate/ai-wourkout-app/refs/heads/main/images/Burpee%20exercise%20progression%20demonstration.png",

    "dumbbell chest press": "https://raw.githubusercontent.com/discreteautomate/ai-wourkout-app/refs/heads/main/images/Dumbbell%20chest%20press%20exercise%20demonstration.png",
    "chest press": "https://raw.githubusercontent.com/discreteautomate/ai-wourkout-app/refs/heads/main/images/Dumbbell%20chest%20press%20exercise%20demonstration.png",

    "dumbbell shoulder press": "https://raw.githubusercontent.com/discreteautomate/ai-wourkout-app/refs/heads/main/images/Dumbbell%20shoulder%20press%20demonstration%20steps.png",
    "shoulder press": "https://raw.githubusercontent.com/discreteautomate/ai-wourkout-app/refs/heads/main/images/Dumbbell%20shoulder%20press%20demonstration%20steps.png",

    "lunges": "https://raw.githubusercontent.com/discreteautomate/ai-wourkout-app/refs/heads/main/images/Forward%20lunge%20exercise%20demonstration.png",
    "lunge": "https://raw.githubusercontent.com/discreteautomate/ai-wourkout-app/refs/heads/main/images/Forward%20lunge%20exercise%20demonstration.png",
    "walking lunges": "https://raw.githubusercontent.com/discreteautomate/ai-wourkout-app/refs/heads/main/images/Forward%20lunge%20exercise%20demonstration.png",

    "torso twists": "https://raw.githubusercontent.com/discreteautomate/ai-wourkout-app/refs/heads/main/images/torso%20twist.png",
    "russian twists": "https://raw.githubusercontent.com/discreteautomate/ai-wourkout-app/refs/heads/main/images/torso%20twist.png",

    "arm circles": "https://raw.githubusercontent.com/discreteautomate/ai-wourkout-app/refs/heads/main/images/arm%20circles.png",
    "shoulder circles": "https://raw.githubusercontent.com/discreteautomate/ai-wourkout-app/refs/heads/main/images/arm%20circles.png",

    "high knees": "https://raw.githubusercontent.com/discreteautomate/ai-wourkout-app/refs/heads/main/images/high%20knees.png",
    "knee raises": "https://raw.githubusercontent.com/discreteautomate/ai-wourkout-app/refs/heads/main/images/high%20knees.png"
}

client = OpenAI()


def find_exercise_image(exercise_text):
    exercise_text = exercise_text.lower()
    sorted_exercises = sorted(
        EXERCISE_IMAGES.items(),
        key=lambda x: len(x[0]),
        reverse=True
    )

    for exercise_name, image_url in sorted_exercises:
        if exercise_name in exercise_text:
            return image_url

    return None


def attach_images_to_items(day_data):
    for section in ["warmup", "main_workout", "finisher"]:
        for item in day_data.get(section, []):
            exercise_name = item.get("exercise", "")
            item["image"] = find_exercise_image(exercise_name)

    return day_data


def generate_workout(goal, experience, equipment, days, duration, focus_area, age, height, weight, limitations, exclude):
    exercise_item_schema = {
        "type": "object",
        "properties": {
            "exercise": {"type": "string"},
            "details": {"type": "string"}
        },
        "required": ["exercise", "details"],
        "additionalProperties": False
    }

    schema = {
        "name": "workout_plan",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                **{
                    f"day{i}": {
                        "type": "object",
                        "properties": {
                            "warmup": {
                                "type": "array",
                                "items": exercise_item_schema
                            },
                            "main_workout": {
                                "type": "array",
                                "items": exercise_item_schema
                            },
                            "finisher": {
                                "type": "array",
                                "items": exercise_item_schema
                            },
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

For each day:
- warmup must be an array of exercise objects
- main_workout must be an array of exercise objects
- finisher must be an array of exercise objects
- each exercise object must have:
  - "exercise": short exercise name
  - "details": sets, reps, or duration
- note must be a short coaching note

Generate the workout plan for this user:

- Goal: {goal}
- Experience: {experience}
- Equipment: {equipment}
- Duration: {duration} minutes
- Focus area: {focus_area}
- Age: {age}
- Height: {height} cm
- Weight: {weight} kg
- Limitations: {limitations}
- Exclude these exercises: {", ".join(exclude) if exclude else "none"}

Rules:
- Keep each day practical and realistic.
- Keep exercise names short and clean.
- Do not include excluded exercises.
- Prefer common exercise names like "push-ups", "squats", "plank", "lunges".
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

        for day_key in expected_day_keys:
            if day_key not in data or not isinstance(data[day_key], dict):
                return {
                    "error": "Invalid structure from AI",
                    "raw_output": output
                }

            for section in ["warmup", "main_workout", "finisher"]:
                if section not in data[day_key] or not isinstance(data[day_key][section], list):
                    return {
                        "error": "Invalid structure from AI",
                        "raw_output": output
                    }

                for item in data[day_key][section]:
                    if not isinstance(item, dict):
                        return {
                            "error": "Invalid structure from AI",
                            "raw_output": output
                        }

                    if "exercise" not in item or "details" not in item:
                        return {
                            "error": "Invalid structure from AI",
                            "raw_output": output
                        }

            if "note" not in data[day_key] or not isinstance(data[day_key]["note"], str):
                return {
                    "error": "Invalid structure from AI",
                    "raw_output": output
                }

            data[day_key] = attach_images_to_items(data[day_key])

        return data


        def swap_exercise(current_exercise, current_details, goal, experience, equipment, limitations, exclude):
            prompt = f"""
            Replace this exercise with one suitable alternative.
        
            Current exercise:
            - Exercise: {current_exercise}
            - Details: {current_details}
        
            User profile:
            - Goal: {goal}
            - Experience: {experience}
            - Equipment: {equipment}
            - Limitations or injuries: {limitations}
            - Excluded exercises: {exclude}
        
            Rules:
            - Do NOT return the same exercise.
            - Respect the user's equipment.
            - Respect injuries and limitations.
            - Avoid excluded exercises.
            - Keep the replacement similar in difficulty and purpose.
            - Return ONLY valid JSON.
        
            JSON format:
            {{
              "exercise": "replacement exercise name",
              "details": "sets/reps/duration"
            }}
            """
        
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
        
            return json.loads(response.choices[0].message.content)

        except json.JSONDecodeError:
        return {
            "error": "Invalid JSON from AI",
            "raw_output": output
        }


def swap_exercise(current_exercise, current_details, goal, experience, equipment, limitations, exclude):
    prompt = f"""
    Replace this exercise with one suitable alternative.
    ...
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)
