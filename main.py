from ingestion.pdf import read_pdf
from chunking.chunker import chunk_docs
from embedding.embeder import Embedder
from storage.vector_store import VectorStore


documents = read_pdf("ingestion/hunger-game.pdf")

chunks = chunk_docs(documents)
embedder= Embedder()
embed_chunk=embedder.emebed_chunks(chunks)
vector_store=VectorStore()
vector_store.store(embed_chunk)



