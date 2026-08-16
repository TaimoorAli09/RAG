# from pathlib import Path
# from dotenv import load_dotenv
# from langsmith import Client
# from test_dataset import EVALUATION_DATASET


# # Load .env from backend_fastapi/.env
# BASE_DIR = Path(__file__).resolve().parents[2]
# load_dotenv(BASE_DIR / ".env")


# client = Client()

# DATASET_NAME = "RAG Evaluation Dataset"


# existing_datasets = list(
#     client.list_datasets(dataset_name=DATASET_NAME)
# )

# if existing_datasets:
#     dataset = existing_datasets[0]

#     print(f"Dataset already exists: {DATASET_NAME}")
#     print(f"Dataset ID: {dataset.id}")

# else:
#     dataset = client.create_dataset(
#         dataset_name=DATASET_NAME,
#         description="Evaluation dataset for RAG retrieval and answer quality"
#     )

#     print(f"Created dataset: {DATASET_NAME}")
#     print(f"Dataset ID: {dataset.id}")


# for item in EVALUATION_DATASET:

#     query = item["query"]
#     relevant_chunks = item["relevant"]

#     client.create_example(
#         inputs={
#             "query": query
#         },
#         outputs={
#             "relevant": list(relevant_chunks)
#         },
#         dataset_id=dataset.id
#     )

#     print(f"Added: {query}")


# print("\n================================")
# print("LangSmith dataset ready!")
# print("================================")
# print(f"Dataset: {DATASET_NAME}")
# print(f"Examples: {len(EVALUATION_DATASET)}")