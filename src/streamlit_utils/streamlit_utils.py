import streamlit as st

def add_to_streamlit_session_state(name: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            st.session_state[name] = result
            return result

        return wrapper

    return decorator

