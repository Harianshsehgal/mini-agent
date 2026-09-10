"""Step 05 — LangChain basics.

4.1: one model call with ChatGroq, and a close look at what comes back.
"""
import inspect

from dotenv import load_dotenv
import langchain_core.messages
from langchain_groq import ChatGroq
from langchain.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv()  # finds the .env at the repo root, loads GROQ_API_KEY

# TODO 1: create the model.
# Use the same model name as Days 1–3. Pick a temperature.
MODEL = "openai/gpt-oss-20b"

model = ChatGroq(
    model=MODEL,
    temperature=0,
)

# TODO 2: build the messages.
# One system message, one human message. Any short question is fine.
messages = [
    SystemMessage("You are a helpful assistant. Answer in one sentence"),
    HumanMessage("What is the capital of France?"),
]

# TODO 3: call the model.
# Hint: every LangChain model has the same method for "run once".
reply = model.invoke(messages)

# ---------- Look at what came back ----------
print("TYPE:", type(reply).__name__)

print("\n--- .content ---")
print(reply.content)

print("\n--- .content_blocks ---")
for block in reply.content_blocks:
    print(block)

print("\n--- .usage_metadata ---")
print(reply.usage_metadata)

print("\n--- .additional_kwargs keys ---")
print(list(reply.additional_kwargs.keys()))
 
print("\n--- where does AIMessage live? ---")
print(AIMessage.__module__)                           # the module that defines it
print(inspect.getfile(AIMessage))                     # the real file on your disk
print(AIMessage is langchain_core.messages.AIMessage) # same class, two import paths?