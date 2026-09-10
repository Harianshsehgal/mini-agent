"""
Week 1, Day 3 (3.1.2) - the ReAct loop.

Day 2 went around the loop once. Today it goes around many times:
model -> tool -> model -> tool -> ... -> answer.

Four things are new:
  1. Scratchpad  - the messages list IS the memory. It grows every turn.
  2. Stop        - no tool_calls means the model is talking to the user.
  3. Cap         - MAX_STEPS, because loops cost money.
  4. Errors      - become text for the model, never exceptions for Python.
"""

import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from schemas import TOOLS
from tools import calculator, find_landmark_city, get_weather

load_dotenv()

client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)

MODEL = "openai/gpt-oss-20b"
MAX_STEPS = 6

SYSTEM_PROMPT = (
    "You are a helpful assistant with tools. "
    "Do not answer factual questions from your own knowledge when a tool "
    "exists for them - call the tool instead. "
    "If a tool returns an error, read the error carefully and correct your "
    "next call. If you cannot get the information, say so honestly. "
    "Never invent a result."
)

# Keys MUST match the "name" field in schemas.py exactly.
TOOL_REGISTRY = {
    "get_weather": get_weather,
    "calculator": calculator,
    "find_landmark_city": find_landmark_city,
}


def run_tool(name: str, arguments: str) -> str:
    """The boundary between Python and the conversation.

    Tools in tools.py raise normally, like ordinary Python.
    Here every failure becomes a string the model can read and act on.
    This function must NEVER raise.
    """
    if name not in TOOL_REGISTRY:
        return f"Error: no tool named '{name}'. Available: {sorted(TOOL_REGISTRY)}"

    try:
        args = json.loads(arguments)
    except json.JSONDecodeError as e:
        return f"Error: arguments were not valid JSON ({e}). Send valid JSON."

    try:
        return str(TOOL_REGISTRY[name](**args))
    except TypeError as e:
        # Almost always wrong argument names - be specific so it can fix itself.
        return f"Error: wrong arguments for {name} ({e})."
    except Exception as e:
        return f"Error running {name}: {type(e).__name__}: {e}"


def ask(question: str) -> str:
    # The scratchpad. Everything the model knows lives in here.
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    for step in range(1, MAX_STEPS + 1):
        print(f"  [step {step}]")

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            reasoning_effort="low",
        )

        message = response.choices[0].message

        # model_dump keeps tool_calls. Hand-building this dict loses them,
        # and then the tool results below have no request to attach to.
        # This append must happen BEFORE running the tools.
        messages.append(message.model_dump(exclude_none=True))

        # The only clean way out of the loop.
        if not message.tool_calls:
            return message.content

        # Several tools can be requested in one turn - handle every one.
        for call in message.tool_calls:
            print(f"    -> {call.function.name}({call.function.arguments})")
            result = run_tool(call.function.name, call.function.arguments)
            print(f"    <- {result}")

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,  # must match the request id
                    "content": result,
                }
            )

    # Only reached if the for-loop finished without returning: the cap fired.
    messages.append({
        "role": "user",
        "content": (
            "You have run out of tool calls. Do NOT call any tool. "
            "Answer now in plain text using only the information already "
            "gathered above. State clearly what you could not find."
        ),
    })

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            reasoning_effort="low",
        )
        return response.choices[0].message.content
    except Exception as e:
        return (
            f"I could not finish within {MAX_STEPS} steps, and could not "
            f"summarise what I found ({type(e).__name__})."
        )


if __name__ == "__main__":
    questions = [
        "What's the weather in the city where the Taj Mahal is?",
        "What's the weather in the city where the Vaultspire Tower is?",
        "What's the weather in the city where the Eiffel Tower is?",
        "What's 17 * 43, and the weather where the Charminar is?",
    ]

    for q in questions:
        print(f"\nQ: {q}")
        answer = ask(q)
        print(f"A: {answer}")