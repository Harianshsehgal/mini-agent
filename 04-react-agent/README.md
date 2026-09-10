# 04 — ReAct agent

Step 03 went around the loop once. This one goes around many times:
model → tool → model → tool → … → answer.

That is the whole difference between calling a tool and having an agent.

## The loop, in plain steps

The loop runs at most 6 times. Each time round:

1. **Ask the model.** Send it the whole conversation so far.
2. **Save what it said.** Put the reply into the message list, straight away.
3. **Check the reply.** Did it ask for a tool?
    - **No** → it is answering. Stop, return it.
    - **Yes** → carry on.
4. **Run the tools it asked for.** One at a time. A tool that fails becomes
   a normal sentence, not an exception.
5. **Save each result** into the message list.
6. **Go back to step 1.**

If 6 rounds pass with no answer, one last call is made with the tool list
removed, so the model has to answer with whatever it already found.

Two ways out: the model stops asking for tools, or the cap fires. Both
return a string. Neither crashes.

## What this step adds over 03

Five real changes. Everything else in the diff is comments and print
spacing.

| #   | Change                             | Why                                             |
| --- | ---------------------------------- | ----------------------------------------------- |
| 1   | `while True` → counted loop        | An unbounded loop is an unbounded bill          |
| 2   | `run_tool` grows 2 lines → 14      | Failures become text the model can read         |
| 3   | A system prompt appears            | Tells the model how to behave when a tool fails |
| 4   | A third tool, `find_landmark_city` | Forces two calls **in sequence**                |
| 5   | The cap degrades gracefully        | Answer with what you have, don't discard it     |

Change 2 is the one that changes behaviour most. Change 4 is the one that
makes the loop _need_ to run more than once.

```bash
diff 03-tool-calling/agent.py 04-react-agent/agent.py
```

## Three rules that matter

**Save the model's reply before running the tools.** Not after. A `tool`
message has nothing to attach to if the request that asked for it is not
in the list yet.

**Send the whole list every time.** The model has no memory. Step 4 works
only because everything from steps 1–3 is shown again. Cost climbs with
every step for exactly this reason.

**Tools raise, `run_tool` doesn't.** Functions in `tools.py` fail like
ordinary Python. `run_tool` is the single boundary where an exception
turns into conversation. It must never raise.

## Why errors go back to the model

Ask for the weather at the Eiffel Tower, which isn't in the lookup table:

```
  [step 1]
    -> find_landmark_city({"landmark":"Eiffel Tower"})
    <- Error running find_landmark_city: ValueError: Unknown landmark
       'Eiffel Tower'. Known landmarks: ['taj mahal', 'charminar',
       'gateway of india', 'vaultspire tower']
  [step 2]
A: I'm sorry, but I don't have information on that landmark in the
   available lookup.
```

It did not say "Paris". The error reached the model as text, the model
read it, and it told the truth. Step 03 would have crashed here with an
unhandled traceback.

The error strings are written **for the model**, not for the log. They say
what went wrong _and_ what is available instead. On one run the model
quoted the phrase "landmark database" straight back — wording taken from
the error message. Error strings are prompts.

## Sequential vs batched tool calls

Step 03's third question calls two tools in a **single** step, because
neither depends on the other. Here, `find_landmark_city` must finish
before `get_weather` can start, so they take one step each.

That is the difference between a tool-caller and an agent: the second call
is chosen based on the first one's result.

The tools still run one after another inside a step, in a plain `for` loop.
Making independent calls run concurrently is a real optimisation, and not
done here.

## Design decision: what to do when the cap fires

**First version:** return `"I could not finish within N steps."`

Wasteful. With the cap set to 2, one test question had already found `731`
and `Hyderabad` — and threw both away. Work paid for and discarded.

**Current version:** one final call with the tools removed, telling the
model to answer from what it has. Same question now returns 731,
Hyderabad, and an honest note that the weather was never fetched.

**The trade-off, stated fairly.** The simple version is one line, costs
nothing, and fails loudly — which makes a misbehaving agent obvious. The
current version costs an extra full-context API call, needs error
handling, and can hide the fact that the cap is firing often, because the
output still looks polished.

The rule settled on: **summarise if a human reads the output, fail loudly
if another program does.** This prints to a human, so it summarises.
LangGraph raises `GraphRecursionError` instead, which is right for a
library — it cannot know who is downstream.

Done properly it would return both: a summary for the user and a
`capped: True` flag for the logs. Not implemented.

## Removing tools does not stop the model asking for them

Building the above produced a 400:

```
Tool choice is none, but model called a tool
failed_generation: {"name": "get_weather", "arguments": {"location":"Hyderabad"}}
```

The model tried to call a tool that was not offered. Groq rejected it and
the program died.

**A prompt is a request, not a rule.** Anything that must not happen has to
be blocked in code, not asked for in words. The final call is now wrapped
in `try/except` so a disobedient model cannot kill the run.

## How to run it

```bash
python 04-react-agent/agent.py
```

Reads `GROQ_API_KEY` from the repo-root `.env`.

## Limitations

- **Tools run one after another.** Multiple calls in one step go through a
  plain `for` loop. Two slow tools mean waiting for both.
- **The context only grows.** Nothing is trimmed or summarised. Fine when
  tool results are one line. With 5,000-word web pages this breaks fast.
- **Cost grows with every step**, since the whole list is re-sent each time.
- **`calculator` uses `eval()`.** Unsafe on model-supplied input.
  Deliberate for now; the fix belongs with input validation.
- **The `try/except` on the final call has never fired.** The path exists
  but is untested. Untested error handling is a guess.
- **Tools are fake.** Hardcoded dicts, on purpose — failures are
  controllable and it costs nothing to run.
- No tests, no tracing, no cost tracking.

## TODO

- [ ] Error message for `find_landmark_city` should say the lookup is
      case-insensitive. On one run the model retried with lowercase after a
      failure — a wasted call, because `.strip().lower()` already ran. The
      error didn't tell it that.

- [ ] Run independent tools concurrently
- [ ] Return a `capped` flag alongside the answer
- [ ] Rebuild with `create_agent()` and compare line counts, and what
      visibility is lost
