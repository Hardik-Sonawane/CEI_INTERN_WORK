import os
import json
import chromadb
from sentence_transformers import SentenceTransformer


INPUT_FOLDER = "data/metadata"

CHROMA_PATH = "chroma_db"

COLLECTION_NAME = "drive_wise"


model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)


def generate_embeddings():

    ids = []
    documents = []
    embeddings = []
    metadatas = []


    for file in os.listdir(INPUT_FOLDER):

        if file.endswith(".json"):

            file_path = os.path.join(
                INPUT_FOLDER,
                file
            )


            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as f:

                chunks = json.load(f)


            for chunk in chunks:

                text = chunk["content"]

                metadata = chunk["metadata"]

                chunk_id = metadata["chunk_id"]


                vector = model.encode(
                    text
                ).tolist()


                ids.append(chunk_id)

                documents.append(text)

                embeddings.append(vector)

                metadatas.append(metadata)



    collection.add(

        ids=ids,

        documents=documents,

        embeddings=embeddings,

        metadatas=metadatas

    )


    print(
        "Total embeddings stored:",
        len(ids)
    )



if __name__ == "__main__":

    generate_embeddings()