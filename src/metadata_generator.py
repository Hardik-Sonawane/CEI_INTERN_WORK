import os
import json
import uuid
from datetime import datetime


INPUT_FOLDER = "data/chunks"
OUTPUT_FOLDER = "data/metadata"


os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)


def generate_metadata():

    for file in os.listdir(INPUT_FOLDER):

        if file.endswith(".json"):

            input_path = os.path.join(
                INPUT_FOLDER,
                file
            )


            with open(
                input_path,
                "r",
                encoding="utf-8"
            ) as f:

                chunks = json.load(f)


            enriched_chunks = []


            for chunk in chunks:

                metadata = chunk["metadata"]


                metadata.update(
                    {

                    "chunk_id": str(uuid.uuid4()),

                    "document_version": "1.0",

                    "created_date": datetime.now().strftime(
                        "%Y-%m-%d"
                    )

                    }
                )


                enriched_chunks.append(
                    {

                    "content": chunk["content"],

                    "metadata": metadata

                    }
                )


            output_path = os.path.join(
                OUTPUT_FOLDER,
                file
            )


            with open(
                output_path,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    enriched_chunks,
                    f,
                    indent=4,
                    ensure_ascii=False
                )


            print(
                "Metadata Generated:",
                file,
                "Chunks:",
                len(enriched_chunks)
            )



if __name__ == "__main__":
    generate_metadata()