from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END

from pathlib import Path
import os
from dotenv import load_dotenv
from openai import OpenAI
import chromadb
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter


## CLIENT SETUP
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

##################
## LANGGRAPH SETUP
class State(TypedDict):
    question: str
    route: Literal["rag", "direct"]
    context: str
    answer: str

builder = StateGraph(State)

def router(state: State):
    question = state["question"].lower()
    if "kubernetes" in question or "pod" in question:
        return {"route": "rag"}
    return {"route": "direct"}

def choose_path(state: State) -> Literal["rag", "direct"]:
    return state["route"]

def retrieve(state: State):
    embedded_question = embedder.encode(state["question"]).tolist()
    collection_results = collection.query(
        query_embeddings=embedded_question,
        n_results=5
    )

    retrieved_text = "\n\n".join(collection_results["documents"][0])
    return {"context": retrieved_text}

def generate_answer(state: State):
    context = state.get("context", "")

    prompt = f"""
    Use the following context to answer the question.
    If the answer is not in the context, answer directly.

    Context:
    {context}

    Question: {state["question"]}
    """

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system",  "content": "You are a helpful kubernetes assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2
    )
    
    answer = response.choices[0].message.content
    return {"answer": answer}


builder.add_node("router", router)
builder.add_node("retrieve", retrieve)
builder.add_node("generate_answer", generate_answer)

builder.add_edge(START, "router")
builder.add_conditional_edges(
    "router", 
    choose_path,
    {
        "rag": "retrieve",
        "direct": "generate_answer"
    },
)
builder.add_edge("retrieve", "generate_answer")
builder.add_edge("generate_answer", END)

app = builder.compile()

result = app.invoke({"question": "What is a readiness probe?"})
# result = app.invoke({"question": "What is a readiness probe in Kubernetes?"})
# print(result)
print(result["answer"])