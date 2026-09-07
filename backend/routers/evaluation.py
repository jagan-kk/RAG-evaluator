from fastapi import APIRouter
from evaluation.answer_metrics import evaluate_retrieval

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
