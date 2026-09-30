from pathlib import Path
import os
from dotenv import load_dotenv
from openai import OpenAI
import chromadb

load_dotenv()

api_key = os.getenv("OMNIROUTE_API_KEY")

client = OpenAI(
    api_key=api_key or "local-dev",
    base_url="http://127.0.0.1:20128/v1",
)


texts = []
for path in Path("data/docs").glob("*.md"):
    texts.append({"id": path.stem, "text": path.read_text()})

chunks = [item["text"] for item in texts]

client_db = chromadb.Client()
collection = client_db.create_collection(name="k8s_docs")

question = "What does a readiness probe do in Kubernetes?"  # should get a proper answer
# question = "What is a security context in a Pod?"   # shoud get I dont know

retrieved_text = """A readiness probe tells Kubernetes whether a container
 is ready to receive traffic. When the readiness probe fails, Kubernetes 
 removes the pod from service endpoints even if the container is still running."""

prompt = f"""
Use the following context to answer the question.
If the answer is not in the context, say you do not know.

Context:
{retrieved_text}

Question: {question}
"""

response = client.chat.completions.create(
    model="gc/grok-4.6",
    messages=[
        {"role": "system",  "content": "You are a helpful kubernetes assistant."},
        {"role": "user", "content": prompt},
    ],
    temperature=0.2
)

print(response.choices[0].message.content) 