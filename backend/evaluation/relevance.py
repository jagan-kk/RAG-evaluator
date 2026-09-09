import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import ollama

load_dotenv()

openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

PROMPT = """
You are an evaluator for a RAG system.

Evaluate how relevant the answer is to the question.

Question:
{question}

Answer:
{answer}

Give a relevance score between 0 and 1.

Scoring:
1.0 = directly and completely answers the question
0.75 = mostly answers the question
0.5 = partially answers the question
0.25 = barely relevant
0.0 = does not answer the question at all

Return ONLY valid JSON in this format:

{{
    "score": 0.0,
    "reason": "brief explanation"
}}
"""


class Relevance:

    def evaluate(self, question: str, answer: str, provider: str = "openrouter"):

        prompt = PROMPT.format(question=question, answer=answer)

        if provider == "ollama":
            response = ollama.generate(
                model="qwen3.5:4b",
                prompt=prompt
            )
            result = json.loads(response["response"])
        else:
            response = openrouter_client.chat.completions.create(
                model="liquid/lfm-2.5-2.6b:free",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0
            )
            result = json.loads(response.choices[0].message.content)

        return result
