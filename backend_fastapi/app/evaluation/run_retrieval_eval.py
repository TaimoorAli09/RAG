# """
# File: run_retrieval_eval.py

# Purpose:
# Run retrieval evaluation on the complete RAG pipeline.

# Pipeline:

# Query
#   ↓
# BM25
#   +
# Semantic Search
#   ↓
# RRF
#   ↓
# Reranker
#   ↓
# Top K
#   ↓
# Precision@K
# Recall@K
# MRR
# """

# from app.core.database import SessionLocal

# from app.services.hybrid_search import hybrid_search

# from app.evaluation.metrics import precision_at_k, recall_at_k, reciprocal_rank

# from app.evaluation.test_dataset import EVALUATION_DATASET


# def chunk_identifier(chunk):
#     """
#     Unique identifier for a chunk.
#     """

#     return (chunk.document_id, chunk.page_number, chunk.chunk_number)


# def evaluate():

#     db = SessionLocal()

#     k = 5

#     total_precision = 0.0
#     total_recall = 0.0
#     total_mrr = 0.0

#     successful_queries = 0
#     failed_queries = 0

#     failed = []

#     print("\n")
#     print("=" * 70)
#     print("RAG RETRIEVAL EVALUATION")
#     print("=" * 70)

#     try:

#         for index, item in enumerate(EVALUATION_DATASET, start=1):

#             query = item["query"]

#             relevant = set(item["relevant"])

#             print("\n")
#             print("-" * 70)
#             print(f"Query {index}/{len(EVALUATION_DATASET)}")
#             print(f"Query: {query}")
#             print("-" * 70)

#             try:

#                 # -----------------------------------------
#                 # COMPLETE RETRIEVAL PIPELINE
#                 # -----------------------------------------

#                 results = hybrid_search(query, db, limit=k)

#                 retrieved = [chunk_identifier(chunk) for chunk in results]

#                 print("\nRetrieved:")

#                 for rank, chunk_id in enumerate(retrieved, start=1):

#                     marker = "✓ RELEVANT" if chunk_id in relevant else ""

#                     print(f"  Rank {rank}: {chunk_id} {marker}")

#                 print("\nRelevant:")

#                 for chunk_id in relevant:
#                     print(f"  {chunk_id}")

#                 # -----------------------------------------
#                 # METRICS
#                 # -----------------------------------------

#                 precision = precision_at_k(retrieved, relevant, k)

#                 recall = recall_at_k(retrieved, relevant, k)

#                 mrr = reciprocal_rank(retrieved, relevant)

#                 print("\nMetrics:")

#                 print(f"  Precision@{k}: " f"{precision * 100:.2f}%")

#                 print(f"  Recall@{k}: " f"{recall * 100:.2f}%")

#                 print(f"  MRR: " f"{mrr * 100:.2f}%")

#                 # -----------------------------------------
#                 # ADD TO TOTALS
#                 # -----------------------------------------

#                 total_precision += precision
#                 total_recall += recall
#                 total_mrr += mrr

#                 successful_queries += 1

#             except Exception as e:

#                 failed_queries += 1

#                 failed.append({"query": query, "error": repr(e)})

#                 print("\n❌ QUERY FAILED")
#                 print(f"Error: {repr(e)}")

#                 # Continue with next query
#                 continue

#         # =================================================
#         # FINAL RESULTS
#         # =================================================

#         print("\n\n")
#         print("=" * 70)
#         print("FINAL RESULTS")
#         print("=" * 70)

#         print(f"Total queries     : {len(EVALUATION_DATASET)}")

#         print(f"Successful queries: {successful_queries}")

#         print(f"Failed queries    : {failed_queries}")

#         if successful_queries > 0:

#             avg_precision = total_precision / successful_queries

#             avg_recall = total_recall / successful_queries

#             avg_mrr = total_mrr / successful_queries

#             print("\nRetrieval Metrics")
#             print("-" * 40)

#             print(f"Precision@{k}: " f"{avg_precision * 100:.2f}%")

#             print(f"Recall@{k}: " f"{avg_recall * 100:.2f}%")

#             print(f"MRR: " f"{avg_mrr * 100:.2f}%")

#         else:

#             print("\nNo queries completed successfully.")

#         # =================================================
#         # FAILED QUERIES
#         # =================================================

#         if failed:

#             print("\n")
#             print("=" * 70)
#             print("FAILED QUERIES")
#             print("=" * 70)

#             for item in failed:

#                 print("\nQuery:")
#                 print(item["query"])

#                 print("Error:")
#                 print(item["error"])

#         print("\n")
#         print("=" * 70)
#         print("EVALUATION COMPLETE")
#         print("=" * 70)

#     finally:

#         db.close()


# if __name__ == "__main__":
#     evaluate()
