import os
from dotenv import load_dotenv
from openai import OpenAI
import ollama

load_dotenv()
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

PROMPT_TEMPLATE = """
Answer the question using only the context below.
IMPORTANT RULES: 
1. Do not use information that is not present in the context. 
2. Do not invent or assume information. 
3. Use Markdown formatting. 
4. Organize the answer using appropriate headings. 
5. Use bullet points for lists. 
6. If the question asks about a person, use sections such as: 
- Name 
- Contact 
- Education 
- Skills 
- Interests 
- Projects 
- Other relevant information
 7. Only include sections for which information exists in the context. 
 8. If the context does not contain the answer, say: "The provided context does not contain enough information to answer this question."

Context:
{context}

Question:
{question}

Answer:
"""


class LLM:

    def generate(self, context, question):

        prompt = PROMPT_TEMPLATE.format(context=context, question=question)

        response = client.chat.completions.create(
            model="liquid/lfm-2.5-2.6b:free",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            stream=True
        )

        answer=""
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                answer+=content
                yield content

    def generate_ollama(self, context, question):

        prompt = PROMPT_TEMPLATE.format(context=context, question=question)

        response = ollama.generate(
            model="qwen3.5:4b",
            prompt=prompt
        )

        return response["response"]