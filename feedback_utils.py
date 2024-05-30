import streamlit as st
from aws_helper_functions import upload_feedback


@st.experimental_dialog("Feedback Form")
def feedbackform(paycode: str):
    with st.form("feedbackform"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        feedback = st.text_area("Feedback")

        feedback_dict = {"name": name, "email": email, "feedback": feedback}

        submitted = st.form_submit_button("Submit")
        if submitted:
            # Format filename
            key = f"paycode_{paycode}.json"

            upload_feedback(feedback_dict, key=key)

            st.success("Thank you for your feedback!")
            st.rerun()
