from fastapi import APIRouter, Query
from services.embeder import Embedder
from services.vector_store import VectorStore
from services.llm import LLM
from schemas.chat import ChatRequest
from fastapi.responses import StreamingResponse

router =APIRouter(
    prefix="/chat",
    tags=["chat"]
)

embedder =Embedder()
vector_store=VectorStore()
llm=LLM()

@router.post("/")
def chat(request:ChatRequest, provider: str = Query(default="openrouter")):

    query_embedding = embedder.embed_query(request.question)
    results = vector_store.search(
        query_embedding.tolist(),
        query=request.question,
        limit=5
    )

    context="\n\n".join(
        result["text"] if isinstance(result, dict) else result.payload["text"]
        for result in results
    )

    if provider == "ollama":
        def generate():
            yield llm.generate_ollama(context=context, question=request.question)
        return StreamingResponse(generate(), media_type="text/plain")
    else:
        return StreamingResponse(
            llm.generate(
                context=context,
                question=request.question
            ),
            media_type="text/plain"
        )

    