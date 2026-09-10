"""Step 05 — agent final: tool errors as text + a polite step cap.

4.4.3: the same job as 04-react-agent/agent.py.
Stage 1 (agent_1_basic.py):  crashes on tool errors.
Stage 2 (agent_2_errors.py): tool errors go to the model as text.
Final   (this file):         also stops politely after MAX_MODEL_CALLS model calls.
"""
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware, ToolErrorMiddleware
from langchain_groq import ChatGroq

from tools import TOOLS

load_dotenv()

MAX_MODEL_CALLS = 6  # the same cap as Day 3

SYSTEM_PROMPT = (
    "You are a helpful assistant. "
    "Always use the tools to find a landmark's city and a city's weather. "
    "Never answer these from memory. "
    "Answer in plain text, without markdown."
)

model = ChatGroq(model="openai/gpt-oss-20b", temperature=0)


def on_tool_error(error, request):
    """Turn a tool error into text for the model, like Day 3."""
    return f"Error: {error}"


def build_agent(max_model_calls: int):
    """Build an agent that stops politely after max_model_calls model calls."""
    return create_agent(
        model=model,
        tools=TOOLS,
        system_prompt=SYSTEM_PROMPT,
        middleware=[
            ToolErrorMiddleware(on_tool_error),
            ModelCallLimitMiddleware(run_limit=max_model_calls, exit_behavior="end"),
        ],
    )


agent = build_agent(MAX_MODEL_CALLS)
tiny_agent = build_agent(2)  # only for the test: too small on purpose

print("AGENT TYPE:", type(agent).__name__)
print("NODES:     ", list(agent.get_graph().nodes))


def run(agent, question: str) -> None:
    print("\n" + "=" * 60)
    print("QUESTION:", question)

    result = agent.invoke({"messages": [{"role": "user", "content": question}]})

    print("\n--- every message in the result ---")
    for i, msg in enumerate(result["messages"]):
        kind = type(msg).__name__
        if getattr(msg, "tool_calls", None):
            for tc in msg.tool_calls:
                print(f"{i}. {kind:12} asks for {tc['name']}({tc['args']})")
        else:
            print(f"{i}. {kind:12} {msg.content}")

    print("\nFINAL ANSWER:", result["messages"][-1].content)


if __name__ == "__main__":
    run(agent, "What's the weather in the city where Vaultspire Tower is?")
    run(agent, "What's the weather in the city where Big Ben is?")
    print("\n\n>>> Same question, but the agent may only call the model 2 times:")
    run(tiny_agent, "What's the weather in the city where Vaultspire Tower is?")