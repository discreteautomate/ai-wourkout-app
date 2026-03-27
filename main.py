from ai_workout import generate_workout

print("Welcome to AI Workout Generator 💪")

goal = input("Enter your goal (fat loss / muscle gain / strength): ")
experience = input("Enter your experience (beginner / intermediate / advanced): ")
equipment = input("Enter your equipment (bodyweight / gym / dumbbells): ")
days = int(input("Enter number of days: "))

result = generate_workout(goal, experience, equipment, days)

print("\nYour Workout Plan:\n")

if "day1" in result:
    for day, plan in result.items():
        print(f"{day.upper()}: {plan}\n")
else:
    print("Error:", result)