from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from services.reranker import Reranker


class VectorStore:
    def __init__(self):
        self.client = QdrantClient(
            url="http://localhost:6333"
        )
        self.reranker = Reranker()
        self.collection_name = "documents"

        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=384,
                    distance=Distance.COSINE
                )
            )

    def store(self, embedded_chunks):
        points = []

        for index, chunk in enumerate(embedded_chunks):
            point = PointStruct(
                id=index,
                vector=chunk["embedding"],
                payload={
                    "text": chunk["text"],
                    "metadata": chunk["metadata"]
                }
            )
            points.append(point)

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def search(self, query_embedding, query=None, limit=5):

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=limit * 2 if query else limit
        )

        points = results.points

        if query and points:
            chunks = [result.payload for result in points]
            reranked = self.reranker.rerank(query, chunks, top_k=limit)
            return reranked

        return [
            {"text": result.payload["text"], "metadata": result.payload.get("metadata", {})}
            for result in points
        ]
