from fastapi import APIRouter
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
def chat(request:ChatRequest):

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

    return StreamingResponse(
        llm.generate(
        context=context,
        question=request.question
        ),
        media_type="text/plain"
    )

    