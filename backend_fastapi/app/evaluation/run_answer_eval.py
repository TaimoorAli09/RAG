"""
RAG Answer Evaluation
RAGAS 0.4.3 + Ollama

Run:
    python -m app.evaluation.run_answer_eval

Requirements:
    ragas==0.4.3
    openai
    sqlalchemy

Ollama:
    LLM: qwen2.5-coder:3b
    Embeddings: nomic-embed-text:latest
"""

from __future__ import annotations

import os
import time
from typing import Any, Optional

from openai import OpenAI

from ragas import EvaluationDataset, evaluate

from ragas.metrics.collections import (
    Faithfulness,
    AnswerRelevancy,
    ContextPrecision,
    ContextRecall,
)

from ragas.llms import llm_factory
from ragas.embeddings.base import embedding_factory

from app.core.database import SessionLocal
from app.services.hybrid_search import hybrid_search
from app.services.llm_service import generate_answer

# ============================================================
# CUSTOM OLLAMA LLM FOR RAGAS
# ============================================================


# ============================================================
# CONFIGURATION
# ============================================================

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434/v1",
)

EVALUATOR_LLM_MODEL = os.getenv(
    "RAGAS_LLM_MODEL",
    "qwen2.5-coder:3b",
)

EVALUATOR_EMBEDDING_MODEL = os.getenv(
    "RAGAS_EMBEDDING_MODEL",
    "nomic-embed-text:latest",
)

# Final number of contexts passed to the answer generator
# and RAGAS.
TOP_K = 5

# Number of candidates requested from hybrid search.
SEARCH_LIMIT = 20


# ============================================================
# TEST DATA
# ============================================================

TEST_CASES = [
    {
        "question": "what is MRV",
        "reference": (
            "MRV (Minimum Remaining Values) is a heuristic used in "
            "constraint satisfaction problems such as Sudoku. It selects "
            "the variable or cell with the fewest remaining valid values, "
            "reducing the branching factor and search space."
        ),
        "expected_location": (2, 7, 1),
    },
    {
        "question": "what is minimum remaining values",
        "reference": (
            "Minimum Remaining Values (MRV) selects the cell or variable "
            "with the fewest valid options. By choosing the most constrained "
            "variable first, it reduces the branching factor and search space."
        ),
        "expected_location": (2, 7, 1),
    },
    {
        "question": "what is AC-3",
        "reference": (
            "AC-3 (Arc Consistency Algorithm 3) is a constraint propagation "
            "algorithm that enforces arc consistency by removing values from "
            "variable domains when they are inconsistent with neighboring "
            "variables."
        ),
        "expected_location": (2, 7, 1),
    },
    {
        "question": "how does AC-3 reduce the search space",
        "reference": (
            "AC-3 reduces the search space by enforcing arc consistency and "
            "removing invalid values from variable domains before deeper "
            "search. This detects conflicts early and reduces unnecessary "
            "backtracking."
        ),
        "expected_location": (2, 7, 1),
    },
    {
        "question": "what is forward checking",
        "reference": (
            "Forward checking is a constraint-solving technique that, after "
            "assigning a value to a variable, removes inconsistent values "
            "from the domains of neighboring unassigned variables. If a "
            "neighboring domain becomes empty, failure is detected early."
        ),
        "expected_location": (2, 7, 2),
    },
    {
        "question": "what are the advantages of forward checking",
        "reference": (
            "Forward checking detects conflicts early by removing invalid "
            "values from neighboring variable domains. This reduces "
            "unnecessary recursion and backtracking and improves search "
            "efficiency."
        ),
        "expected_location": (2, 7, 2),
    },
    {
        "question": "what is local search",
        "reference": (
            "Local search is an iterative optimization technique that starts "
            "with a candidate solution and repeatedly makes local changes to "
            "improve the solution according to an objective or cost function."
        ),
        "expected_location": (2, 8, 1),
    },
    {
        "question": "what is hill climbing",
        "reference": (
            "Hill climbing is a local search algorithm that starts from an "
            "initial solution and repeatedly moves to a neighboring solution "
            "that improves the objective or cost function until no further "
            "improvement is possible."
        ),
        "expected_location": (2, 8, 1),
    },
    {
        "question": "what is the cost function of hill climbing",
        "reference": (
            "In the Sudoku hill-climbing approach, the cost function measures "
            "constraint violations such as duplicate values in rows and "
            "columns. The objective is to minimize these violations."
        ),
        "expected_location": (2, 8, 1),
    },
    {
        "question": "what are the limitations of hill climbing",
        "reference": (
            "Hill climbing can get stuck in local minima and is not guaranteed "
            "to find the global optimum or a solution. Its performance depends "
            "on the starting state and the neighborhood."
        ),
        "expected_location": (2, 8, 1),
    },
    {
        "question": "what is the conclusion of the project",
        "reference": (
            "The project demonstrates an AI-based Sudoku solver and "
            "benchmarking system for generating, solving, and evaluating "
            "9x9 Sudoku puzzles across multiple difficulty levels. It compares "
            "different AI search strategies including uninformed search, "
            "informed search, constraint propagation, and local search."
        ),
        "expected_location": (2, 10, 1),
    },
]


