"""
Week 1, Day 2 (2.3.3) - the validate-then-repair loop.

When validation fails we hold something useful: an error message saying
exactly what is wrong. Send it back and ask the model to fix its own output.

This is the SAME pattern as Week 5's SQL self-correction:
    bad SQL -> Postgres error -> feed the error back -> repaired SQL
Only the validator changes.

We use a deliberately hard schema so failures actually happen and you can
watch a repair. With an easy schema it would pass first try every time and
you would learn nothing.
"""

import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel,ConfigDict, Field, ValidationError

load_dotenv()

client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)

MODEL = "openai/gpt-oss-20b"
MAX_ATTEMPTS = 3


# ---------------------------------------------------------------- schema
# Constraints here are ENFORCED by pydantic (unlike `description`, which is
# only advice to the model). ge/le = greater/less-or-equal.

class Employee(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    age: int = Field(ge=22, le=65, description="Working age only.")
    salary_inr: int = Field(ge=300_000, le=5_000_000)
    department: str = Field(description="One of: Engineering, Sales, HR.")
    years_experience: int = Field(ge=0, le=40)


class Team(BaseModel):
    model_config = ConfigDict(extra="forbid")
    team_name: str
    employees: list[Employee] = Field(min_length=4, max_length=4)


# Vague on purpose. We are not telling it the numeric ranges, so it has a
# real chance of producing something out of bounds on the first attempt.
PROMPT = (
    "Invent a software team as JSON. Include the team name and its members, "
    "each with name, age, salary in INR, department and years of experience."
)


# ------------------------------------------------------------ the loop

def ask_with_repair() -> Team | None:
    messages = [{"role": "user", "content": PROMPT}]

    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"\n--- attempt {attempt} ---")

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "team",
                    "schema": Team.model_json_schema(),
                    "strict": True,
                },
            },
            reasoning_effort="low",
        )

        raw = response.choices[0].message.content
        print("raw:", raw[:180].replace("\n", " "))

        try:
            team = Team.model_validate_json(raw)
            print(f"VALID on attempt {attempt}")
            return team

        except ValidationError as err:
            print(f"INVALID: {err.error_count()} problem(s)")
            for e in err.errors():
                # loc is the path to the bad field, e.g. ('employees', 0, 'age')
                where = " -> ".join(str(x) for x in e["loc"])
                print(f"   {where}: {e['msg']}")

            if attempt == MAX_ATTEMPTS:
                print("Out of attempts. Giving up.")
                return None

            # Keep the failed attempt IN the conversation. The model needs to
            # see what it wrote next to what was wrong with it.
            messages.append({"role": "assistant", "content": raw})
            messages.append(
                {
                    "role": "user",
                    "content": (
                        "That output failed validation with these errors:\n"
                        f"{err}\n\n"
                        "Return corrected JSON. Fix only the invalid fields "
                        "and keep everything else the same."
                    ),
                }
            )

    return None


if __name__ == "__main__":
    team = ask_with_repair()

    if team:
        print(f"\n{team.team_name}")
        for e in team.employees:
            # Real ints - maths works, no casting needed.
            print(
                f"  {e.name:20} {e.age:3}  {e.department:12} "
                f"Rs {e.salary_inr:>9,}  {e.years_experience}y"
            )
    else:
        print("\nNo valid result.")