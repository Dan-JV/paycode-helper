import streamlit as st
import re

st.set_page_config(
    page_title="Feedback",
    page_icon="imgs/page_icon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)


from src.pages.utils import sidebar_navigation
from src.utils.aws_helper_functions import read_feedback

st.title("Feedback")

sidebar_navigation()


feedback_data = read_feedback()

for key, feedback_list in feedback_data.items():
    formated_key = re.split("_|,", key)
    formated_key = f"**Paycode** : {formated_key[1]}"

    with st.expander(formated_key, expanded=False):
        for feedback in feedback_list:
            st.write(f"**Name:** {feedback['name']}")
            st.write(f"**Email:** {feedback['email']}")
            st.write(f"**Feedback:** {feedback['feedback']}")
            st.divider()  # This will separate each feedback entry
