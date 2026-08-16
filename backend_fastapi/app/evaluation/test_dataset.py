EVALUATION_DATASET = [
    {
        "query": "what is MRV",
        "relevant": {(2, 7, 1)},
        "reference": (
            "MRV, or Minimum Remaining Values, selects the cell "
            "with the fewest valid options. It reduces the branching "
            "factor by solving the hardest variables first."
        ),
    },
    {
        "query": "what is minimum remaining values",
        "relevant": {(2, 7, 1)},
        "reference": (
            "MRV, or Minimum Remaining Values, selects the cell "
            "with the fewest valid options. It reduces the branching "
            "factor by solving the hardest variables first."
        ),
    },
    {
        "query": "what is AC-3",
        "relevant": {(2, 7, 1)},
        "reference": (
            "AC-3, or Arc Consistency, enforces constraint consistency "
            "between variables by removing invalid domain values early."
        ),
    },
    {
        "query": "how does AC-3 reduce the search space",
        "relevant": {(2, 7, 1)},
        "reference": (
            "AC-3 reduces the search space by removing invalid domain "
            "values early through constraint propagation."
        ),
    },
    {
        "query": "what is forward checking",
        "relevant": {(2, 7, 2)},
        "reference": (
            "Forward checking reduces the search space by checking "
            "the remaining variables after assigning a value."
        ),
    },
    {
        "query": "what are the advantages of forward checking",
        "relevant": {(2, 7, 2)},
        "reference": (
            "Forward checking detects conflicts early and reduces "
            "the number of unnecessary search operations."
        ),
    },
    {
        "query": "what is local search",
        "relevant": {(2, 8, 1)},
        "reference": (
            "Local search starts with a complete solution and "
            "iteratively improves it."
        ),
    },
    {
        "query": "what is hill climbing",
        "relevant": {(2, 8, 1)},
        "reference": (
            "Hill climbing starts with a complete solution and "
            "iteratively makes improving moves to reduce conflicts."
        ),
    },
    {
        "query": "what is the cost function of hill climbing",
        "relevant": {(2, 8, 1)},
        "reference": (
            "The hill climbing cost function measures the number "
            "of constraint violations in the Sudoku board."
        ),
    },
    {
        "query": "what are the limitations of hill climbing",
        "relevant": {(2, 8, 1)},
        "reference": (
            "Hill climbing can get stuck in local optima and may "
            "fail to find a solution even when one exists."
        ),
    },
    {
        "query": "what is the conclusion of the project",
        "relevant": {(2, 10, 1)},
        "reference": (
            "The project concludes by comparing different Sudoku "
            "solving techniques and their performance."
        ),
    },
]
