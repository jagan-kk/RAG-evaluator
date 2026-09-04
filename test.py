import os
import ollama
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError
from embedding.embeder import Embedder
from storage.vector_store import VectorStore

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
embedder = Embedder()
vector_store = VectorStore()

OLLAMA_MODEL = "qwen3.5:4b"  # Local fallback model name


def retriever(query: str) -> str:
    """Retrieves relevant background context from the vector database for a given query."""
    query_embedding = embedder.embed_query(query)
    results = vector_store.search(query_embedding.tolist(), limit=5)
    context = "\n\n".join(result.payload["text"] for result in results)
    return context


TOOL_MAP = {"retriever": retriever}


def run_ollama_fallback(query: str):
    """Fallback handler using local Ollama model when Gemini quota is exceeded."""
    print("\n[Fallback] Falling back to local Ollama (qwen3.5:4b)...")

    # 1. Manually run the retrieval step locally
    print("[Fallback Execution] Running 'retriever' locally...")
    context = retriever(query)

    # 2. Query Ollama with the retrieved context
    prompt = f"""You are a helpful AI Assistant.
Answer the user query based on the retrieved context below.

Context:
{context}

User Query: {query}
"""

    response = ollama.generate(model=OLLAMA_MODEL, prompt=prompt)
    print(f"\nAgent (Ollama Fallback): {response['response']}")


def run_agent(chat_session, query: str):
    try:
        # Initial call to Gemini
        response = chat_session.send_message(query)

        # Loop through function calls required by Gemini
        while response.function_calls:
            function_responses = []

            for call in response.function_calls:
                tool_name = call.name
                args = call.args

                print(
                    f"\n[Agent tool execution] Running '{tool_name}' with arguments: {args}"
                )

                if tool_name in TOOL_MAP:
                    tool_result = TOOL_MAP[tool_name](**args)
                else:
                    tool_result = f"Error: Tool '{tool_name}' not found."

                function_responses.append(
                    types.Part.from_function_response(
                        name=tool_name, response={"result": tool_result}
                    )
                )

            # Send tool execution results back to Gemini
            response = chat_session.send_message(function_responses)

        print(f"\nAgent: {response.text}")

    except APIError as e:
        # Catch 429 Quota or API errors and use Ollama fallback
        print(f"\n[Warning] Gemini API Error occurred: {e}")
        run_ollama_fallback(query)
    except Exception as e:
        print(f"\n[Warning] Unexpected error: {e}")
        run_ollama_fallback(query)


if __name__ == "__main__":
    chat = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction="""You are a helpful AI Assistant.
            Your duty is to retrieve the results using the tool "retriever" to the Query and 
            understand and give answer to the user""",
            tools=[retriever],
            temperature=0.2,
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(
                    mode="ANY",
                    allowed_function_names=["retriever"],
                )
            ),
        ),
    )
    query = input("Enter your Doubt: ")
    run_agent(chat, query)