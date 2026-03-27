from openai import OpenAI

client = OpenAI()

goal = "fat loss"
experience = "beginner"
equipment = "bodyweight"

prompt = f"""
Generate a 3-day workout plan.

User:
- Goal: {goal}
- Experience: {experience}
- Equipment: {equipment}

Return ONLY valid JSON in this format:

{{
  "day1": "",
  "day2": "",
  "day3": ""
}}
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": prompt}
    ],
)

print(response.choices[0].message.content)