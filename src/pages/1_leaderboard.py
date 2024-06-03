import streamlit as st


st.set_page_config(
    page_title="Lønart Leaderboard",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)


from src.utils.leaderboard_utils import display_leaderboard
from src.pages.utils import sidebar_navigation


st.title("Lønart Leaderboard")

sidebar_navigation()

display_leaderboard()
