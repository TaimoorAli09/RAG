from google import genai
from google.genai import types

from app.core.config import GEMINI_API_KEY, GEMINI_EMBEDDING_MODEL


EMBEDDING_DIMENSIONS = 768


def generate_embedding(text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> list[float]:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.embed_content(
        model=GEMINI_EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(
            task_type=task_type,
            output_dimensionality=EMBEDDING_DIMENSIONS,
        ),
    )
    return response.embeddings[0].values