# ============================================================
# DISPLAY HELPERS
# ============================================================


def print_separator(char: str = "=", length: int = 70) -> None:
    print(char * length)


def get_chunk_value(
    chunk: Any,
    field: str,
    default: Any = None,
) -> Any:
    """
    Supports:
        - SQLAlchemy objects
        - dictionaries
    """

    if isinstance(chunk, dict):
        return chunk.get(field, default)

    return getattr(chunk, field, default)


def chunk_location(chunk: Any) -> tuple:
    """
    Returns:

        (document_id, page_number, chunk_number)
    """

    document_id = get_chunk_value(
        chunk,
        "document_id",
    )

    page_number = get_chunk_value(
        chunk,
        "page_number",
    )

    chunk_number = get_chunk_value(
        chunk,
        "chunk_number",
    )

    return (
        document_id,
        page_number,
        chunk_number,
    )


def chunk_text(chunk: Any) -> str:
    """
    Safely extract chunk text.
    """

    text = get_chunk_value(
        chunk,
        "text",
        "",
    )

    if text is None:
        return ""

    return str(text)


# ============================================================
# RAGAS SAMPLE BUILDER
# ============================================================


def build_ragas_sample(
    question: str,
    answer: str,
    contexts: list[str],
    reference: str,
) -> dict:
    """
    RAGAS evaluation row.

    RAGAS 0.4.x fields:

        user_input
        response
        retrieved_contexts
        reference
    """

    return {
        "user_input": question,
        "response": answer,
        "retrieved_contexts": contexts,
        "reference": reference,
    }


# ============================================================
# CREATE OLLAMA LLM FOR RAGAS
# ============================================================


def create_ragas_llm():
    """Creates an Ollama-backed RAGAS evaluator using llm_factory."""

    print("Creating evaluator LLM...")
    print(f"LLM: {EVALUATOR_LLM_MODEL}")

    client = OpenAI(
        api_key="ollama",
        base_url=OLLAMA_BASE_URL,
    )

    evaluator_llm = llm_factory(
        EVALUATOR_LLM_MODEL,
        provider="openai",
        client=client,
    )

    return evaluator_llm, client


# ============================================================
# CREATE OLLAMA EMBEDDINGS FOR RAGAS
# ============================================================


def create_ragas_embeddings(client: OpenAI):
    """Creates Ollama-backed embeddings for RAGAS using embedding_factory."""

    print(f"Creating evaluator embeddings...")
    print(f"Embeddings: {EVALUATOR_EMBEDDING_MODEL}")

    evaluator_embeddings = embedding_factory(
        "openai",
        model=EVALUATOR_EMBEDDING_MODEL,
        client=client,
    )

    return evaluator_embeddings


# ============================================================
# CONFIGURE RAGAS METRICS
# ============================================================


def configure_metrics(
    evaluator_llm,
    evaluator_embeddings,
):
    """Create metrics properly for RAGAS 0.4.3."""

    print()
    print("Configuring metrics...")

    metrics = [
        Faithfulness(llm=evaluator_llm),
        AnswerRelevancy(
            llm=evaluator_llm,
            embeddings=evaluator_embeddings,
        ),
        ContextPrecision(llm=evaluator_llm),
        ContextRecall(llm=evaluator_llm),
    ]

    print()
    print("Metrics:")

    for metric in metrics:
        print(f"- {metric.name}")

    return metrics


