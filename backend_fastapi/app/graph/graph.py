"""
=========================================================
File: graph.py
=========================================================

LangGraph RAG Pipeline

START
  ↓
Retrieve
  ↓
END

Retrieve uses the existing hybrid search system:

BM25
+
Semantic Search
+
RRF
+
Reranker
=========================================================
"""

from langgraph.graph import StateGraph, START, END

from app.graph.state import RAGState

from app.graph.nodes.retrieve import retrieve_node


# -----------------------------------------
# Create Graph
# -----------------------------------------

builder = StateGraph(RAGState)


# -----------------------------------------
# Add Nodes
# -----------------------------------------

builder.add_node(
    "retrieve",
    retrieve_node
)


# -----------------------------------------
# Add Edges
# -----------------------------------------

builder.add_edge(
    START,
    "retrieve"
)

builder.add_edge(
    "retrieve",
    END
)


# -----------------------------------------
# Compile
# -----------------------------------------

rag_graph = builder.compile()