# 05 — LangChain basics

Steps 01–04 built an agent by hand. This step rebuilds the same agent with
LangChain 1.x. The goal: learn what the framework does for me, and what it
hides from me.

---

## Setup

From the repo root, with `.venv` active:

```bash
uv pip install langchain langchain-groq
```

Versions used: `langchain` 1.4.0, `langchain-groq` 1.1.3, `langgraph` 1.2.11.
I did not install `langgraph` myself. `langchain` needs it, so it came automatically.

The `.env` at the repo root needs `GROQ_API_KEY`. Model: `openai/gpt-oss-20b`.

## How to run

Always from the repo root:

```bash
python 05-langchain/basics.py           # 4.1, 4.3, 4.3b
python 05-langchain/tools.py            # 4.2: print each tool's schema
python 05-langchain/round_trip.py       # 4.2: one tool round trip
python 05-langchain/agent_1_basic.py    # 4.4 stage 1: crashes on Big Ben (on purpose)
python 05-langchain/agent_2_errors.py   # 4.4 stage 2: tool errors go to the model
python 05-langchain/agent.py            # 4.4 final: + a polite step cap
```

## Files

- `basics.py` — one model call, prompt templates, and LCEL.
- `tools.py` — the same three tools as step 04, built with `@tool`.
- `round_trip.py` — one tool round trip, done by hand. Same job as step 03.
- `agent_1_basic.py` — `create_agent`, no error handling.
- `agent_2_errors.py` — adds safe error handling.
- `agent.py` — adds a step cap. Compare it with `04-react-agent/agent.py`.

Each agent file adds **one** new idea to the one before it.

---

## What LangChain replaces

| Built by hand (steps 01–04)                   | LangChain (this step)                                       |
| --------------------------------------------- | ----------------------------------------------------------- |
| `OpenAI(...)` client pointed at Groq          | `ChatGroq`                                                  |
| Message dicts `{"role": ..., "content": ...}` | `SystemMessage`, `HumanMessage`, `AIMessage`, `ToolMessage` |
| Hand-written schemas in `schemas.py`          | `@tool`                                                     |
| `json.loads` on tool arguments                | Arguments arrive as a dict                                  |
| My `while` loop                               | `create_agent`                                              |
| My error handling                             | `ToolErrorMiddleware`                                       |
| My step cap                                   | `ModelCallLimitMiddleware`                                  |

---

## 4.1 — One model call

1. `model.invoke(messages)` returns an `AIMessage` object.
2. `.content` has only the final answer.
3. `.content_blocks` has everything: a `reasoning` block and a `text` block.
   This shape is the same for every provider.
4. Token counts are called `input_tokens` and `output_tokens`.
5. Reasoning costs money. For an easy question: 43 output tokens, 27 of them reasoning.
6. `AIMessage` is defined in `langchain-core`. `langchain` only re-exports it.
   `langchain-groq` creates the objects.

## 4.2 — Tools and one round trip

**Tools with `@tool`:**

1. `@tool` turns a function into a `StructuredTool` object.
2. I call it with `.invoke({"city": "Agra"})`, not like a normal function.
3. It reads the name from the function name, the types from the type hints,
   and the description from the docstring.
4. The docstring is required. Without it: `ValueError: Function must have a docstring...`
5. The docstring is for the model. `#` comments are for humans.
6. Parameter descriptions need `@tool(parse_docstring=True)` and an `Args:` section.
7. The schema comes out in correct OpenAI format, with the `"type": "function"` wrapper.

**One round trip (`round_trip.py`):**

1. `model.bind_tools(TOOLS)` attaches the tools to the model once.
2. The model asks for a tool. `ai_msg.content` is empty, and `ai_msg.tool_calls` has the request.
3. The arguments are already a dict. No `json.loads`.
4. I append `ai_msg` as it is. LangChain converts it before sending,
   so the missing-`tool_calls` bug from step 02 cannot happen.
5. LangChain removed the formatting work. But the loop logic was still mine.

## 4.3 — Prompt templates and LCEL

1. A prompt template is a message with blanks: `"Answer in {style}."`
2. `prompt.invoke({...})` fills the blanks and returns the messages.
3. The pipe `|` joins steps into a line. This is **LCEL**
   (LangChain Expression Language).
4. `prompt | model | StrOutputParser()`: each step's output is the next step's input.
5. `StrOutputParser` returns plain text. It throws away the reasoning and token
   counts, but I still pay for them.
6. Everything is a `Runnable`: prompt, model, parser, chain, tool.
   So everything has `invoke`, `stream`, and `batch`.

## 4.3b — More LCEL pieces

1. **`RunnableLambda`:** puts a normal Python function into a chain.
   A plain function in a chain is wrapped automatically.
2. **`RunnableParallel`:** sends one input to several chains at the same time,
   and returns a dict. Two calls took 0.55 s in parallel vs 1.08 s one after the other.
3. **`RunnablePassthrough`:** passes the input on, unchanged.

