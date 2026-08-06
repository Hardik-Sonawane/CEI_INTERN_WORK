def format_sources(sources):

    output = "\n\nSources:\n"


    for source in sources:

        output += (

            f"\n📄 Document: {source['source']}"

            f"\n📌 Section: {source['section']}"

            f"\n📄 Page: {source['page']}\n"

        )


    return output



if __name__ == "__main__":


    sample_sources = [

        {
            "source":"Creta.pdf",
            "section":"safety",
            "page":8
        }

    ]


    print(
        format_sources(sample_sources)
    )