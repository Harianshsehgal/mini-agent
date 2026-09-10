"""
Week 1, Day 2 (2.1.2) - the actual tool functions.

These are plain Python. The model never sees this file - it only sees the
descriptions in schemas.py. Keep the function names in sync between the two.

Tools raise normally on failure, like ordinary Python. Deciding what to do
with those failures is the caller's job, not theirs.
"""

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
    print(get_weather("Delhi"))
    print(calculator("17 * 43"))        # 731

    # Unknown city: the tool raises. That is correct - tools fail like
    # ordinary Python, and the caller decides what to do about it.
    try:
        get_weather("Paris")
    except ValueError as e:
        print(f"raised as expected: {e}")