from evaluation.dataset import evaluation_data
from evaluation.retrieval_metrics import (
    hit_rate_at_k,
    recall_at_k,
    precision_at_k,
    reciprocal_rank
)

from services.embeder import Embedder
from services.vector_store import VectorStore
from services.llm import LLM
from evaluation.faithfulness import Faithfulness


embedder = Embedder()
vector_store = VectorStore()
llm = LLM()
faithfulness = Faithfulness()


def evaluate_retrieval(k=5):

    results = []

    for item in evaluation_data:

        question = item["question"]
        relevant_chunks = item["relevant_chunks"]

        # Convert question into embedding
        query_embedding = embedder.embed_query(question)

        # Search Qdrant
        retrieved = vector_store.search(
            query_embedding.tolist(),
            query=question,
            limit=k
        )

        # Extract text from Qdrant results
        retrieved_chunks = [
            result["text"] if isinstance(result, dict) else result.payload["text"]
            for result in retrieved
        ]

        # Calculate metrics
        hit_rate = hit_rate_at_k(
            retrieved_chunks,
            relevant_chunks,
            k
        )

        recall = recall_at_k(
            retrieved_chunks,
            relevant_chunks,
            k
        )

        precision = precision_at_k(
            retrieved_chunks,
            relevant_chunks,
            k
        )

        rr = reciprocal_rank(
            retrieved_chunks,
            relevant_chunks,
            k
        )

        results.append({
            "question": question,
            "hit_rate": hit_rate,
            "recall": recall,
            "precision": precision,
            "reciprocal_rank": rr,
            "retrieved_chunks": retrieved_chunks[:3],
            "relevant_chunks": relevant_chunks[:3]
        })

    return results


def evaluate_faithfulness(k=5):

    results = []

    for i, item in enumerate(evaluation_data):

        question = item["question"]

        try:
            query_embedding = embedder.embed_query(question)

            retrieved = vector_store.search(
                query_embedding.tolist(),
                query=question,
                limit=k
            )

            retrieved_chunks = [
                result["text"] if isinstance(result, dict) else result.payload["text"]
                for result in retrieved
            ]

            context = "\n\n".join(retrieved_chunks)

            answer = "".join(llm.generate(context=context, question=question))

            score = faithfulness.evaluate(context=context, answer=answer)

            results.append({
                "question": question,
                "answer": answer,
                "faithfulness": score
            })
        except Exception as e:
            results.append({
                "question": question,
                "answer": f"Error: {str(e)}",
                "faithfulness": None
            })

    return results