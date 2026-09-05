import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)


class LLM:

    def generate(self, context, question):

        prompt = f"""
Answer the question using only the context below.

Context:
{context}

Question:
{question}

Answer:
"""

        response = client.chat.completions.create(
            model="minimax/minimax-m3:free",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content