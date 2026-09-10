"""
Week 1, Day 2 (2.1.3) - look at a raw tool-call response. Do not parse it yet.

No streaming here on purpose. Streamed tool calls arrive in fragments and
have to be reassembled, which hides the thing we want to see.
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

from schemas import TOOLS

load_dotenv()

client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)

MODEL = "openai/gpt-oss-20b"

QUESTIONS = [
    "What's the weather in Delhi?",      # expect: get_weather
    "What is 17 * 43?",                  # expect: calculator
    "Hello, how are you?",               # expect: no tool at all
]


def peek(question: str) -> None:
    print("=" * 60)
    print("QUESTION:", question)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": question}],
        tools=TOOLS,
        reasoning_effort="low",
    )

    choice = response.choices[0]

    print("finish_reason:", choice.finish_reason)
    print("content      :", repr(choice.message.content))

    calls = choice.message.tool_calls
    if not calls:
        print("tool_calls   : None  <- model answered by itself")
        return

    for call in calls:
        print("-" * 40)
        print("id           :", call.id)
        print("name         :", call.function.name)
        print("arguments    :", repr(call.function.arguments))
        print("arg type     :", type(call.function.arguments).__name__)


if __name__ == "__main__":
    for q in QUESTIONS:
        peek(q)
        print()