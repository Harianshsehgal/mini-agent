"""Step 05 — one round trip with bind_tools.

4.2: the same job as 03-tool-calling, done with LangChain.
Ask → model requests a tool → we run it → send the result back → final answer.
"""
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.messages import HumanMessage, ToolMessage

from tools import TOOLS

load_dotenv()

model = ChatGroq(model="openai/gpt-oss-20b", temperature=0)

# TODO 1: give the tools to the model.
model_with_tools = model.bind_tools(TOOLS)

messages = [HumanMessage("What is the weather in Agra?")]

# ---------- Step 1: ask the model ----------
ai_msg = model_with_tools.invoke(messages)

print("--- ai_msg.content ---")
print(repr(ai_msg.content))
print("\n--- ai_msg.tool_calls ---")
for call in ai_msg.tool_calls:
    print(call)
    print("  type of args:", type(call["args"]).__name__)

messages.append(ai_msg)

# ---------- Step 2: run each tool the model asked for ----------
tools_by_name = {t.name: t for t in TOOLS}

for call in ai_msg.tool_calls:
    chosen_tool = tools_by_name[call["name"]]

    # TODO 2: run the tool with the arguments the model gave.
    result = chosen_tool.invoke(call["args"])

    # TODO 3: wrap the result in a ToolMessage and add it to messages.
    messages.append(ToolMessage(content=result, tool_call_id=call["id"]))

# ---------- Step 3: ask the model again, now with the tool result ----------
final = model_with_tools.invoke(messages)

print("\n--- final answer ---")
print(final.content)