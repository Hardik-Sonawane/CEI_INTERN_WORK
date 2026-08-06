from src.retriever import retrieve_answer
from src.reranker import rerank_results
from src.context_manager import build_context
from src.gemini_generator import generate_answer
from src.source_attribution import format_sources

def drive_wise_answer(
        brand,
        model,
        question
):


    # Step 1: Retrieve

    retrieved_chunks = retrieve_answer(

        query=question,

        brand=brand,

        model_name=model,

        top_k=5

    )


    # Step 2: Re-ranking

    ranked_chunks = rerank_results(

        question,

        retrieved_chunks,

        top_k=3

    )


    # Step 3: Context control

    context, sources = build_context(

        ranked_chunks,

        max_length=3000

    )


    # Step 4: Gemini answer

    answer = generate_answer(

        question,

        context

    )


    # Step 5: Source details

    source_text = format_sources(

        sources

    )


    final_response = (

        answer

        +

        "\n\n"

        +

        source_text

    )


    return final_response




if __name__ == "__main__":


    response = drive_wise_answer(

        brand="Hyundai",

        model="Creta",

        question="What safety features are available?"

    )


    print(response)