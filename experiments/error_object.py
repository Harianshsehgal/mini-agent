"""What is inside a Python error object?"""
import traceback


def find_landmark_city(landmark: str) -> str:
    raise ValueError(f"Unknown landmark '{landmark}'")


try:
    find_landmark_city("Big Ben")
except ValueError as error:
    error.add_note("During task with name 'tools'")   # like LangGraph does

    print("1. TYPE:     ", type(error).__name__)
    print("2. MESSAGE:  ", str(error))
    print("3. TRACEBACK:", error.__traceback__)
    print("4. NOTES:    ", error.__notes__)

    print("\n--- what f'Error: {error}' gives ---")
    print(f"Error: {error}")

    print("\n--- what the terminal shows if nobody catches it ---")
    print("".join(traceback.format_exception(error)))