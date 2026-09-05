from services.embeder import Embedder
from services.vector_store import VectorStore
from services.llm import LLM


embedder = Embedder()
vector_store = VectorStore()
llm = LLM()


question = "who is Barnaby"

query_embedding = embedder.embed_query(question)

results = vector_store.search(
    query_embedding.tolist(),
    limit=5
)


context = "\n\n".join(
    result.payload["text"]
    for result in results
)


answer = llm.generate(
    context=context,
    question=question
)


print("\nANSWER:")
print(answer)