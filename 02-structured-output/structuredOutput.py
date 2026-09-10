"""
Week 1, Day 2 (2.3.2) - three ways to get reliable JSON, weakest to strongest.

  Method 1: ask nicely                  -> hope
  Method 2: response_format json_object -> guaranteed VALID json, ANY shape
  Method 3: response_format json_schema -> guaranteed valid json in YOUR shape

Pydantic sits alongside all three. Its job is not to produce JSON.
Its job is to FAIL LOUDLY when the JSON is not what you expected.
"""

import json
import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError

load_dotenv()

client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)

MODEL = "openai/gpt-oss-20b"


# ---------------------------------------------------------------- schema

class Person(BaseModel):
    name: str
    age: int                      # note: int, not str. This is the trap we want.
    occupation: str


class People(BaseModel):
    """A wrapper, because most APIs want a top-level OBJECT, not a list."""
    people: list[Person] = Field(description="Exactly three fictional people.")


PROMPT = "Give me three fictional people as JSON: name, age, occupation."


# ------------------------------------------------------- method 1: hope

def method_1_ask_nicely() -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": PROMPT}],
        reasoning_effort="low",
    )
    return response.choices[0].message.content


# ------------------------------------------ method 2: json_object mode

def method_2_json_mode() -> str:
    """
    The server now CONSTRAINS generation so the output must be valid JSON.
    It cannot emit backticks or a preamble - those tokens are unavailable.

    Limitation: valid JSON, but any shape it likes. It might return
    {"people": [...]} or {"person_1": {...}} or a bare list.
    You still do not know what you are getting.

    Note: the word "JSON" must appear in the prompt for this mode.
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": PROMPT}],
        response_format={"type": "json_object"},
        reasoning_effort="low",
    )
    return response.choices[0].message.content


# ----------------------------------------- method 3: json_schema mode

def method_3_json_schema() -> str:
    """
    Now we hand over the exact shape. Pydantic generates the JSON Schema
    for us - look at what model_json_schema() prints, it is the same kind
    of dict you hand-wrote in schemas.py this morning.

    Not every model/provider supports this. If it 400s, that is the
    provider telling you so - fall back to method 2 plus validation.
    """
    schema = People.model_json_schema()

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": PROMPT}],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "people",
                "schema": schema,
                "strict": True,
            },
        },
        reasoning_effort="low",
    )
    return response.choices[0].message.content


# -------------------------------------------------------- the validator

def validate(raw: str) -> People | None:
    """
    This is the part that matters, and it is independent of the method above.
    Even a perfect schema mode can hand you age="twenty-nine".
    Pydantic turns that into an exception NOW instead of a bug three
    steps later in some other file.
    """
    try:
        return People.model_validate_json(raw)
    except ValidationError as err:
        print("  VALIDATION FAILED:")
        print("  " + str(err).replace("\n", "\n  "))
        return None
    except json.JSONDecodeError:
        print("  NOT EVEN JSON")
        return None


# --------------------------------------------------------------- runner

def try_method(label: str, fn) -> None:
    print("=" * 60)
    print(label)
    try:
        raw = fn()
    except Exception as err:            # provider rejected the request
        print(f"  REQUEST FAILED: {type(err).__name__}: {err}")
        return

    print("  raw:", repr(raw[:200]))

    result = validate(raw)
    if result:
        print(f"  VALID -> {len(result.people)} people")
        for p in result.people:
            # p.age is a real int here. You can do maths on it.
            print(f"    {p.name}, {p.age}, {p.occupation}")


if __name__ == "__main__":
    print("The schema Pydantic generates for us:")
    print(json.dumps(People.model_json_schema(), indent=2))
    print()

    try_method("METHOD 1 - ask nicely", method_1_ask_nicely)
    try_method("METHOD 2 - json_object mode", method_2_json_mode)
    try_method("METHOD 3 - json_schema mode", method_3_json_schema)