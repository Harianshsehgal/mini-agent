# 06 — Middleware

The same agent as `04-react-agent`, but built with LangChain's `create_agent`.
New today: a **middleware** that logs every tool call with its latency.

## Run

```
uv pip install langchain langchain-openai
python 06-middleware/agent.py
```

## Output

```
[tool] get_landmark_city {'landmark': 'Taj Mahal'} -> 1 ms
[tool] get_weather {'city': 'Agra'} -> 506 ms

Answer: The weather in Agra, the city where the Taj Mahal is located, is 31 °C and sunny.
```

`get_weather` takes about 500 ms because of `time.sleep(0.5)` (a pretend slow API).

## Why middleware

- In `04-react-agent`, I wrote the loop myself, so I could add any code inside it.
- `create_agent` builds the loop for me, so I can't edit the loop anymore.
- Middleware is how I add my own code inside that loop.

## The flow

1. I call `agent.invoke(...)`.
2. The agent calls the LLM.
3. The LLM says: "run `get_landmark_city`."
4. The agent calls my middleware, not the tool directly.
5. The middleware runs the tool and prints the time.
6. The result goes back to the LLM.
7. The LLM says: "run `get_weather`." Steps 4–6 repeat.
8. The LLM asks for no tool, so the loop stops.
9. I get the final answer.

## Inside `log_tool_latency`

1. The agent gives it `request` (which tool, which args) and `handler` (the button that runs the tool).
2. It reads the tool name and args from `request`.
3. It starts the timer.
4. It runs the tool with `handler(request)`.
5. `finally` stops the timer and prints the name, args, and time (even if the tool fails).
6. It **returns** the result to the agent.

## Things to remember

- **The LLM never runs anything.** It only asks. The agent runs the tool.
- **The tool is defined with `@tool`, not in the middleware.** The middleware only presses the "run" button (`handler`).
- **It runs on every tool call.** One middleware covers all tools.
- **Always `return handler(request)`.** Without `return`, the agent gets `None` and crashes.
- **It's only there if I add it:** `middleware=[log_tool_latency]`. With `middleware=[]`, tools run directly.

## Two kinds of hooks

- **Node-style:** runs at one point — `before_model`, `after_model`, `before_agent`, `after_agent`.
- **Wrap-style:** runs around a call — `wrap_model_call`, `wrap_tool_call`.

To time a tool, I need code before **and** after the call, so I use wrap-style.

## What else middleware can do

- **Block** a tool: don't call `handler`, return a message instead.
- **Retry** a tool: call `handler` again if it fails.
- **Change input or output:** clean the args, or cut a long result.
- **Built-in ones** exist too: human approval before a tool runs, summarising long history, hiding personal data (PII).

## Interview line

> "The model never executes tools. It only returns a tool-call request. The agent loop executes it, and middleware wraps that execution, so I can add logging, retries, or safety checks without rewriting the loop."
