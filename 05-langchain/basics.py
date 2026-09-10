"""Step 05 — LangChain basics.

4.1: one model call with ChatGroq, and a close look at what comes back.
4.3: prompt templates and the | pipe.
"""
import inspect

from dotenv import load_dotenv
import langchain_core.messages
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_groq import ChatGroq
from langchain.messages import SystemMessage, HumanMessage, AIMessage

from tools import TOOLS

load_dotenv()  # finds the .env at the repo root, loads GROQ_API_KEY


# ==================== 4.1: one model call ====================
MODEL = "openai/gpt-oss-20b"

model = ChatGroq(
    model=MODEL,
    temperature=0,
)

messages = [
    SystemMessage("You are a helpful assistant. Answer in one sentence"),
    HumanMessage("What is the capital of France?"),
]

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

# ---------- class checks ----------
print("\n--- class checks ---")
print(isinstance(reply, AIMessage))          # is reply an AIMessage?
print(isinstance(messages[1], HumanMessage))
print(type(reply).__mro__)                   # the class "family tree"

# ---------- where does AIMessage live? ----------
print("\n--- where does AIMessage live? ---")
print(AIMessage.__module__)                            # the module that defines it
print(inspect.getfile(AIMessage))                      # the real file on your disk
print(AIMessage is langchain_core.messages.AIMessage)  # same class, two import paths?


# ==================== 4.3: prompt templates and the | pipe ====================
print("\n\n=========== 4.3 ===========")

# ---------- A: a prompt template (message with blanks) ----------
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Answer in {style}."),
    ("human", "{question}"),
])
print("BLANKS:", prompt.input_variables)

# Fill the blanks. One key for each blank; names must match exactly.
filled = prompt.invoke({
    "style": "one sentence",
    "question": "What is the capital of Japan?",
})

print("TYPE:", type(filled).__name__)
for m in filled.to_messages():
    print(" ", type(m).__name__, "->", m.content)

# ---------- B: the pipe ----------
# Three steps in a line: prompt -> model -> parser
chain = prompt | model | StrOutputParser()

print("\nCHAIN TYPE:", type(chain).__name__)
print("STEPS:", [type(s).__name__ for s in chain.steps])

answer = chain.invoke({"style": "three words", "question": "Why is the sky blue?"})
print("ANSWER:", answer)
print("IS IT A STRING?", isinstance(answer, str))

# ---------- C: why does invoke work on everything? ----------
print()
for obj in [prompt, model, StrOutputParser(), chain, TOOLS[0]]:
    print(f"{type(obj).__name__:20} is a Runnable: {isinstance(obj, Runnable)}")