import streamlit as st


st.set_page_config(
    page_title="Feedback",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)


from leaderboard_utils import display_leaderboard
from streamlit_utils import sidebar_navigation


st.title("Feedback")

sidebar_navigation()
