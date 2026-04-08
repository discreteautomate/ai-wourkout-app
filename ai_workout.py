import json
from openai import OpenAI

client = OpenAI()

def generate_workout(goal, experience, equipment, days, duration, focus_area, limitations):
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

Generate a {days}-day workout plan for this user:

- Goal: {goal}
- Experience: {experience}
- Equipment: {equipment}
- Duration: {duration} minutes
- Focus area: {focus_area}
- Limitations: {limitations}

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
        return json.loads(output)
    except json.JSONDecodeError:
        return {
            "error": "Invalid JSON from AI",
            "raw_output": output
        }
