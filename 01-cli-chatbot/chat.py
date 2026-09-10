"""
Week 1, Day 1 - CLI chatbot.

No framework. Just the provider SDK and a Python list.
The list IS the memory - that is the whole trick.
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)

MODEL = "openai/gpt-oss-20b"

messages = [
    {"role": "system", "content": "You are a helpful assistant. Keep answers short."}
]

total_tokens = 0

print("Chat started. Type 'quit' or 'exit' to leave.\n")

try:
    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() in ("quit", "exit"):
            break
        if not user_input:                 # empty Enter - don't waste a call
            continue

        messages.append({"role": "user", "content": user_input})

        stream = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            reasoning_effort="low",
            stream=True,
            stream_options={"include_usage": True},
        )

        print("Bot: ", end="", flush=True)

        pieces = []
        for chunk in stream:
            # The final chunk carries usage and has an empty choices list,
            # so check choices exists before touching index 0.
            if chunk.choices and chunk.choices[0].delta.content:
                piece = chunk.choices[0].delta.content
                print(piece, end="", flush=True)
                pieces.append(piece)

            if chunk.usage:
                total_tokens += chunk.usage.total_tokens

        print()
        reply = "".join(pieces)

        # Without this line the bot forgets everything it said.
        messages.append({"role": "assistant", "content": reply})

        print(f"[turn tokens total: {total_tokens} | messages in history: {len(messages)}]")

except KeyboardInterrupt:
    print()                                # Ctrl+C without the ugly traceback

print("\nBye.")
print(f"Session used {total_tokens} tokens across {len(messages)} messages.")