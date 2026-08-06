import os
import json
from pypdf import PdfReader


INPUT_FOLDER = "data/raw/Hyundai"
OUTPUT_FOLDER = "data/extracted_text"


os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def extract_pdf(pdf_path):

    reader = PdfReader(pdf_path)

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):

        text = page.extract_text()

        if text:
            pages.append(
                {
                    "page_number": page_number,
                    "text": text.strip()
                }
            )

    return pages


def process_documents():

    brand = "Hyundai"

    for file in os.listdir(INPUT_FOLDER):

        if file.endswith(".pdf"):

            model = file.replace(".pdf", "")

            pdf_path = os.path.join(
                INPUT_FOLDER,
                file
            )

            print("Processing:", file)


            pages = extract_pdf(pdf_path)


            document = {

                "brand": brand,

                "model": model,

                "document": file,

                "pages": []

            }


            for page in pages:

                document["pages"].append(
                    {
                        "page_number": page["page_number"],

                        "text": page["text"],

                        "metadata":
                        {
                            "brand": brand,

                            "model": model,

                            "source": file,

                            "page": page["page_number"]
                        }
                    }
                )


            output_file = os.path.join(
                OUTPUT_FOLDER,
                model + ".json"
            )


            with open(
                output_file,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    document,
                    f,
                    indent=4,
                    ensure_ascii=False
                )


            print("Saved:", output_file)



if __name__ == "__main__":
    process_documents()