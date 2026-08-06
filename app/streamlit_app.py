import streamlit as st
import sys
import os


sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)


from src.app_pipeline import drive_wise_answer



st.set_page_config(

    page_title="Drive Wise AI",

    page_icon="🚗",

    layout="centered"

)



st.title("🚗 Drive Wise - Automotive AI Assistant")

st.write(
    "Ask questions about Hyundai cars using official brochure data."
)



brands = {

    "Hyundai":[

        "Alcazar",
        "Aura",
        "Creta",
        "Creta_EV",
        "Creta_N_Line",
        "Exter",
        "Grand_i10_NIOS",
        "i20",
        "i20_N_Line",
        "IONIQ5",
        "Venue",
        "Venue_N_Line",
        "Verna"

    ]

}



brand = st.selectbox(

    "Select Brand",

    list(brands.keys())

)



model = st.selectbox(

    "Select Car Model",

    brands[brand]

)



question = st.text_input(

    "Ask your question",

    placeholder="Example: What safety features are available?"

)



if st.button("Ask Drive Wise"):


    if question:


        with st.spinner(
            "Searching brochure and generating answer..."
        ):


            response = drive_wise_answer(

                brand,

                model,

                question

            )


        st.subheader(
            "Answer"
        )


        st.write(
            response
        )


    else:

        st.warning(
            "Please enter a question."
        )