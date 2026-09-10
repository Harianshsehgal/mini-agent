"""
Week 1, Day 2 (2.3.1) - watch plain JSON prompting fail.

We ask the model for JSON the obvious way: by asking nicely.
Then we run it 8 times and count how often we can actually parse it.

This file exists to produce EVIDENCE, not a working feature.
Save the failures - they are the reason 2.3.2 matters.
"""

import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)

MODEL = "openai/gpt-oss-20b"
RUNS = 8

PROMPT = (
    "Give me the name, age and occupation of three fictional people as JSON."
)


def one_run(n: int) -> bool:
    """Ask once. Return True if the reply parsed as JSON."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": PROMPT}],
        # temperature 1.0 is roughly the default. We are not fighting
        # randomness here - we want to see the natural variation.
        temperature=1.0,
        reasoning_effort="low",
    )

    raw = response.choices[0].message.content

    try:
        data = json.loads(raw)
        print(f"[{n}] PARSED   -> type={type(data).__name__}")
        # Even when it parses, the SHAPE may differ between runs.
        # Sometimes a list, sometimes {"people": [...]}, sometimes
        # {"person1": {...}}. Note which you get.
        print(f"     shape: {json.dumps(data)[:120]}")
        return True
    except json.JSONDecodeError as err:
        print(f"[{n}] FAILED   -> {err}")
        print("     raw reply starts with:")
        print("     " + repr(raw[:200]))
        return False


if __name__ == "__main__":
    successes = sum(one_run(i + 1) for i in range(RUNS))
    print()
    print(f"Parsed cleanly: {successes}/{RUNS}")
    print("Note the SHAPE differences too, not just the parse failures.")