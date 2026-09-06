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

        response = client.chat.completions.create(
            model="minimax/minimax-m3:free",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            stream=True
        )

        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                yield content