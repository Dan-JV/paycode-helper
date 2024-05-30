import json

import streamlit as st


@st.cache_data
def load_streamlit_template():
    with open("paycode_input_template.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    return data


def add_to_streamlit_session_state(name: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            st.session_state[name] = result
            return result

        return wrapper

    return decorator


def sidebar_navigation():
    with st.sidebar:
        st.page_link("app.py", label="Home", icon="🏠")
        st.page_link("pages/1_leaderboard.py", label="Leaderboard", icon="🎖️")
        st.page_link("pages/2_feedback.py", label="Feedback", icon="😡")


@st.experimental_dialog("Feedback Form")
def feedbackform():
    with st.form("feedbackform"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        feedback = st.text_area("Feedback")

        if st.form_submit_button("Submit"):

            st.success("Thank you for your feedback!")
            st.rerun()