A mini RAG chain uses all of this:

```python
rag_chain = (
    {"context": fake_retriever, "question": RunnablePassthrough()}
    | rag_prompt
    | model
    | StrOutputParser()
)
```

The flow:

1. `rag_chain.invoke(question)` gets one string, the question.
2. The dict makes a new dictionary from it:
   `context` from calling `fake_retriever(question)`, and `question` kept unchanged.
3. `rag_prompt` uses this dictionary to fill its two blanks.
4. `model` answers.
5. `StrOutputParser` keeps only the text.

Result: "Vaultspire Tower is 300 metres tall." The tower is fictional,
so this answer could only come from the context.

---

## 4.4 — The agent with `create_agent`

**What `create_agent` does inside `agent.invoke(...)`:**

1. The model reads the messages and replies.
2. If the reply asks for a tool, the tool runs.
3. The result is added to the messages as a `ToolMessage`.
4. Back to step 1.
5. When the model asks for no tool, the loop stops.

This is my step 04 loop. I no longer write it.

**What I found:**

1. `create_agent` returns a `CompiledStateGraph`: a LangGraph graph.
2. Its nodes are `model` and `tools`.
3. The system prompt is added to every model call, but it is not saved
   in the message list.
4. The result's message list is my step 04 scratchpad.

### Stage 1: tool errors crash (`agent_1_basic.py`)

1. The model asks for `find_landmark_city("Big Ben")`.
2. The tool raises a `ValueError`.
3. LangChain does not catch it. The whole run crashes.

This is different from step 04, where errors went to the model as text.
The reason is safety: an error message can contain private details,
so LangChain does not send errors to the model unless I choose to.

### Stage 2: tool errors go to the model (`agent_2_errors.py`)

`ToolErrorMiddleware` calls my function when a tool fails:

```python
def on_tool_error(error, request):
    if isinstance(error, ValueError):
        return f"Error: {error}"          # my own errors: safe to send
    return "Error: the tool failed. Tell the user to try again later."
```

The flow:

1. A tool fails.
2. The middleware calls `on_tool_error`.
3. A `ValueError` (the kind my tools raise) sends its message.
   Any other error sends only a general message, so private details stay hidden.
4. The text becomes a `ToolMessage`.
5. The model reads it on the next call, and decides what to do.

Good to know:

- `f"Error: {error}"` sends only the error's **message**. Not its type,
  traceback, or notes.
- LangChain does not retry. The **model** may choose to try again with different input.
- This middleware only handles errors while a tool runs. Bad arguments are
  already sent to the model as text by default.

### Final: a polite step cap (`agent.py`)

`ModelCallLimitMiddleware(run_limit=6, exit_behavior="end")` does the job of
my step 04 cap.

1. It counts **model calls**. Each loop turn has one model call,
   so capping model calls stops the tool-calling loop too.
2. `before_model` checks the count. If the limit is reached, it stops the loop
   before the next call.
3. `after_model` adds 1 to the count.
4. That's why the graph now has two extra nodes:
   `ModelCallLimitMiddleware.before_model` and `.after_model`.

Test: the Vaultspire question needs 3 model calls. With a cap of 2,
the agent stopped with `Model call limits exceeded: run limit (2/2)`.
That message was added by the middleware, not written by the model.

To limit **one specific tool** instead, there is `ToolCallLimitMiddleware`.

---

## Line count

|              | Step 04 | Step 05 |
| ------------ | ------- | ------- |
| `agent.py`   | 150     | 75      |
| `schemas.py` | 84      | —       |
| `tools.py`   | 63      | 90      |
| **Total**    | **297** | **165** |

About 44% less code. Most of the 75 lines in `agent.py` are printing and tests.
The agent itself is one `create_agent(...)` call.

## What I gained

1. No hand-written schemas.
2. No loop code.
3. No message-format bugs.
4. Error handling and the step cap are one line each.
5. The agent is a LangGraph graph, so Week 2 features can plug in.

## What I can no longer see or control

1. The loop is hidden. I can only add logic at the points LangChain offers.
2. The defaults can differ from my design. Tool errors crash by default.
   I only found out because I tested it.
3. Some things are hidden: the system prompt, the call counter.
4. Some behaviour is fixed, like the step cap's stop message.
5. Debugging is harder. Errors pass through many LangGraph files.
   This is why tracing (LangSmith) matters.

---

## Chain vs agent

- **Chain:** I choose the steps. They run once, in the same order.
- **Agent:** the model chooses the next step, in a loop, until it stops.

## How much control do I need?

1. `create_agent` with settings: fast and simple.
2. `create_agent` with middleware: more control, at fixed points.
3. LangGraph: full control. I build the loop myself (Week 2).

---

## Notes

- Tutorials that use `AgentExecutor`, `initialize_agent`, or `LLMChain`
  are from before LangChain 1.0. They are outdated.
- The system prompt says "plain text, without markdown", because the model
  used markdown in `round_trip.py` when nothing told it not to.
