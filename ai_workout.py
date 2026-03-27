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

Return ONLY valid JSON where the keys are day1, day2, ..., up to the requested number of days.
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

        expected_keys = [f"day{i}" for i in range(1, days + 1)]

        for key in expected_keys:
            if key not in data or not data[key]:
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