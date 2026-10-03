from pathlib import Path
import os
from dotenv import load_dotenv
from openai import OpenAI
import chromadb
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter


load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise RuntimeError("No API key found. Check [.env](.env) for GROQ_API_KEY")


client = OpenAI(
    api_key=api_key or "local-dev",
    base_url="https://api.groq.com/openai/v1",
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

chunk_texts = []
chunk_ids = []

for path in sorted(Path("data/docs").glob("*.md")):
    text = path.read_text(encoding="utf-8")
    for index, chunk in enumerate(splitter.split_text(text)):
        chunk_texts.append(chunk)
        chunk_ids.append(f"{path.stem}-{index}")

## EMBEDDING
client_db = chromadb.Client()
collection = client_db.get_or_create_collection(name="k8s_docs")

vectors = embedder.encode(chunk_texts)

collection.add(
    documents=chunk_texts,
    embeddings=vectors.tolist(),
    ids=chunk_ids
)

question = "What does a readiness probe do in Kubernetes?"  # should get a proper answer
# question = "What is a security context in a Pod?"   # shoud get I dont know
embedded_question = embedder.encode([question]).tolist()
collection_results = collection.query(
    query_embeddings=embedded_question,
    n_results=5
)

retrieved_text = "\n\n".join(collection_results["documents"][0])

prompt = f"""
Use the following context to answer the question.
If the answer is not in the context, say you do not know.

Context:
{retrieved_text}

Question: {question}
"""

response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {"role": "system",  "content": "You are a helpful kubernetes assistant."},
        {"role": "user", "content": prompt},
    ],
    temperature=0.2
)

print(response.choices[0].message.content) 