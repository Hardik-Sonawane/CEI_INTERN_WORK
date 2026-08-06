import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_PATH = "chroma_db"

COLLECTION_NAME = "drive_wise"


model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


collection = client.get_collection(
    name=COLLECTION_NAME
)



def retrieve_answer(
        query,
        brand,
        model_name,
        top_k=5
):

    query_embedding = model.encode(
        query
    ).tolist()


    results = collection.query(

        query_embeddings=[
            query_embedding
        ],

        n_results=top_k,

        where={
            "$and":[

                {
                    "brand": brand
                },

                {
                    "model": model_name
                }

            ]
        }

    )


    retrieved_chunks = []


    for i in range(
        len(results["documents"][0])
    ):

        retrieved_chunks.append(
            {

            "content":
            results["documents"][0][i],


            "metadata":
            results["metadatas"][0][i]

            }
        )


    return retrieved_chunks



if __name__ == "__main__":


    results = retrieve_answer(

        query="What safety features are available?",

        brand="Hyundai",

        model_name="Creta"

    )


    for item in results:

        print("\n----------------")

        print(item["metadata"])

        print(item["content"][:300])