import os
import json
import re


INPUT_FOLDER = "data/extracted_text"
OUTPUT_FOLDER = "data/processed"


os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def clean_text(text):

    # remove extra spaces
    text = re.sub(
        r'\s+',
        ' ',
        text
    )

    # remove page numbers
    text = re.sub(
        r'\bPage\s+\d+\b',
        '',
        text,
        flags=re.IGNORECASE
    )

    # remove repeated website links
    text = re.sub(
        r'www\.\S+',
        '',
        text
    )

    # remove unwanted symbols
    text = re.sub(
        r'[^\w\s.,:%+\-/()]',
        '',
        text
    )

    return text.strip()



def process_json_files():

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


            for page in data["pages"]:

                page["cleaned_text"] = clean_text(
                    page["text"]
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
                    data,
                    f,
                    indent=4,
                    ensure_ascii=False
                )


            print(
                "Cleaned:",
                file
            )



if __name__ == "__main__":
    process_json_files()