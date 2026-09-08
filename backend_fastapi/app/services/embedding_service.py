import os
from ollama import Client

ollama_client = Client(host=os.getenv("OLLAMA_HOST", "http://localhost:11434"))


def generate_embedding(text):

    response = ollama_client.embeddings(

        model="nomic-embed-text",

        prompt=text

    )


    return response["embedding"]
