# """
# =========================================================
# File: metrics.py
# =========================================================

# Purpose
# -------
# Retrieval evaluation metrics.

# These metrics tell us how good our RAG retrieval system is.

# Metrics:
# 1. Precision@K
# 2. Recall@K
# 3. MRR

# Example:

# Question:
# "What is local search?"

# Relevant chunks:
# [8]

# Retrieved:
# [2, 8, 4, 6, 5]

# Precision@5 = 1/5
# Recall@5 = 1/1
# MRR = 1/2

# =========================================================
# """


# def precision_at_k(retrieved, relevant, k):
#     """
#     Precision@K

#     Out of the first K retrieved chunks,
#     how many are actually relevant?
#     """

#     retrieved_k = retrieved[:k]

#     if not retrieved_k:
#         return 0.0

#     relevant_count = sum(1 for item in retrieved_k if item in relevant)

#     return relevant_count / len(retrieved_k)


# def recall_at_k(retrieved, relevant, k):
#     """
#     Recall@K

#     Out of all relevant chunks,
#     how many did our retriever find?
#     """

#     if not relevant:
#         return 0.0

#     retrieved_k = retrieved[:k]

#     relevant_count = sum(1 for item in relevant if item in retrieved_k)

#     return relevant_count / len(relevant)


# def reciprocal_rank(retrieved, relevant):
#     """
#     Reciprocal Rank

#     Finds the position of the FIRST relevant result.

#     Example:

#     retrieved:
#     [5, 3, 8, 2]

#     relevant:
#     [8]

#     First relevant result is position 3.

#     MRR contribution = 1 / 3
#     """

#     for rank, item in enumerate(retrieved, start=1):

#         if item in relevant:

#             return 1 / rank

#     return 0.0
