"""Step 05 — LangChain basics.

4.1: one model call with ChatGroq, and a close look at what comes back.
4.3: prompt templates and the | pipe.
"""
import inspect

from dotenv import load_dotenv
import langchain_core.messages
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import time
from langchain_core.runnables import Runnable, RunnableLambda, RunnableParallel, RunnablePassthrough
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
    
# ==================== 4.3b: more LCEL pieces ====================
print("\n\n=========== 4.3b ===========")

# ---------- A: a normal Python function as a step (RunnableLambda) ----------
def add_word_count(text: str) -> dict:
    """A normal Python function. It knows nothing about LangChain."""
    return {"answer": text, "words": len(text.split())}

# I pipe a plain function. LangChain wraps it for me.
counted_chain = chain | add_word_count

print("LAST STEP TYPE:", type(counted_chain.steps[-1]).__name__)
result = counted_chain.invoke({"style": "one sentence", "question": "What is the largest planet?"})
print("RESULT:", result)
print("RESULT TYPE:", type(result).__name__)

# ---------- B: two chains on the same input, at the same time (RunnableParallel) ----------
one_word_prompt = ChatPromptTemplate.from_messages([
    ("human", "Answer in exactly one word: {question}"),
])
one_sentence_prompt = ChatPromptTemplate.from_messages([
    ("human", "Answer in one sentence: {question}"),
])
parser = StrOutputParser()

one_word_chain = one_word_prompt | model | parser
one_sentence_chain = one_sentence_prompt | model | parser

both = RunnableParallel(one_word=one_word_chain, one_sentence=one_sentence_chain)

question = {"question": "What is the largest planet?"}

start = time.perf_counter()
result = both.invoke(question)
parallel_time = time.perf_counter() - start

print("\nPARALLEL RESULT:", result)
print("PARALLEL RESULT TYPE:", type(result).__name__)

# The same two chains, one after the other, to compare the time
start = time.perf_counter()
one_word_chain.invoke(question)
one_sentence_chain.invoke(question)
sequential_time = time.perf_counter() - start

print(f"TIME parallel:        {parallel_time:.2f} s")
print(f"TIME one after other: {sequential_time:.2f} s")

# ---------- C: a mini RAG chain with a fake retriever (RunnablePassthrough) ----------
def fake_retriever(question: str) -> str:
    """Stands in for a real retriever. A real one would search documents
    using the question. This one always returns the same text."""
    return "Vaultspire Tower is a 300-metre glass tower in Kochi. It was finished in 2031."

rag_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "Answer using ONLY the context below. "
     "If the context does not have the answer, say 'I don't know'.\n\n"
     "Context: {context}"),
    ("human", "{question}"),
])

rag_chain = (
    {"context": fake_retriever, "question": RunnablePassthrough()}
    | rag_prompt
    | model
    | StrOutputParser()
)

print("\nFIRST STEP TYPE:", type(rag_chain.steps[0]).__name__)

user_question = "How tall is Vaultspire Tower?"

# Look inside: run ONLY the first step, to see what the prompt will receive
print("FIRST STEP OUTPUT:", rag_chain.steps[0].invoke(user_question))

print("RAG ANSWER:", rag_chain.invoke(user_question))