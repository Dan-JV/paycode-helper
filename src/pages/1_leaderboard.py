import streamlit as st


st.set_page_config(
    page_title="Leaderboard",
    page_icon="imgs/page_icon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)


from src.utils.leaderboard_utils import display_leaderboard
from src.pages.utils import sidebar_navigation

# If user reloads the page, redirect to login page
if "user_name" not in st.session_state or not st.session_state.user_name:
    st.switch_page("app_v3.py")


st.title("Lønart Leaderboard")

sidebar_navigation()

display_leaderboard()
