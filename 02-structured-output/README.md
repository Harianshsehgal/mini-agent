# 02 — Structured output

## What this step adds

- `naivejson.py` — evidence that "just ask for JSON" fails: 8 runs, count the parses.
- `structuredOutput.py` — three ways to get JSON, weakest to strongest:
  ask nicely → `response_format: json_object` → `response_format: json_schema`.
  Pydantic sits alongside all three as the thing that fails loudly.
- `repairLoop.py` — validate, feed the validation error back, ask the model
  to fix its own output. Up to 3 attempts.

These are three separate demos, not one program. Run them in order — each
answers a problem the previous one exposed.

## What it can't do yet

- No tools. The model still can't act, only emit text/JSON.
- The repair loop can still give up and return `None` after 3 attempts.
- Nothing is retried at the network level — a timeout just fails.
- The repair path is **untested**: every run so far passed on attempt 1,
  so the retry code has never actually executed.

## Two things worth knowing

**Strict schema mode has provider-specific rules.** Groq's `json_schema`
mode requires `additionalProperties: false` on every object, including
nested ones. Pydantic doesn't add that by default, so both models set
`model_config = ConfigDict(extra="forbid")`. Without it the request comes
back as a 400. The docs for a given provider are the only reliable source
here — this is not portable across providers.

**`model_validate_json` swallows `json.JSONDecodeError`.** Pydantic parses
the JSON itself, so text that isn't JSON at all does not raise
`JSONDecodeError` — it comes back as a `ValidationError` with
`type == "json_invalid"`. Broken JSON and wrong-shaped JSON arrive as the
same exception. Checking the error type is the only way to tell them apart.

## How to run it

```bash
python 02-structured-output/naivejson.py
python 02-structured-output/structuredOutput.py
python 02-structured-output/repairLoop.py
```

Each reads `GROQ_API_KEY` from the repo-root `.env`.

## Results

**`naivejson.py` — 0 parsed out of 8.**

Every single reply was wrapped in ` ```json ` markdown fences, so
`json.loads` failed at character 1 every time. Not "usually works". Never
works.

That matters more than a mixed rate would. The failure is _systematic_,
not random — so no amount of retrying fixes it. The method itself is
wrong, which is what makes the next file necessary.

**`structuredOutput.py` — one run, three outcomes:**

| Method            | Result                                        |
| ----------------- | --------------------------------------------- |
| 1 — ask nicely    | Fenced output. Not JSON at all.               |
| 2 — `json_object` | Valid JSON, and this run the right shape too. |
| 3 — `json_schema` | Valid JSON in exactly the requested shape.    |

**Method 2 getting the right shape was luck.** The mode guarantees valid
JSON, not a particular structure. On another run it returned a bare
`[...]` list instead of `{"people": [...]}`, which parsed fine and then
failed validation. That gap — valid but wrong-shaped — is precisely what
method 3 closes.

**`repairLoop.py` — passed on attempt 1, every time so far.**

Which means the repair loop has never actually run. The code exists and
has never been exercised.

## TODO

- [ ] Tighten a constraint in `repairLoop.py` (`min_length=8` on
      employees, say) until a real repair is observable. Untested error
      handling is a guess — the same problem as the `try/except` in
      step 04 that has also never fired.
- [ ] Run `structuredOutput.py` several times and record how often
      method 2 returns the wrong shape. One run is an anecdote.
