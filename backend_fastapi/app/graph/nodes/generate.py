"""
=========================================================
File: generate.py
=========================================================

Generation Node

Uses the retrieved context and generates an answer
using the existing LLM service.
=========================================================
"""

from app.services.llm_service import generate_answer


def generate_node(state):

    query = state["query"]

    context = state["context"]

    print("\n==============================")
    print("GENERATE NODE")
    print("==============================")

    answer = generate_answer(query, context)

    return {"answer": answer}
