"""
Streaming vs non-streaming - measured, not explained.

Run this and WATCH YOUR SCREEN while it runs.
The numbers at the end matter, but so does how the two feel different.

Usage:
    python streaming_test.py
"""

import os
import time

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)

MODEL = "openai/gpt-oss-20b"

# A long-ish answer, so the difference is easy to see.
PROMPT = "Explain in about 200 words what a database index is and why it makes queries faster."


def without_streaming():
    print("\n" + "=" * 60)
    print("RUN 1:  stream=False")
    print("=" * 60)
    print("Sending request... watch the screen. Nothing will happen for a while.\n")

    start = time.time()

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": PROMPT}],
        reasoning_effort="low",
    )

    # This is the first moment anything can possibly be shown.
    first_output = time.time() - start

    print(resp.choices[0].message.content)

    total = time.time() - start
    return first_output, total


def with_streaming():
    print("\n" + "=" * 60)
    print("RUN 2:  stream=True")
    print("=" * 60)
    print("Sending request... watch the screen. Text will grow word by word.\n")

    start = time.time()
    first_output = None
    chunks = 0
    full_text = ""

    stream = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": PROMPT}],
        reasoning_effort="low",
        stream=True,
    )

    for chunk in stream:
        piece = chunk.choices[0].delta.content
        if piece:
            if first_output is None:
                # The very first moment the user sees ANYTHING.
                first_output = time.time() - start
            chunks += 1
            full_text += piece                    # assembling it ourselves
            print(piece, end="", flush=True)

    print()
    total = time.time() - start

    print(f"\n(arrived in {chunks} chunks, {len(full_text)} characters assembled)")
    return first_output, total


def main():
    off_first, off_total = without_streaming()

    print("\n\nPausing 3 seconds so the two runs don't blur together...")
    time.sleep(3)

    on_first, on_total = with_streaming()

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"{'':<14}{'first word':>14}{'finished':>14}")
    print(f"{'stream=False':<14}{off_first:>13.2f}s{off_total:>13.2f}s")
    print(f"{'stream=True':<14}{on_first:>13.2f}s{on_total:>13.2f}s")

    saved = off_first - on_first
    print(f"\nYou started reading {saved:.2f} seconds sooner with streaming.")
    print("Look at the 'finished' column: total time is roughly the SAME.")
    print("Streaming does not make the model faster. It removes the blank wait.")


if __name__ == "__main__":
    main()