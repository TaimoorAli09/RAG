from app.graph.graph import rag_graph

from app.core.database import SessionLocal

db = SessionLocal()


try:

    result = rag_graph.invoke(
        {
            "query": "what is local search",
            "retrieved_chunks": [],
            "reranked_chunks": [],
            "context": "",
            "answer": "",
            "sources": [],
        },
        context={"db": db},
    )

    print("\n")
    print("================================")
    print("FINAL ANSWER")
    print("================================")

    print(result["answer"])

    print("\n")
    print("================================")
    print("SOURCES")
    print("================================")

    for source in result["sources"]:

        print(source)


finally:

    db.close()
