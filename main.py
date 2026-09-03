from ingestion.pdf import read_pdf
from chunking.chunker import chunk_docs
from embedding.embeder import Embedder

documents = read_pdf("ingestion/hunger-game.pdf")

chunks = chunk_docs(documents)
embedder= Embedder()
embed_chunk=embedder.emebed_chunks(chunks)

print(embed_chunk[0])