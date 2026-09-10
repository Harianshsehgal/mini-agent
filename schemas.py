"""
Week 1, Day 3 (3.1.1) - tool schemas, OpenAI/Groq format.

The model never sees tools.py. It only sees these descriptions.
So the description IS a prompt.

Every tool needs TWO things: a variable name, and an entry in TOOLS.
Miss either and the tool silently does not exist.
"""

WEATHER_TOOL = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": (
            "Get the current weather for a city. "
            "Use this whenever the user asks about temperature, rain, "
            "or conditions in a specific place."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city name, e.g. 'Delhi' or 'Bengaluru'.",
                }
            },
            "required": ["city"],
        },
    },
}

CALCULATOR_TOOL = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": (
            "Evaluate a mathematical expression and return the result. "
            "Use this for any arithmetic the user asks for - sums, "
            "percentages, multiplication, division. Always use this "
            "instead of calculating in your head."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": (
                        "A maths expression to evaluate, "
                        "e.g. '17 * 43' or '4500 * 0.18'."
                    ),
                }
            },
            "required": ["expression"],
        },
    },
}

LANDMARK_TOOL = {
    "type": "function",
    "function": {
        "name": "find_landmark_city",
        "description": (
            "Find which city a famous landmark is located in. "
            "You MUST call this to find a landmark's city. Never answer "
            "from your own knowledge, even if you are sure - the lookup "
            "table is the only correct source. To get the weather at a "
            "landmark, call this first, then pass the city to get_weather."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "landmark": {
                    "type": "string",
                    "description": (
                        "Name of the landmark, e.g. 'Taj Mahal' or 'Charminar'."
                    ),
                }
            },
            "required": ["landmark"],
        },
    },
}

TOOLS = [WEATHER_TOOL, CALCULATOR_TOOL, LANDMARK_TOOL]