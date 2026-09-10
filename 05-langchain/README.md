# 05 — LangChain basics

Steps 01–04 built everything by hand: the model call, the tool schemas, the
tool-calling loop. This step does the same jobs with LangChain 1.x, to see
what the framework does for me and what it hides from me.

Status: sessions 4.1–4.3b done. 4.4 (`agent.py` with `create_agent`) is next.

---

## Setup

From the repo root, with `.venv` active:

```bash
uv pip install langchain langchain-groq
```

Versions used:

| Package          | Version | Note                                             |
| ---------------- | ------- | ------------------------------------------------ |
| `langchain`      | 1.4.0   |                                                  |
| `langchain-groq` | 1.1.3   | uses Groq's own `groq` SDK, not the `openai` SDK |
| `langgraph`      | 1.2.11  | not installed by me; `langchain` pulls it in     |

The `.env` at the repo root must have `GROQ_API_KEY`. Model: `openai/gpt-oss-20b`.

## How to run

Always from the repo root:

```bash
python 05-langchain/basics.py       # 4.1 + 4.3 + 4.3b
python 05-langchain/tools.py        # 4.2 — prints each tool's schema
python 05-langchain/round_trip.py   # 4.2 — one tool round trip with the model
```

`basics.py` and `round_trip.py` do `from tools import TOOLS`. This finds
`05-langchain/tools.py`, because Python looks for imports in the same folder
as the script you run.

## Files

| File            | Session        | What it does                                                                                              |
| --------------- | -------------- | --------------------------------------------------------------------------------------------------------- |
| `basics.py`     | 4.1, 4.3, 4.3b | One model call and a close look at the reply. Then prompt templates and LCEL (the `\|` pipe and friends). |
| `tools.py`      | 4.2            | The same three tools as step 04, built with `@tool`. No `schemas.py` needed.                              |
| `round_trip.py` | 4.2            | Ask → model requests a tool → I run it → send result back → final answer. Same job as step 03.            |

`tools.py` shares its name with `04-react-agent/tools.py` on purpose, so the two
can be diffed. `round_trip.py` has no match in step 03; compare it by hand.

---

## What LangChain replaces

| Built by hand (steps 01–04)                      | LangChain (this step)                                       |
| ------------------------------------------------ | ----------------------------------------------------------- |
| `OpenAI(...)` client pointed at Groq             | `ChatGroq` model object                                     |
| `client.chat.completions.create(...)`            | `model.invoke(messages)`                                    |
| `response.choices[0].message`                    | `invoke` returns an `AIMessage` directly                    |
| Message dicts `{"role": "user", ...}`            | `SystemMessage`, `HumanMessage`, `AIMessage`, `ToolMessage` |
| Hand-written JSON schemas in `schemas.py`        | `@tool` builds them from the function                       |
| `tools=...` in every API call                    | `model.bind_tools(TOOLS)` once                              |
| `json.loads` on tool arguments                   | arguments arrive as a dict                                  |
| `model_dump(exclude_none=True)` before appending | append the `AIMessage` object as it is                      |

---

## 4.1 — One model call

**What comes back is an object.** `model.invoke(messages)` returns an
`AIMessage`. It is an object (one filled-in copy) of the class `AIMessage`
(the blueprint).

**The same reply lives in several places:**

| Field                                     | What it holds                                                                                                     |
| ----------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `.content`                                | Only the final answer. No reasoning.                                                                              |
| `.content_blocks`                         | Everything, in LangChain's standard shape: a `reasoning` block and a `text` block. Same shape for every provider. |
| `.additional_kwargs["reasoning_content"]` | The reasoning in Groq's raw, provider-specific form.                                                              |
| `.usage_metadata`                         | Token counts.                                                                                                     |

**Token counts have new names:**

| Raw SDK (step 01)   | LangChain       |
| ------------------- | --------------- |
| `prompt_tokens`     | `input_tokens`  |
| `completion_tokens` | `output_tokens` |
| `total_tokens`      | `total_tokens`  |

**Reasoning tokens cost money.** For "What is the capital of France?":
43 output tokens, and 27 of them were reasoning. Less than half of the output
was the visible answer, but I pay for all of it.

**Where `AIMessage` comes from:**

