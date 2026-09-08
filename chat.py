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
    messages=[{"role": "user", "content": "Say hi"}],
    reasoning_effort="low",
    stream=True,
    stream_options={"include_usage": True},
)

for chunk in stream:
    print(chunk)
    print("---")

        # Without this line the bot forgets everything it said.
        messages.append({"role": "assistant", "content": reply})

        print(f"[turn tokens total: {total_tokens} | messages in history: {len(messages)}]")

except KeyboardInterrupt:
    print()                                # Ctrl+C without the ugly traceback

print("\nBye.")
print(f"Session used {total_tokens} tokens across {len(messages)} messages.")