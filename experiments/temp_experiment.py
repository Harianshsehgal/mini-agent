"""
Week 1, Day 1 - Block 2 experiments.

Five experiments that show how an LLM API really behaves.
Run them one at a time and READ THE OUTPUT. The point is what surprises you.

Usage:
    python experiments.py          -> menu
    python experiments.py 3        -> run experiment 3 only
    python experiments.py all      -> run everything
"""

import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)

MODEL = "openai/gpt-oss-20b"


def header(text):
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)


# ---------------------------------------------------------------
# EXPERIMENT 1 - The API has no memory
# ---------------------------------------------------------------
def experiment_1_no_memory():
    header("EXPERIMENT 1: the API has no memory")

    first = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": "Say hello in exactly 5 words."}],
        reasoning_effort="low",
    )
    print("Call 1 ->", first.choices[0].message.content)

    # A brand new call. Nothing from call 1 is sent.
    second = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": "What did I just ask you?"}],
        reasoning_effort="low",
    )
    print("Call 2 ->", second.choices[0].message.content)

    print("\nWHAT TO NOTICE:")
    print("Call 2 has no idea about call 1. The server forgot instantly.")
    print("Chatbots 'remember' only because the app resends the whole history.")


# ---------------------------------------------------------------
# EXPERIMENT 2 - The system role changes behaviour
# ---------------------------------------------------------------
def experiment_2_system_role():
    header("EXPERIMENT 2: the system role")

    question = "What is Python?"

    personalities = [
        "You are a grumpy pirate. Never say more than one sentence.",
        "You are a formal university professor. Be precise and dry.",
    ]

    for persona in personalities:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": persona},
                {"role": "user", "content": question},
            ],
            reasoning_effort="low",
        )
        print(f"\nSYSTEM: {persona}")
        print(f"ANSWER: {resp.choices[0].message.content}")

    print("\nWHAT TO NOTICE:")
    print("Same user question. Very different answers.")
    print("In week 5 your SQL agent's system message holds the DB schema.")


# ---------------------------------------------------------------
# EXPERIMENT 3 - Temperature controls randomness
# ---------------------------------------------------------------
def experiment_3_temperature():
    header("EXPERIMENT 3: temperature")

    prompt = "Write one sentence about the sea."

    for temp in [0.0, 1.5]:
        print(f"\n--- temperature = {temp} ---")
        for run in range(1, 4):
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=temp,
                reasoning_effort="low",
            )
            print(f"Run {run}: {resp.choices[0].message.content.strip()}")

    print("\nWHAT TO NOTICE:")
    print("At 0.0 the three runs are nearly identical.")
    print("At 1.5 they vary a lot.")
    print("Use temperature=0 whenever there is a correct answer (SQL, extraction).")


# ---------------------------------------------------------------
# EXPERIMENT 4 - The token budget trap
# ---------------------------------------------------------------
def experiment_4_token_budget():
    header("EXPERIMENT 4: max_completion_tokens and the empty answer")

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": "Explain what an API is."}],
        max_completion_tokens=50,
    )

    # repr() so an empty string is visible as '' instead of a blank line.
    print("content       ->", repr(resp.choices[0].message.content))
    print("finish_reason ->", resp.choices[0].finish_reason)
    print("usage         ->", resp.usage)

    print("\nWHAT TO NOTICE:")
    print("The answer is probably EMPTY, and finish_reason is 'length'.")
    print("Reasoning tokens count against the budget. The model spent all 50")
    print("thinking and had nothing left to write with. Not a bug - a budget.")
    print("\nNow try again with a bigger budget:")

    resp2 = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": "Explain what an API is."}],
        max_completion_tokens=400,
    )
    print("content       ->", repr(resp2.choices[0].message.content[:120]), "...")
    print("finish_reason ->", resp2.choices[0].finish_reason)


# ---------------------------------------------------------------
# EXPERIMENT 5 - Streaming
# ---------------------------------------------------------------
def experiment_5_streaming():
    header("EXPERIMENT 5: streaming")

    stream = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": "Count from 1 to 20 slowly."}],
        stream=True,
        reasoning_effort="low",
    )

    chunk_count = 0
    for chunk in stream:
        chunk_count += 1
        piece = chunk.choices[0].delta.content
        if piece:                       # some chunks carry no text at all
            print(piece, end="", flush=True)
    print()

    print(f"\nWHAT TO NOTICE:")
    print(f"The text arrived in {chunk_count} separate chunks, not all at once.")
    print("It is 'delta' not 'message' - each chunk holds only the NEW piece.")
    print("Cost: with stream=True there is no usage object. You lose token counts.")


EXPERIMENTS = {
    "1": experiment_1_no_memory,
    "2": experiment_2_system_role,
    "3": experiment_3_temperature,
    "4": experiment_4_token_budget,
    "5": experiment_5_streaming,
}


def main():
    choice = sys.argv[1] if len(sys.argv) > 1 else None

    if choice is None:
        print("Which experiment?")
        print("  1  no memory")
        print("  2  system role")
        print("  3  temperature")
        print("  4  token budget trap")
        print("  5  streaming")
        print("  all")
        choice = input("> ").strip()

    if choice == "all":
        for fn in EXPERIMENTS.values():
            fn()
    elif choice in EXPERIMENTS:
        EXPERIMENTS[choice]()
    else:
        print(f"Unknown choice: {choice}")


if __name__ == "__main__":
    main()