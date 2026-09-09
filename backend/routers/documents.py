from fastapi import APIRouter,UploadFile,File
from pathlib import Path
from services.ingestion import PDFloader
from services.chunker import Chunker
from services.embeder import Embedder
from services.vector_store import VectorStore

router=APIRouter(
    prefix='/documents',
    tags=["Documents"]
)

loader=PDFloader()
chunking=Chunker()
embeder=Embedder()
dbstorage=VectorStore()

UPLOAD_DIR=Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/uploads")
async def uploads(file:UploadFile=File(...)):

    file_path=UPLOAD_DIR/file.filename
    with open(file_path,"wb") as f:
        f.write(await file.read())

    documents=loader.read_pdf(file_path)
    chunked_doc=chunking.chunk_docs(documents)
    embeded=embeder.embed_chunks(chunked_doc)
    new_chunks=dbstorage.store(embeded)

    return {
        "file_name":file.filename,
        "content_type":file.content_type,
        "pages": len(documents),
        "chunks": len(chunked_doc),
        "embeddings":len(embeded),
        "new_chunks": new_chunks
    }
