import uuid
import hashlib
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
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

    def _hash_text(self, text):
        return hashlib.md5(text.strip().encode()).hexdigest()

    def _get_existing_hashes(self):
        try:
            results = self.client.query_points(
                collection_name=self.collection_name,
                query=[0] * 384,
                limit=10000,
                query_filter=None
            )
            hashes = set()
            for point in results.points:
                if point.payload and "text" in point.payload:
                    hashes.add(self._hash_text(point.payload["text"]))
            return hashes
        except Exception:
            return set()

    def store(self, embedded_chunks):
        existing_hashes = self._get_existing_hashes()
        points = []

        for chunk in embedded_chunks:
            chunk_hash = self._hash_text(chunk["text"])
            if chunk_hash in existing_hashes:
                continue

            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=chunk["embedding"],
                payload={
                    "text": chunk["text"],
                    "metadata": chunk["metadata"],
                    "hash": chunk_hash
                }
            )
            points.append(point)
            existing_hashes.add(chunk_hash)

        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

        return len(points)

    def search(self, query_embedding, query=None, limit=5):

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=30
        )

        points = results.points

        if query and points:
            chunks = [result.payload for result in points]
            reranked = self.reranker.rerank(query, chunks, top_k=limit)
            return reranked

        return [
            {"text": result.payload["text"], "metadata": result.payload.get("metadata", {})}
            for result in points[:limit]
        ]
