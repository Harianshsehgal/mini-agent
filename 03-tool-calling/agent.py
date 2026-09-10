"""
Week 1, Day 2 (2.1.4) - the agent loop.

An agent is a while-loop around a model that can ask you to run functions.
The model decides WHICH function and WITH WHAT arguments.
Everything else - running it, handling errors, deciding whether to loop
again - is our code.
"""

import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from schemas import TOOLS
from tools import calculator, get_weather

load_dotenv()

client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)

MODEL = "openai/gpt-oss-20b"

# Keys MUST match the "name" field in schemas.py exactly.
TOOL_REGISTRY = {
    "get_weather": get_weather,
    "calculator": calculator,
}


def run_tool(name: str, arguments: str) -> str:
    """Arguments arrive as a JSON *string*, so parse before calling."""
    args = json.loads(arguments)
    return str(TOOL_REGISTRY[name](**args))


def ask(question: str) -> str:
    messages = [{"role": "user", "content": question}]

    while True:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            reasoning_effort="low",
        )

        message = response.choices[0].message

        # model_dump keeps tool_calls. Hand-building this dict loses them,
        # and then the tool result below has no request to attach to.
        messages.append(message.model_dump(exclude_none=True))

        # The only way out of the loop.
        if not message.tool_calls:
            return message.content

        # Several tools can be requested in one turn - handle every one.
        for call in message.tool_calls:
            print(f"  -> calling {call.function.name}({call.function.arguments})")
            result = run_tool(call.function.name, call.function.arguments)
            print(f"  <- got: {result}")

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,  # must match the request id
                    "content": result,
                }
            )


if __name__ == "__main__":
    for q in [
        "What is 17 * 43?",
        "What's the weather in Delhi?",
        "What's the weather in Delhi, and what is 17 * 43?",
        "Hello",
    ]:
        print(f"\nQ: {q}")
        print(f"A: {ask(q)}")