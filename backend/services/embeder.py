from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(self,model_name:str="all-MiniLM-L6-v2"):
        self.model=SentenceTransformer(model_name)

    def emebed_chunks(self,chunks:list[dict])->list[dict]:
        texts=[chunk["text"] for chunk in chunks]

        embeddings=self.model.encode(
            texts,
            batch_size=32,
            normalize_embeddings=True,
            show_progress_bar=True
        )

        result=[]

        for chunk,embedding in zip(chunks,embeddings):

            result.append({
                "text":chunk["text"],
                "metadata":chunk["metadata"],
                "embedding":embedding.tolist()
            })
        return result

    def embed_query(self, query):
        return self.model.encode(
            query,
            normalize_embeddings=True
        )