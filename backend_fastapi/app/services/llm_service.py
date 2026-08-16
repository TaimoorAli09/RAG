import ollama

from langsmith import traceable


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

    response = ollama.chat(
        model="qwen2.5:0.5b",

        options={
            "temperature": 0.1
        },

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]