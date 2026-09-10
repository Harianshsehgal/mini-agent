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
            f"Unknown landmark '{landmark}'. Known landmarks: {list(LANDMARK_CITIES)}"
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
    """Evaluate a maths expression. eval() is unsafe — see drill 2.4.5."""
    return str(eval(expression))

# if __name__ == "__main__":
#     print(get_weather("Delhi"))
#     print(get_weather("Paris"))     # should give the "no data" message
#     print(calculator("17 * 43"))    # 731
