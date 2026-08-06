from sentence_transformers import CrossEncoder


reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)



def rerank_results(
        query,
        retrieved_chunks,
        top_k=3
):

    pairs = []


    for chunk in retrieved_chunks:

        pairs.append(
            [
                query,
                chunk["content"]
            ]
        )


    scores = reranker.predict(
        pairs
    )


    ranked = []


    for chunk, score in zip(
        retrieved_chunks,
        scores
    ):

        chunk["rerank_score"] = float(score)

        ranked.append(chunk)



    ranked = sorted(
        ranked,
        key=lambda x:x["rerank_score"],
        reverse=True
    )


    return ranked[:top_k]



if __name__ == "__main__":

    from retriever import retrieve_answer


    query = "What safety features are available?"


    results = retrieve_answer(
        query,
        "Hyundai",
        "Creta",
        5
    )


    ranked_results = rerank_results(
        query,
        results
    )


    for item in ranked_results:

        print("\n-------------")

        print(
            item["rerank_score"]
        )

        print(
            item["metadata"]
        )

        print(
            item["content"][:300]
        )