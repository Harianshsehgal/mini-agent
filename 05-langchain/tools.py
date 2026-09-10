"""Step 05 — LangChain tools.

4.2: the same tools as 04-react-agent, now built with @tool.
No schemas.py here — @tool builds the schema from the function.
"""
import json

from langchain.tools import tool
from langchain_core.utils.function_calling import convert_to_openai_tool


# TODO 1: copy your tool functions from 04-react-agent/tools.py.
# Put @tool on the line above each one.
# Keep the type hints and the docstring. @tool reads both.


LANDMARK_CITIES = {
    "taj mahal": "Agra",
    "charminar": "Hyderabad",
    "gateway of india": "Mumbai",
    "vaultspire tower": "Kochi",
}
WEATHER_DATA = {
    "delhi": "32°C, hazy sunshine",
    "agra": "34°C, clear",
    "kochi": "29°C, humid with light rain",
    "hyderabad": "30°C, partly cloudy",
    "mumbai": "31°C, humid",
}
@tool(parse_docstring=True)
def find_landmark_city(landmark: str) -> str:
    """Find the city where a famous landmark is located.

    Args:
        landmark: Name of the landmark in English, for example 'Taj Mahal'.
    """
    key = landmark.strip().lower()
    if key not in LANDMARK_CITIES:
        raise ValueError(
            f"Unknown landmark '{landmark}'. Known landmarks: {sorted(LANDMARK_CITIES)}"
        )
    return LANDMARK_CITIES[key]


@tool(parse_docstring=True)
def get_weather(city: str) -> str:
    """Get the current weather for a city.

    Args:
        city: Name of the city in English, for example 'Agra'.
    """
    key = city.strip().lower()
    if key not in WEATHER_DATA:
        raise ValueError(
            f"No weather data for '{city}'. Known cities: {sorted(WEATHER_DATA)}"
        )
    return f"{city}: {WEATHER_DATA[key]}"


@tool(parse_docstring=True)
def calculator(expression: str) -> str:
    """Evaluate a maths expression and return the result.

    Args:
        expression: A maths expression in Python syntax, for example '2 + 3 * 4'. Use ** for powers, for example '2 ** 3'.
    """
    # eval() is unsafe - see drill 2.4.5
    return str(eval(expression))




# TODO 2: put every tool in this list.
TOOLS = [find_landmark_city, get_weather, calculator]


if __name__ == "__main__":
    for t in TOOLS:
        print("=" * 50)
        print("TYPE:       ", type(t).__name__)
        print("NAME:       ", t.name)
        print("DESCRIPTION:", t.description)
        print("ARGS:       ", t.args)
        print("\nOPENAI SCHEMA:")
        print(json.dumps(convert_to_openai_tool(t), indent=2))

    # TODO 3: run one tool yourself, without the model.
    # Hint: it's the same "run once" word from 4.1.
    # A tool takes its arguments as a dict: {"city": "Agra"}
    print("\n--- test call ---")
    print(get_weather.invoke({"city": "Agra"}))