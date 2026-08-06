import os
import json
import re


INPUT_FOLDER = "data/processed"
OUTPUT_FOLDER = "data/chunks"


os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)


SECTION_KEYWORDS = {

    "engine_performance": [
        "engine",
        "power",
        "torque",
        "transmission",
        "gearbox"
    ],

    "safety": [
        "airbag",
        "abs",
        "esc",
        "brake",
        "safety"
    ],

    "interior_comfort": [
        "seat",
        "interior",
        "comfort",
        "dashboard"
    ],

    "infotainment": [
        "screen",
        "audio",
        "bluetooth",
        "android",
        "apple"
    ],

    "dimensions": [
        "length",
        "width",
        "height",
        "wheelbase"
    ],

    "mileage_efficiency": [
        "mileage",
        "fuel",
        "efficiency"
    ]

}



def detect_section(text):

    text_lower = text.lower()


    scores = {}


    for section, keywords in SECTION_KEYWORDS.items():

        score = 0

        for word in keywords:

            if word in text_lower:
                score += 1


        scores[section] = score



    best_section = max(
        scores,
        key=scores.get
    )


    if scores[best_section] == 0:
        return "general"


    return best_section



def create_chunks():

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

                data = json.load(f)



            chunks = []


            for page in data["pages"]:

                text = page["cleaned_text"]


                words = text.split()


                chunk_size = 120


                for i in range(
                    0,
                    len(words),
                    chunk_size
                ):

                    chunk_text = " ".join(
                        words[i:i+chunk_size]
                    )


                    if len(chunk_text) > 50:

                        section = detect_section(
                            chunk_text
                        )


                        chunks.append(
                            {

                            "content": chunk_text,

                            "metadata": {

                                "brand": data["brand"],

                                "model": data["model"],

                                "source": data["document"],

                                "page": page["page_number"],

                                "section": section

                            }

                            }
                        )



            output_file = os.path.join(
                OUTPUT_FOLDER,
                file
            )


            with open(
                output_file,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    chunks,
                    f,
                    indent=4,
                    ensure_ascii=False
                )


            print(
                "Chunked:",
                file,
                "Chunks:",
                len(chunks)
            )



if __name__ == "__main__":
    create_chunks()