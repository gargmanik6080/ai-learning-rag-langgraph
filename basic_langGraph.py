from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    question: str
    answer: str

builder = StateGraph(State)

def router(state: State):
    question = state["question"] 
    if "kubernetes" in question.lower() or "pod" in question.lower():
        return {"answer": f"Need retrieval for question: {question}"}
    return {"answer": f"Direct answer for question: {question}"}

builder.add_node("router", router)
builder.add_edge(START, "router")
builder.add_edge("router", END)

app = builder.compile()

# result = app.invoke({"question": "What is a readiness probe?"})
result = app.invoke({"question": "What is a readiness probe in Kubernetes?"})
print(result)