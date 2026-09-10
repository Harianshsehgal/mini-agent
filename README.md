# mini-agent

<!-- TODO (me): rewrite this intro in my own words. Something like:
     an agent, built by hand with no framework, to understand what one
     actually is before using one. -->

A tool-calling agent built by hand, no framework. Runs on Groq via the
OpenAI SDK. Four steps, each a folder, each runnable on its own.

## Setup

### Every time you sit down (macOS / zsh)

    cd ~/Documents/Hariansh/learningAgents/mini-agent
    source .venv/bin/activate

Your prompt should now start with `(mini-agent)`. To leave:

    deactivate

### First time on a new machine

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

Then create a `.env` file in this folder:

    GROQ_API_KEY=gsk_your_key_here

`.env` is gitignored. Never commit it.

## Tutorial steps

Each folder is a standalone snapshot — a frozen picture of what was known
that day. Run any one on its own. Folders share filenames on purpose so
they can be diffed against each other.

Folder numbers are steps, not days. Day 2 covered two topics, so it
produced two folders.

| Folder                  | Files                                                                                       | What it is                                                                                                             |
| ----------------------- | ------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `01-cli-chatbot/`       | `chat.py`                                                                                   | Streaming CLI chatbot. No tools. Memory is a Python list.                                                              |
| `02-structured-output/` | `naivejson.py`, `structuredOutput.py`, `repairLoop.py`                                      | Getting reliable JSON: watch plain prompting fail, then `json_object` / `json_schema` modes, then validate-and-repair. |
| `03-tool-calling/`      | `peek.py`, `schemas.py`, `tools.py`, `agent.py`                                             | The model asks for a function, your code runs it, the result goes back. One round trip. No error handling yet.         |
| `04-react-agent/`       | `agent.py`, `tools.py`, `schemas.py`                                                        | The ReAct loop: model → tool → model → … → answer, with a step cap and errors-as-text.                                 |
| `experiments/`          | `test_key.py`, `list_models.py`, `see_chunks.py`, `streaming_test.py`, `temp_experiment.py` | Not a step. Scratch files: key smoke test, model list, Day 1 streaming pokes.                                          |

`.env` lives at the repo root (this folder) and is gitignored. Every script
calls bare `load_dotenv()`, which walks up from the script's folder and
finds it — no per-folder path fix is needed.

## What changed between steps

<!-- TODO (me): I write the reasoning in each section below. The headings
     mark the jumps; the "why" is mine to fill in. -->

### 01 → 02: from "it talks" to "it emits data you can trust"

<!-- TODO (me): why plain-JSON prompting isn't enough — 0/8 parsed, every
     reply fenced in backticks; what json_object buys you vs json_schema;
     where Pydantic fits; why a repair loop. -->

### 02 → 03: from "one round trip" to "the model can act"

<!-- TODO (me): what a tool schema is and why the description IS a prompt;
     the two-file split and the name kept in sync in three places; what the
     raw tool-call response looks like; why inspect before parsing. -->

### 03 → 04: from "one tool call" to "a loop"

<!-- TODO (me): the scratchpad; the stop condition (no tool_calls); the
     step cap and why; turning tool errors into text instead of exceptions;
     the chained question that forces two calls in sequence.

     Useful command: diff 03-tool-calling/agent.py 04-react-agent/agent.py -->

## Notes

Model: `openai/gpt-oss-20b` on Groq. Small and fast; tool-calling
reliability is lower than large models, so an occasional missed tool
call is the model, not the code.
