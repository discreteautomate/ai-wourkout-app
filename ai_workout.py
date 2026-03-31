import json
from openai import OpenAI
from examples import WORKOUT_EXAMPLES

client = OpenAI()

def generate_workout(goal, experience, equipment, days):
    prompt = f"""
You are a workout plan generator.

Generate a {days}-day workout plan.

Here are examples of the expected style:

{WORKOUT_EXAMPLES}

Now generate a new workout plan for this user:

Input:
- Goal: {goal}
- Experience: {experience}
- Equipment: {equipment}

Return ONLY valid JSON.

Each day must be an object with this structure:
{{
  "warmup": "",
  "main_workout": "",
  "finisher": "",
  "note": ""
}}

Use keys day1, day2, ..., up to the requested number of days.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
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
                    "raw_output": data
                }

            for section_key in expected_section_keys:
                if section_key not in data[day_key] or not data[day_key][section_key]:
                    return {
                        "error": "Invalid structure from AI",
                        "raw_output": data
                    }

        return data

    except json.JSONDecodeError:
        return {
            "error": "Invalid JSON from AI",
            "raw_output": output
        }
