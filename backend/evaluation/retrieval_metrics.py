def normalize(text):
    return " ".join(text.split())


def is_relevant(retrieved_chunk, relevant_chunk):
    r = normalize(retrieved_chunk).lower()
    rel = normalize(relevant_chunk).lower()
    return rel in r or r in rel


def hit_rate_at_k(retrieved_chunks, relevant_chunks, k=5):
    retrieved_chunks = retrieved_chunks[:k]
    for chunk in retrieved_chunks:
        for rel in relevant_chunks:
            if is_relevant(chunk, rel):
                return 1
    return 0


def recall_at_k(retrieved_chunks, relevant_chunks, k=5):
    retrieved_chunks = retrieved_chunks[:k]
    if not relevant_chunks:
        return 0
    retrieved_relevant = 0
    for rel in relevant_chunks:
        for chunk in retrieved_chunks:
            if is_relevant(chunk, rel):
                retrieved_relevant += 1
                break
    return retrieved_relevant / len(relevant_chunks)


def precision_at_k(retrieved_chunks, relevant_chunks, k=5):
    retrieved_chunks = retrieved_chunks[:k]
    if not retrieved_chunks:
        return 0
    retrieved_relevant = 0
    for chunk in retrieved_chunks:
        for rel in relevant_chunks:
            if is_relevant(chunk, rel):
                retrieved_relevant += 1
                break
    return retrieved_relevant / len(retrieved_chunks)


def reciprocal_rank(retrieved_chunks, relevant_chunks, k=5):
    retrieved_chunks = retrieved_chunks[:k]
    for index, chunk in enumerate(retrieved_chunks, start=1):
        for rel in relevant_chunks:
            if is_relevant(chunk, rel):
                return 1 / index
    return 0


def mean_reciprocal_rank(evaluation_data, k=5):
    scores = []
    for item in evaluation_data:
        score = reciprocal_rank(
            item["retrieved_chunks"],
            item["relevant_chunks"],
            k
        )
        scores.append(score)
    if len(scores) == 0:
        return 0
    return sum(scores) / len(scores)
