from typing import TypedDict
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition


from pathlib import Path
import os
from dotenv import load_dotenv
from openai import OpenAI
import chromadb
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

## TOOLS
@tool
def search_k8s_docs(query: str) -> str:
    """Search the Kubernetes documentation for information relevant to a query."""
    query_embedding = embedder.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3,
    )

    documents = results["documents"][0] if results["documents"] else []
    if not documents:
        return "No matching kubernetes documentation found."

    return "\n\n".join(documents)

@tool 
def calculate_available_replicas(desired: int, unavailable: int) -> str:
    """Calculate the available replica count from desired and unavailable replicas."""
    if desired < 0 or unavailable < 0:
        raise ValueError("Replica counts must be non-negative.")
    if unavailable > desired:
        raise ValueError("Unavailable replicas cannot exceed desired replicas.")

    available = desired - unavailable
    return f"{available} replicas are available."


## CLIENT SETUP
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise RuntimeError("GROQ_API_KEY is not set.")

model = ChatOpenAI(
    model="openai/gpt-oss-120b",
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1",
    temperature=0.2,
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


tools = [search_k8s_docs, calculate_available_replicas]
model_with_tools = model.bind_tools(tools)

def agent(state: MessagesState):
    response = model_with_tools.invoke(state["messages"])
    return {"messages": state["messages"] + [response]}

## 


builder = StateGraph(MessagesState)

builder.add_node("agent", agent)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "agent")

builder.add_conditional_edges(
    "agent",
    tools_condition,
    {
        "tools": "tools",
        END: END
    },
)

builder.add_edge("tools", "agent")

graph = builder.compile()

result = graph.invoke({
    "messages": [
        {
            "role": "user",
            "content": (
                "Use the Kubernetes documentation search tool to find what a "
                "readiness probe does. Also use the replica calculator for "
                "5 desired replicas and 2 unavailable replicas. Combine both results."
            ),
        }
    ]
})

for message in result["messages"]:
    print(f"\n--- {message.type} ---")
    if getattr(message, "tool_calls", None):
        print("Tool calls:", message.tool_calls)
    print(message.content)