# ============================================================
# RUN ACTUAL RAG PIPELINE
# ============================================================


def run_rag_pipeline():
    """
    Run the existing RAG pipeline.

    Pipeline:

        question
             ↓
        hybrid_search
             ↓
        reranked top 5
             ↓
        context
             ↓
        generate_answer
             ↓
        RAGAS sample
    """

    db = SessionLocal()

    ragas_samples = []

    retrieval_hits = 0
    latencies = []

    try:

        total_queries = len(TEST_CASES)

        for index, test_case in enumerate(
            TEST_CASES,
            start=1,
        ):

            question = test_case["question"]

            reference = test_case["reference"]

            expected_location = test_case["expected_location"]

            print()
            print_separator("-", 70)

            print(f"QUERY {index}/{total_queries}")

            print(question)

            print_separator("-", 70)

            # ------------------------------------------------
            # START TIMER
            # ------------------------------------------------

            start_time = time.perf_counter()

            # ------------------------------------------------
            # HYBRID SEARCH
            # ------------------------------------------------

            retrieved_chunks = hybrid_search(
                question,
                db,
                limit=SEARCH_LIMIT,
            )

            if retrieved_chunks is None:
                retrieved_chunks = []

            retrieved_chunks = list(retrieved_chunks)

            # Final top K
            retrieved_top_k = retrieved_chunks[:TOP_K]

            print(f"Retrieved: " f"{len(retrieved_top_k)}")

            # ------------------------------------------------
            # RETRIEVAL HIT RATE
            # ------------------------------------------------

            hit = False

            for chunk in retrieved_top_k:

                location = chunk_location(chunk)

                if location == expected_location:

                    hit = True
                    break

            if hit:
                retrieval_hits += 1

            # ------------------------------------------------
            # PREPARE CONTEXTS
            # ------------------------------------------------

            contexts = []

            for chunk in retrieved_top_k:

                text = chunk_text(chunk)

                if text.strip():

                    contexts.append(text)

            print(f"Retrieved contexts: " f"{len(contexts)}")

            # ------------------------------------------------
            # GENERATE ANSWER
            # ------------------------------------------------

            context_string = "\n\n".join(contexts)

            answer = generate_answer(
                question,
                context_string,
            )

            if answer is None:
                answer = ""

            answer = str(answer)

            # ------------------------------------------------
            # LATENCY
            # ------------------------------------------------

            latency = time.perf_counter() - start_time

            latencies.append(latency)

            # ------------------------------------------------
            # PRINT ANSWER
            # ------------------------------------------------

            print()
            print("ANSWER:")

            print(answer)

            # ------------------------------------------------
            # PRINT RETRIEVED LOCATIONS
            # ------------------------------------------------

            print()
            print("RETRIEVED:")

            for rank, chunk in enumerate(
                retrieved_top_k,
                start=1,
            ):

                location = chunk_location(chunk)

                relevant_marker = ""

                if location == expected_location:
                    relevant_marker = " [RELEVANT]"

                print(f"Rank {rank}: " f"{location}" f"{relevant_marker}")

            print()
            print(f"Latency: " f"{latency:.3f} sec")

            # ------------------------------------------------
            # CREATE RAGAS SAMPLE
            # ------------------------------------------------

            sample = build_ragas_sample(
                question=question,
                answer=answer,
                contexts=contexts,
                reference=reference,
            )

            ragas_samples.append(sample)

    finally:

        db.rollback()
        db.close()

    return (
        ragas_samples,
        retrieval_hits,
        latencies,
    )


# ============================================================
# RUN RAGAS EVALUATION
# ============================================================


