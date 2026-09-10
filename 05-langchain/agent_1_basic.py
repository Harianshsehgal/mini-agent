"""Step 05 — agent stage 1: create_agent with no error handling.

4.4.1–4.4.2: the same job as 04-react-agent/agent.py.
Crashes on the Big Ben question: by default, a tool error stops the run.
"""
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_groq import ChatGroq

from tools import TOOLS

load_dotenv()

SYSTEM_PROMPT = (
    "You are a helpful assistant. "
    "Always use the tools to find a landmark's city and a city's weather. "
    "Never answer these from memory. "
    "Answer in plain text, without markdown."
)

model = ChatGroq(model="openai/gpt-oss-20b", temperature=0)

agent = create_agent(model=model, tools=TOOLS, system_prompt=SYSTEM_PROMPT)

print("AGENT TYPE:", type(agent).__name__)
print("NODES:     ", list(agent.get_graph().nodes))


def run(question: str) -> None:
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
    run("What's the weather in the city where Vaultspire Tower is?")