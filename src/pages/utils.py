import streamlit as st


def sidebar_navigation():
    with st.sidebar:
        st.image("imgs/visma_enterprise.png")
        st.page_link("app_v3.py", label="Home", icon="🏠")
        st.page_link("pages/1_leaderboard.py", label="Leaderboard", icon="🎖️")
        st.page_link("pages/2_feedback.py", label="Feedback", icon="😅")
        st.page_link("pages/3_guide.py", label="Guide", icon="📖")
        st.page_link("pages/4_documented.py", label="Paycodes", icon="📂")
