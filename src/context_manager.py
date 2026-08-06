def build_context(
        ranked_chunks,
        max_length=3000
):

    context = ""

    sources = []


    for chunk in ranked_chunks:

        text = chunk["content"]


        if len(context) + len(text) > max_length:
            break


        context += "\n\n" + text


        sources.append(
            {
                "source": chunk["metadata"]["source"],
                "page": chunk["metadata"]["page"],
                "section": chunk["metadata"]["section"]
            }
        )


    return context, sources



if __name__ == "__main__":

    sample_chunks = [

        {
            "content":
            "Hyundai Creta has six airbags.",

            "metadata":
            {
                "source":"Creta.pdf",
                "page":8,
                "section":"safety"
            }
        }

    ]


    context, sources = build_context(
        sample_chunks
    )


    print(context)

    print(sources)