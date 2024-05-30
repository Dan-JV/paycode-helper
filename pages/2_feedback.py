import streamlit as st
import re
import datetime

st.set_page_config(
    page_title="Feedback",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)


from streamlit_utils import sidebar_navigation
from aws_helper_functions import read_feedback

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