- It is **defined** in `langchain-core` (`langchain_core/messages/ai.py`).
- `langchain` only **re-exports** it, so `from langchain.messages import AIMessage`
  and `langchain_core.messages.AIMessage` are the same class (checked: `is` → `True`).
- `langchain-groq` **creates** `AIMessage` objects from Groq's raw response.
  Every provider package creates the same class, so every provider gives the same shape.
- Its parents are `BaseMessage` (parent of all messages) and Pydantic's `BaseModel`
  (that's why `model_dump()` works).

**Import rule:** I only import a class when I write its name in my own code.
`basics.py` got an `AIMessage` back without importing it, because the object was
created inside `langchain-groq`.

---

## 4.2 — Tools with `@tool`, and one round trip

**`@tool` turns a function into an object.** The type becomes `StructuredTool`.
It is no longer callable like a function:

```python
get_weather("Agra")                    # TypeError: 'StructuredTool' object is not callable
get_weather.invoke({"city": "Agra"})   # works
```

**Where `@tool` gets each part of the schema:**

| Schema part            | Comes from                          |
| ---------------------- | ----------------------------------- |
| name                   | the function name                   |
| parameter type         | the type hint (`city: str`)         |
| tool description       | the docstring                       |
| required parameters    | parameters with no default value    |
| parameter descriptions | **nothing, by default** — see below |

**The docstring is required.** Without one, the file fails as soon as it
loads (decorators run when Python reads the file):

```
ValueError: Function must have a docstring if description not provided.
```

**The docstring is for the model. `#` comments are for humans.** The docstring
is sent to the model as the tool description. Private notes (like "eval() is
unsafe") go in `#` comments.

**Parameter descriptions need `parse_docstring=True`** and an `Args:` section:

```python
@tool(parse_docstring=True)
def get_weather(city: str) -> str:
    """Get the current weather for a city.

    Args:
        city: Name of the city in English, for example 'Agra'.
    """
```

- If I write `Args:` but forget `parse_docstring=True`, the whole `Args:` text
  goes into the tool description, and the parameter still gets no description.
- The name in `Args:` must match the parameter name exactly. Otherwise:
  `ValueError: Arg town in docstring not found in function signature.`

**The schema is correct OpenAI format**, with the `"type": "function"` wrapper
and `parameters`. (Step 02 had a bug from getting this wrong by hand.)
`ChatGroq.bind_tools` runs `convert_to_openai_tool` on every tool, so what
`tools.py` prints is what Groq receives.

**Round trip findings (`round_trip.py`):**

- `call["args"]` is already a `dict`. No `json.loads`.
- When the model asks for a tool, `ai_msg.content` is `''` (the raw SDK gave `None`).
- Each tool call has a standard shape: `{'name', 'args', 'id', 'type': 'tool_call'}`.
- Tool calls with broken JSON go to `ai_msg.invalid_tool_calls`, not `tool_calls`.
- `messages.append(ai_msg)` just works. The list holds message objects, and
  `ChatGroq` converts them to Groq's format before sending, keeping `tool_calls`.
  So the missing-`tool_calls` bug from step 02 cannot happen here.

**What LangChain did, and what I still did:**

| LangChain did it                   | I still did it                                                  |
| ---------------------------------- | --------------------------------------------------------------- |
| Built the tool schemas             | Looped over `ai_msg.tool_calls`                                 |
| Sent the tools with every call     | Found the right tool by name                                    |
| Turned the JSON string into a dict | Ran the tool                                                    |
| Kept `tool_calls` when sending     | Appended in the right order: `ai_msg` first, then `ToolMessage` |

LangChain removed the formatting work. The loop logic is still mine
(until `create_agent` in 4.4).

---

## 4.3 — Prompt templates and the `|` pipe (LCEL)

**A prompt template is a message maker.** Dict in, messages out:

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Answer in {style}."),
    ("human", "{question}"),
])
filled = prompt.invoke({"style": "one sentence", "question": "..."})
```

- `filled` is a `ChatPromptValue`, a wrapper. `.to_messages()` gives a
  `SystemMessage` and a `HumanMessage`, the same objects I built by hand in 4.1.
- `prompt.input_variables` lists the blanks, sorted alphabetically.
- A missing key fails with
  `KeyError: "Input to ChatPromptTemplate is missing variables {'style'}. ..."`

**The pipe joins steps into a line.** This is LCEL (LangChain Expression Language).
Each step's output is the next step's input:

```
dict → [prompt] → messages → [model] → AIMessage → [parser] → string
```

```python
chain = prompt | model | StrOutputParser()
chain.invoke({"style": "three words", "question": "Why is the sky blue?"})
# → "Rayleigh scattering dominates."
```

- The chain is a `RunnableSequence` with three steps.
- `StrOutputParser` returns only the text. **It throws away the reasoning and
  `usage_metadata`.** The tokens are still used and paid for; I just can't see
  them. To keep them, use `prompt | model` without the parser.

**Everything is a `Runnable`.** The prompt, the model, the parser, the chain,
and the tool all passed `isinstance(obj, Runnable)`. Every Runnable has
`invoke`, `stream`, and `batch`, and can be joined with `|`. That is why
`invoke` works on everything. A chain is also a Runnable, so a chain can be a
step inside a bigger chain.

**Three ways to write the same message:**

```python
{"role": "system", "content": "..."}   # dict (step 01)
SystemMessage("...")                   # class (4.1)
("system", "...")                      # tuple (4.3, inside templates)
```

---

## 4.3b — More LCEL pieces

A chain is a line of workers. Each worker does one job and passes the result on.
4.3b adds three new kinds of workers.

**`RunnableLambda` — my own function as a worker.**

1. I wrote a normal function, `add_word_count`. It knows nothing about LangChain.
2. I put it in the chain with `|`.
3. LangChain wrapped it in a `RunnableLambda`, so it fits in the line.
4. The chain now returns what my function returns: a dict.

Result: `{'answer': 'The largest planet in our solar system is Jupiter.', 'words': 9}`

**`RunnableParallel` — several workers at the same time.**

1. Two chains get the same question.
2. They run at the same time, not one after the other.
3. The answers come back in a dict, with the names I chose.

Result: `{'one_word': 'Jupiter', 'one_sentence': 'Jupiter is the largest planet in our solar system.'}`

Time: 0.55 s in parallel vs 1.08 s one after the other. About 2× faster.

**`RunnablePassthrough` — a mini RAG chain.**

The prompt has two blanks (`{context}` and `{question}`), but the user gives
only one thing: the question. The flow:

1. `rag_chain.invoke(question)` gets one string, the question.
2. The dict at the start makes a new dictionary from it:
    - `context`: made by calling `fake_retriever(question)`
    - `question`: the same question, unchanged (this is `RunnablePassthrough`)
3. `rag_prompt` uses this dictionary to fill its two blanks.
4. `model` reads the messages and answers.
5. `StrOutputParser` keeps only the text.

```python
rag_chain = (
    {"context": fake_retriever, "question": RunnablePassthrough()}
    | rag_prompt
    | model
    | StrOutputParser()
)
```

Result: `Vaultspire Tower is 300 metres tall.` Vaultspire Tower is fictional,
so the model could only know this from the context.

Good to know:

- A dict at the start of a chain becomes a `RunnableParallel` automatically.
- `RunnablePassthrough()` does the same as `lambda q: q`.
- On Friday, `fake_retriever` becomes a real retriever that searches documents.
  The rest of the chain stays the same.

---

## Chain vs agent

- **Chain:** I choose the steps when I write the code. They run once, in the
  same order, every time. No loop.
- **Agent:** the model chooses the next step (call a tool, or stop), in a loop,
  until it stops.

---

## Gained vs lost (so far)

| What I gained                                    | What I can no longer see                                                      |
| ------------------------------------------------ | ----------------------------------------------------------------------------- |
| No hand-written schemas                          | The exact JSON sent to Groq (unless I print it with `convert_to_openai_tool`) |
| Same message and token shapes for every provider | Groq's raw response (it's converted into an `AIMessage`)                      |
| No `json.loads`, no `model_dump`                 | How messages are converted before sending                                     |
| `invoke` / `stream` / `batch` on everything      | With `StrOutputParser`: reasoning and token counts                            |

To be completed in 4.4–4.5, after `create_agent` and the line-count comparison.

---

## Notes

- `round_trip.py`'s final answer used markdown (`**bold**`, `-` bullets),
  because nothing told the model not to. A system prompt can fix this.
- Old tutorials using `AgentExecutor`, `initialize_agent`, or `LLMChain` are
  pre-1.0 and outdated.
