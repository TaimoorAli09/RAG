# """
# =========================================================
# File: retrieval_metrics.py
# =========================================================

# Purpose
# -------
# Evaluate the retrieval quality of our RAG system.

# Metrics
# -------
# 1. Precision@K
# 2. Recall@K
# 3. MRR@K

# These metrics evaluate the RETRIEVAL layer.

# They do NOT evaluate the LLM answer.

# Pipeline:

# Query
#   ↓
# BM25
#   ↓
# Semantic Search
#   ↓
# RRF
#   ↓
# Reranker
#   ↓
# Top K chunks
#   ↓
# Evaluation Metrics
# =========================================================
# """


# def precision_at_k(retrieved_pages, relevant_pages, k):
#     """
#     Precision@K

#     Measures how many of the retrieved
#     documents are actually relevant.

#     Formula:

#     relevant retrieved documents
#     -----------------------------
#               K
#     """

#     retrieved = retrieved_pages[:k]

#     if not retrieved:
#         return 0.0

#     relevant_retrieved = sum(1 for page in retrieved if page in relevant_pages)

#     return relevant_retrieved / len(retrieved)


# def recall_at_k(retrieved_pages, relevant_pages, k):
#     """
#     Recall@K

#     Measures how many of the relevant
#     documents were successfully retrieved.

#     Formula:

#     relevant retrieved
#     ------------------
#     total relevant
#     """

#     retrieved = retrieved_pages[:k]

#     if not relevant_pages:
#         return 0.0

#     relevant_retrieved = sum(1 for page in set(retrieved) if page in relevant_pages)

#     return relevant_retrieved / len(set(relevant_pages))


# def mrr_at_k(retrieved_pages, relevant_pages, k):
#     """
#     Mean Reciprocal Rank for a single query.

#     Finds the rank of the FIRST relevant result.

#     Example:

#     Retrieved:

#     [2, 8, 4, 6, 5]

#     Relevant:

#     [8]

#     Rank of 8 = 2

#     MRR = 1 / 2 = 0.5
#     """

#     retrieved = retrieved_pages[:k]

#     for rank, page in enumerate(retrieved, start=1):

#         if page in relevant_pages:

#             return 1.0 / rank

#     return 0.0


# def evaluate_query(retrieved_pages, relevant_pages, k=5):
#     """
#     Calculate all metrics for one query.
#     """

#     precision = precision_at_k(retrieved_pages, relevant_pages, k)

#     recall = recall_at_k(retrieved_pages, relevant_pages, k)

#     mrr = mrr_at_k(retrieved_pages, relevant_pages, k)

#     return {"precision@k": precision, "recall@k": recall, "mrr@k": mrr}


# def evaluate_dataset(results, k=5):
#     """
#     Calculate average metrics
#     across the complete dataset.

#     results format:

#     [
#         {
#             "retrieved_pages": [2, 8, 4, 6, 5],
#             "relevant_pages": [8]
#         }
#     ]
#     """

#     if not results:
#         return {"precision@k": 0.0, "recall@k": 0.0, "mrr@k": 0.0}

#     total_precision = 0.0
#     total_recall = 0.0
#     total_mrr = 0.0

#     for result in results:

#         metrics = evaluate_query(result["retrieved_pages"], result["relevant_pages"], k)

#         total_precision += metrics["precision@k"]

#         total_recall += metrics["recall@k"]

#         total_mrr += metrics["mrr@k"]

#     count = len(results)

#     return {
#         "precision@k": total_precision / count,
#         "recall@k": total_recall / count,
#         "mrr@k": total_mrr / count,
#     }