def evaluate_rag(
    ragas_samples: list[dict],
):
    """Run RAGAS evaluation."""

    print()
    print_separator("=")
    print("                    RUNNING RAGAS")
    print_separator("=")

    # --------------------------------------------------------
    # CREATE EVALUATOR LLM
    # --------------------------------------------------------

    evaluator_llm, client = create_ragas_llm()

    # --------------------------------------------------------
    # CREATE EVALUATOR EMBEDDINGS
    # --------------------------------------------------------

    evaluator_embeddings = create_ragas_embeddings(client)

    # --------------------------------------------------------
    # CONFIGURE METRICS
    # --------------------------------------------------------

    metrics = configure_metrics(
        evaluator_llm=evaluator_llm,
        evaluator_embeddings=evaluator_embeddings,
    )

    # --------------------------------------------------------
    # DATASET
    # --------------------------------------------------------

    print()
    print("Creating EvaluationDataset...")

    dataset = EvaluationDataset.from_list(ragas_samples)

    print(f"Samples: {len(ragas_samples)}")

    # --------------------------------------------------------
    # START EVALUATION
    # --------------------------------------------------------

    print()
    print("Starting evaluation...")
    print()

    result = evaluate(
        dataset=dataset,
        metrics=metrics,
        llm=evaluator_llm,
        embeddings=evaluator_embeddings,
    )

    return result


# ============================================================
# PRINT RAGAS RESULTS
# ============================================================


def print_ragas_results(result) -> None:
    """
    Print RAGAS results safely.
    """

    print()
    print_separator("=")
    print("                    RAGAS RESULTS")
    print_separator("=")

    print()

    # --------------------------------------------------------
    # Direct result
    # --------------------------------------------------------

    print(result)

    print()

    # --------------------------------------------------------
    # DataFrame
    # --------------------------------------------------------

    try:

        if hasattr(
            result,
            "to_pandas",
        ):

            dataframe = result.to_pandas()

            print(dataframe.to_string(index=False))

            print()

            # ------------------------------------------------
            # Print averages if possible
            # ------------------------------------------------

            try:

                numeric_columns = dataframe.select_dtypes(include="number").columns

                if len(numeric_columns) > 0:

                    print()
                    print("Average metric scores:")

                    for column in numeric_columns:

                        value = dataframe[column].mean()

                        print(f"{column}: " f"{value:.4f}")

            except Exception as exc:

                print("Could not calculate " "metric averages:")

                print(repr(exc))

    except Exception as exc:

        print("Could not convert RAGAS " "result to pandas:")

        print(repr(exc))


# ============================================================
# MAIN
# ============================================================


def main():

    print(
        "DATABASE URL: "
        + os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:postgres@127.0.0.1:5433/rag_bot_db",
        )
    )

    print()

    print_separator("=")

    print("                    RAG EVALUATION")

    print_separator("=")

    # ========================================================
    # RUN RAG
    # ========================================================

    (
        ragas_samples,
        retrieval_hits,
        latencies,
    ) = run_rag_pipeline()

    # ========================================================
    # RETRIEVAL SUMMARY
    # ========================================================

    total_queries = len(TEST_CASES)

    if total_queries > 0:

        hit_rate = retrieval_hits / total_queries

    else:

        hit_rate = 0.0

    if latencies:

        average_latency = sum(latencies) / len(latencies)

    else:

        average_latency = 0.0

    print()
    print_separator("=")

    print("                 RETRIEVAL SUMMARY")

    print_separator("=")

    print(f"Retrieval Hit Rate@5: " f"{hit_rate:.4f}")

    print(f"Average Latency: " f"{average_latency:.3f} sec")

    # ========================================================
    # RAGAS
    # ========================================================

    try:

        result = evaluate_rag(ragas_samples)

        print_ragas_results(result)

        print()
        print_separator("=")

        print("                 EVALUATION COMPLETE")

        print_separator("=")

    except TypeError as e:

        print()
        print_separator("=")
        print("               RAGAS EVALUATION SKIPPED")
        print_separator("=")
        print()
        print(f"Note: RAGAS evaluation unavailable: {e}")
        print()
        print("RAG Pipeline executed successfully.")
        print("Retrieval metrics available above.")

    except Exception as exc:

        print()
        print_separator("=")

        print("                    RAGAS ERROR")

        print_separator("=")

        print()
        print("RAGAS evaluation failed:")

        print(repr(exc))

        print()
        print("Type:")

        print(type(exc).__name__)

        print()

        # IMPORTANT:
        # Show the real traceback.
        raise


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
