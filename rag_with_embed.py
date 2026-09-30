from pathlib import Path
import os
from dotenv import load_dotenv
from openai import OpenAI
import chromadb
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter


load_dotenv()

api_key = os.getenv("OMNIROUTE_API_KEY")

client = OpenAI(
    api_key=api_key or "local-dev",
    base_url="http://127.0.0.1:20128/v1",
)


## Chunking
embedder = SentenceTransformer('all-MiniLM-L6-v2')
splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50,
    length_function=lambda text: len(
        embedder.tokenizer.encode(text, add_special_tokens=False)
    ),
    separators=["\n\n", "\n", ". ", " ", ""]
)

chunks = []
for path in sorted(Path("data/docs").glob("*.md")):
    text = path.read_text(encoding="utf-8")
    for index, chunk in enumerate(splitter.split_text(text)):
        chunks.append({
            "id": f"{path.stem}-{index}",
            "text": chunk,
            "source": path.name
        })


## EMBEDDING
client_db = chromadb.Client()
collection = client_db.create_collection(name="k8s_docs")

vectors = embedder.encode(chunks)
collection.add(
    documents=chunks,
    embeddings=vectors.tolist(),
    ids=[item["id"] for item in texts]
)

question = "What does a readiness probe do in Kubernetes?"  # should get a proper answer
# question = "What is a security context in a Pod?"   # shoud get I dont know
embedded_question = embedder.encode([question]).tolist()
collection_results = collection.query(
    query_embeddings=embedded_question,
    n_results=5
)

retrieved_text = " ".join([item["document"] for item in collection_results["documents"][0]])

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