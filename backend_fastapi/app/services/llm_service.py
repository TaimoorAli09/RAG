from google import genai
from google.genai import types

from langsmith import traceable

from app.core.config import GEMINI_API_KEY, GEMINI_CHAT_MODEL


@traceable(name="generate_answer")
def generate_answer(
    question,
    context
):

    prompt = f"""
You are an intelligent document assistant.

Your job is to answer questions from the provided document context.

Rules:

1. Answer ONLY using the given context.
2. Do not use outside knowledge.
3. If the answer is not present in the context, say:
   "I could not find this information in the document."
4. Keep the answer clear and concise.
5. Mention page numbers when available.

DOCUMENT CONTEXT:

{context}

USER QUESTION:

{question}

ANSWER:
"""

    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model=GEMINI_CHAT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.1),
    )

    return response.text or "I could not generate an answer from the document context."
