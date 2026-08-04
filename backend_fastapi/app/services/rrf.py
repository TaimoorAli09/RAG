"""
=========================================================
Reciprocal Rank Fusion (RRF)
=========================================================

Purpose:
--------
This service combines results from multiple search methods
(e.g. Semantic Search + BM25 Search).

Why do we need it?
------------------
Semantic search may miss exact keywords.

BM25 may miss semantic meaning.

Instead of choosing one search algorithm,
we combine both rankings.

This improves retrieval quality.

Example
-------

Semantic Search

1. Page 8
2. Page 5
3. Page 2

BM25 Search

1. Page 5
2. Page 4
3. Page 8

After RRF

1. Page 5
2. Page 8
3. Page 4

This gives a much better final ranking.

Reference:
-----------
Reciprocal Rank Fusion
Cormack et al.
https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf

=========================================================
"""

from collections import defaultdict


def reciprocal_rank_fusion(*rank_lists, k=60):
    """
    Combine multiple ranked lists into one ranked list.

    Parameters
    ----------
    rank_lists
        Multiple ranked result lists.

    k
        Constant used in RRF formula.

    Returns
    -------
    List
        Final ranked results.
    """

    scores = defaultdict(float)

    items = {}

    # Iterate over every ranking list
    for rank_list in rank_lists:

        # rank starts from 0
        for rank, item in enumerate(rank_list):

            # RRF Formula
            score = 1 / (k + rank + 1)

            scores[item.id] += score

            items[item.id] = item

    # Sort by highest score
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # Return actual objects
    return [items[item_id] for item_id, score in ranked]
