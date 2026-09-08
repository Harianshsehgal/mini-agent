import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)

stream = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[{"role": "user", "content": "Say hi"}],
    reasoning_effort="low",
    stream=True,
    stream_options={"include_usage": True},
)

for i, chunk in enumerate(stream):
    print(f"--- BOX {i} ---")
    print(chunk)