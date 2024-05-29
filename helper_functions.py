import streamlit as st


from aws_helper_functions import get_random_paycode



def pick_random_paycode_click():
    result = get_random_paycode(
        source_bucket="paycodehelper-templates",
        target_bucket="paycodehelper-processing",
    )
    st.session_state.paycode = result



