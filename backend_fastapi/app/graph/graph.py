"""
=========================================================
File: graph.py
=========================================================

Complete RAG LangGraph

START
  ↓
Retrieve
  ↓
Rerank
  ↓
Context
  ↓
Generate
  ↓
Sources
  ↓
END

=========================================================
"""

from langgraph.graph import StateGraph, START, END

from app.graph.state import RAGState

from app.graph.nodes.retrieve import retrieve_node
from app.graph.nodes.rerank import rerank_node
from app.graph.nodes.context import context_node
from app.graph.nodes.generate import generate_node
from app.graph.nodes.sources import sources_node

# -----------------------------------------
# Create Graph
# -----------------------------------------

builder = StateGraph(RAGState)


# -----------------------------------------
# Add Nodes
# -----------------------------------------

builder.add_node("retrieve", retrieve_node)

builder.add_node("rerank", rerank_node)

builder.add_node("context", context_node)

builder.add_node("generate", generate_node)

builder.add_node("sources", sources_node)


# -----------------------------------------
# Edges
# -----------------------------------------

builder.add_edge(START, "retrieve")

builder.add_edge("retrieve", "rerank")

builder.add_edge("rerank", "context")

builder.add_edge("context", "generate")

builder.add_edge("generate", "sources")

builder.add_edge("sources", END)


# -----------------------------------------
# Compile
# -----------------------------------------

rag_graph = builder.compile()
