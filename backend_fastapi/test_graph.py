from app.graph.graph import rag_graph

from app.core.database import SessionLocal


# -----------------------------------------
# Create database session
# -----------------------------------------

db = SessionLocal()


try:

    # -----------------------------------------
    # Run LangGraph
    # -----------------------------------------

    result = rag_graph.invoke(

        {
            "query": "what is local search",

            "retrieved_chunks": [],

            "reranked_chunks": [],

            "context": "",

            "answer": "",

            "sources": []
        },

        context={
            "db": db
        }
    )


    # -----------------------------------------
    # Print Results
    # -----------------------------------------

    print("\n==============================")
    print("FINAL RESULT")
    print("==============================")

    print(
        "Query:",
        result["query"]
    )


    print(
        "Retrieved:",
        len(result["retrieved_chunks"])
    )


    for chunk in result["retrieved_chunks"]:

        print(
            "\nPage:",
            chunk.page_number
        )

        print(
            "Chunk:",
            chunk.chunk_number
        )

        print(
            "Text:",
            chunk.text[:200]
        )


finally:

    db.close()