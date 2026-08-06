import os
import streamlit as st
from dotenv import load_dotenv
from google import genai


load_dotenv()


api_key = os.getenv("GEMINI_API_KEY")


if api_key is None:

    api_key = st.secrets["GEMINI_API_KEY"]



client = genai.Client(
    api_key=api_key
)

def generate_answer(
        question,
        context
):

    prompt = f"""

You are Drive Wise, an automotive AI assistant.

Answer only from the brochure context.

Rules:
- Do not use outside knowledge.
- Do not guess.
- If information is missing say:
  Information not available in brochure.


Context:

{context}


Question:

{question}

Answer:

"""


    response = client.models.generate_content(

        model="gemini-3.1-flash-lite",

        contents=prompt

    )


    return response.text



if __name__ == "__main__":


    answer = generate_answer(

        "How many airbags does Hyundai Creta have?",


        """
        Hyundai CRETA comes equipped with
        70+ advanced safety features including
        six airbags as standard.
        """

    )


    print(answer)