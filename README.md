# AI Learning: RAG + LangGraph

A beginner-friendly learning repo for building a small Retrieval-Augmented Generation (RAG) workflow and a simple LangGraph-based agent using Python and Kubernetes-oriented example docs.

## Purpose

This repository is for:
- learning the fundamentals of AI application development
- understanding RAG, embeddings, retrieval, and prompting
- learning LangGraph basics and agent loops
- building a small local prototype with practical examples

## Project focus

The repository includes:
- a simple LLM call example
- a small Kubernetes knowledge corpus in `data/docs/`
- a basic RAG pattern
- learning notes and reference material

## Repository structure

```text
.
├── README.md
├── LICENSE
├── basic_llm.py
├── basic_rag.py
├── .env
├── .gitignore
├── data/
│   └── docs/
│       ├── kubernetes_deployments.md
│       ├── readiness_probe.md
│       └── pod_lifecycle.md
├── ai_7day_curriculum.md
├── ai_learning_detailed_reference.md
├── ai_7day_curriculum.pdf
├── ai_learning_detailed_reference.pdf
└── .venv/
```

## Learning flow

1. Start with `basic_llm.py` to understand how to call an LLM.
2. Use the docs in `data/docs/` as your retrieval corpus.
3. Build the RAG pattern in `basic_rag.py`.
4. Extend toward a LangGraph workflow and tools-based agent.

## Setup

Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install openai python-dotenv chromadb langgraph
```

Then add your environment variables in `.env`:

```env
OMNIROUTE_API_KEY=your_key_here
```

## Example usage

```bash
source .venv/bin/activate
python basic_llm.py
python basic_rag.py
```

## License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0).

You may use, copy, and modify this project for learning, personal use, and non-commercial purposes only.

Commercial use, monetization, and business use are not permitted without prior written permission.

See [LICENSE](LICENSE) for details.

## Important note

This repo is meant for learning and experimentation, not for commercial exploitation or monetized business use.
