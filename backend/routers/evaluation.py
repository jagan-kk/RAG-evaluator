from fastapi import APIRouter
from evaluation.answer_metrics import evaluate_retrieval, evaluate_faithfulness,evaluate_relevance

router = APIRouter(
    prefix="/evaluation",
    tags=["evaluation"]
)


@router.get("/retrieval")
def retrieval_evaluation(k: int = 5):
    results = evaluate_retrieval(k=k)

    avg_hit_rate = sum(r["hit_rate"] for r in results) / len(results) if results else 0
    avg_recall = sum(r["recall"] for r in results) / len(results) if results else 0
    avg_precision = sum(r["precision"] for r in results) / len(results) if results else 0
    avg_rr = sum(r["reciprocal_rank"] for r in results) / len(results) if results else 0

    for r in results:
        print(f"\n[Eval] Q: {r['question'][:60]}")
        print(f"  retrieved_chunks: {r.get('retrieved_chunks', [])}")
        print(f"  relevant_chunks:  {r.get('relevant_chunks', [])}")
        print(f"  -> hit={r['hit_rate']} recall={r['recall']} precision={r['precision']} rr={r['reciprocal_rank']}")

    return {
        "results": results,
        "averages": {
            "hit_rate": avg_hit_rate,
            "recall": avg_recall,
            "precision": avg_precision,
            "reciprocal_rank": avg_rr
        }
    }


@router.get("/faithfulness")
def faithfulness_evaluation(k: int = 5, provider: str = "openrouter", start: int = 0, end: int = 10):
    results = evaluate_faithfulness(k=k, provider=provider, start=start, end=end)

    valid_scores = [r["faithfulness"] for r in results if r["faithfulness"] is not None]
    avg_faithfulness = sum(valid_scores) / len(valid_scores) if valid_scores else 0

    return {
        "results": results,
        "average": avg_faithfulness
    }


@router.get("/relevance")
def relevance_evaluation(
    k: int = 5,
    provider: str = "openrouter",
    start: int = 0,
    end: int = 10
):
    results = evaluate_relevance(
        k=k,
        provider=provider,
        start=start,
        end=end
    )

    valid_scores = [
        r["relevance"]["score"]
        for r in results
        if r["relevance"] is not None
    ]

    avg_relevance = (
        sum(valid_scores) / len(valid_scores)
        if valid_scores else 0
    )

    return {
        "results": results,
        "average": avg_relevance
    }