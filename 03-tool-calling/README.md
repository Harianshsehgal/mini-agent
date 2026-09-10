# 03 — Tool calling

The model gets a list of functions it can request. It picks one, your code
runs it, and the result goes back into the conversation. One round trip.

## What this step adds

- `schemas.py` — JSON descriptions of the tools, written by hand. This is
  the only thing the model ever sees about them.
- `tools.py` — the actual Python functions. Plain code, no magic.
- `peek.py` — the raw response, unparsed. Prints `finish_reason`, `content`
  and each `tool_calls` entry so you can see the shape before writing code
  that depends on it.
- `agent.py` — the loop. Ask, run what it asks for, feed the result back,
  ask
