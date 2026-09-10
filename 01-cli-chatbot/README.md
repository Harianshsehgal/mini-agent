# 01 — CLI chatbot

## What this step adds

- A bare REPL loop over the provider SDK. No framework.
- Conversation memory is just a Python list (`messages`) that grows each turn.
- Streaming the reply and reading token usage off the stream.

## What it can't do yet

- No tools. It can only talk.
- No structured output, no validation.
- No persistence — history dies when the process exits.

## How to run it

python 01-cli-chatbot/chat.py

Reads `GROQ_API_KEY` from the repo-root `.env`.

## Two things worth noticing when you run it

**The list is the memory.** Ask it your name, then ask it what your name
is. It answers correctly not because it remembers, but because the whole
list is re-sent on every call. Remove the `messages.append` for the
assistant reply and it goes deaf to its own answers.

**Watch the token count grow.** Three short turns cost 226, then 284,
then 340 tokens. Each turn re-sends everything before it, so cost climbs
even when your questions get shorter. Harmless here. This is the same
curve that makes long agent runs expensive.

## Repair note

This file was committed mid-refactor and did not compile. The streaming
block from a separate experiment (`experiments/see_chunks.py`) had been
pasted over the real loop, so the file sent a hardcoded `"Say hi"`
instead of `messages`, never assigned `reply`, and never counted tokens.

Fixed by restoring the streaming loop: collect each chunk's text into a
list while printing it, join at the end, append that as the assistant
message. The guard `if chunk.choices and ...` matters — the final chunk
carries usage and has an empty `choices` list, so indexing it blindly
raises `IndexError` on the last chunk of every reply.
