"""
Week 1, Day 3 (3.1.1) - the actual tool functions.

Plain Python. The model never sees this file - it only sees the
descriptions in schemas.py. Keep the function names in sync between the
two, and with TOOL_REGISTRY in agent.py.

These raise normally on failure. Turning exceptions into text is
run_tool()'s job in agent.py, not theirs.
"""

LANDMARK_CITIES = {
    "taj mahal": "Agra",
    "charminar": "Hyderabad",
    "gateway of india": "Mumbai",
    "vaultspire tower": "Kochi",
}


def find_landmark_city(landmark: str) -> str:
    key = landmark.strip().lower()
    if key not in LANDMARK_CITIES:
        raise ValueError(
            f"Unknown landmark '{landmark}'. Known landmarks: {sorted(LANDMARK_CITIES)}"
        )
    return LANDMARK_CITIES[key]


WEATHER_DATA = {
    "delhi": "32°C, hazy sunshine",
    "agra": "34°C, clear",
    "kochi": "29°C, humid with light rain",
    "hyderabad": "30°C, partly cloudy",
    "mumbai": "31°C, humid",
}


def get_weather(city: str) -> str:
    key = city.strip().lower()
    if key not in WEATHER_DATA:
        raise ValueError(
            f"No weather data for '{city}'. Known cities: {sorted(WEATHER_DATA)}"
        )
    return f"{city}: {WEATHER_DATA[key]}"


def calculator(expression: str) -> str:
    """Evaluate a maths expression. eval() is unsafe - see drill 2.4.5."""
    return str(eval(expression))


if __name__ == "__main__":
    # Run this file directly to check the tools work before the agent uses them.
    print(find_landmark_city("Taj Mahal"))      # Agra
    print(get_weather("Delhi"))
    print(calculator("17 * 43"))                # 731

    # Unknown inputs raise. That is correct - tools fail like ordinary
    # Python, and run_tool() in agent.py decides what to do about it.
    for bad in (lambda: get_weather("Paris"), lambda: find_landmark_city("Eiffel Tower")):
        try:
            bad()
        except ValueError as e:
            print(f"raised as expected: {e}")