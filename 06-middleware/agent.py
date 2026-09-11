"""Step 06: middleware. Log every tool call with its latency."""

import os
import time
from collections.abc import Callable

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain.messages import ToolMessage
from langchain.tools import tool
from langchain.tools.tool_node import ToolCallRequest
from langchain_openai import ChatOpenAI
from langgraph.types import Command

load_dotenv()

# Same model as before: Groq, through the OpenAI-compatible endpoint.
model = ChatOpenAI(
    model="openai/gpt-oss-20b",
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ["GROQ_API_KEY"],
)


# ---------- tools (fake data, like Day 3) ----------

@tool
def get_landmark_city(landmark: str) -> str:
    """Return the city where a landmark is."""
    cities = {"taj mahal": "Agra", "eiffel tower": "Paris"}
    return cities.get(landmark.lower(), "unknown")


@tool
def get_weather(city: str) -> str:
    """Return the current weather for a city."""
    time.sleep(0.5)  # pretend this is a slow API
    return f"It is 31°C and sunny in {city}."


# ---------- middleware: the new part today ----------

@wrap_tool_call
def log_tool_latency(
    request: ToolCallRequest,
    handler: Callable[[ToolCallRequest], ToolMessage | Command],
) -> ToolMessage | Command:
    name = request.tool_call["name"]
    args = request.tool_call["args"]
    start = time.perf_counter()        # 1. before the tool
    try:
        return handler(request)        # 2. run the real tool
    finally:                           # 3. after the tool (even if it fails)
        ms = (time.perf_counter() - start) * 1000
        print(f"[tool] {name} {args} -> {ms:.0f} ms")


agent = create_agent(
    model=model,
    tools=[get_landmark_city, get_weather],
    system_prompt="Always use the tools to find facts. Never answer from memory.",
    middleware=[log_tool_latency],
)

if __name__ == "__main__":
    question = "What's the weather in the city where the Taj Mahal is?"
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    print("\nAnswer:", result["messages"][-1].content)