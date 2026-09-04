from qdrant_client import QdrantClient
from qdrant_client.models import Distance,VectorParams,PointStruct

class VectorStore:
    def __init__(self):
        self.client=QdrantClient(
            url="http://localhost:6333"
        )

        self.collection_name="documents"

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

    def search(self, query_embedding, limit=5):

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=limit
        )

        return results.points