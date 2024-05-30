import boto3
import json
import streamlit as st
from streamlit_tags import st_tags

# must be the first line called to avoid it being called twice
st.set_page_config(
    page_title="Data Entry Form",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Data Entry Form")

from streamlit_utils import load_streamlit_template

from helper_functions import (
    get_random_paycode,
)

from leaderboard_utils import update_leaderboard


def sidebar_navigation():
    st.sidebar.title("Navigation")
    options = st.sidebar.radio("Go to", ["Home", "Leaderboard"])
    return options


def fill_paycode_form():
    pass


s3 = boto3.client("s3")


def submit_paycode(paycode, key):
    s3.put_object(Body=paycode, Bucket="paycodehelper-documented", Key=key)
    s3.delete_object(Bucket="paycodehelper-processing", Key=key)
    st.write("Submitting paycode")
    st.success("Thank you!")


def main():
    streamlit_input_template = load_streamlit_template()

    choice = sidebar_navigation()

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.button(
            "Pick Random Paycode",
            on_click=get_random_paycode,  # TODO: if you have already submitted a paycode, the input form should be cleaned of previous user input
            args=("paycodehelper-templates", "paycodehelper-processing"),
        )
    with col2:
        generate_ai_summary = st.button("Generate AI Summary")

    if "paycode" in st.session_state:
        with st.form(key="data_form"):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.header("Data Entry Form")

                st.session_state["paycode"]["user_input"]["bools"] = st.toggle(
                    "AM-bidrag", value=False
                )
                for key in streamlit_input_template["text_area"]:
                    st.session_state["paycode"]["user_input"]["text_fields"][key] = (
                        st.text_area(
                            label=key,
                            help=streamlit_input_template["text_area"][key]["help"],
                        )
                    )

                # Lønart input field
                st.session_state["paycode"]["user_input"]["input"] = st.multiselect(
                    "Lønart input",
                    options=streamlit_input_template["input"],
                    help="Help us fill these",
                )

                st.session_state["paycode"]["user_input"]["tags"] = st_tags(
                    label="Enter Keywords",
                    suggestions=streamlit_input_template["input"],
                    text="Press enter to add more",
                    maxtags=100,
                )

            with col2:
                st.header("Lønart Information")

                user_name = st.text_input("Enter your name: ")

                catalog = st.session_state["paycode"]["catalog"]
                st.text_input(
                    label="Paycode",
                    value=catalog["paycode"],
                    disabled=True,
                )
                st.text_input(
                    label="Name",
                    value=catalog["name"],
                    disabled=True,
                )
                st.text_input(label="Type", value=catalog["type"], disabled=True)
                st.text_input(
                    label="Kommentar", value=catalog["kommentar"], disabled=True
                )
                st.toggle("Pensionsgrundlag", value=catalog["Pensionsgrundlag"])
                st.toggle("E-indkomst", value=catalog["E-indkomst"])
                st.toggle("Ferieberettiget", value=catalog["Ferieberettiget"])
                st.toggle("ATP-timer", value=catalog["ATP-timer"])
                st.info(f"IL-typer: {catalog['IL-typer']}")

            with col3:
                st.header("User Input Summary")

                if generate_ai_summary:
                    print()

                st.header("AI Summary of Guides")

                # Update placeholders
                st.write("AI Summary")

                st.header("Sources")
                st.write(
                    """
                1. Source one: https://example.com/source1
                2. Source two: https://example.com/source2
                3. Source three: https://example.com/source3
                """
                )
            # TODO: Potential problem: if the user presses "enter" after filling out a field, the form will be submitted!
            st.session_state["submit_button"] = st.form_submit_button(label="Submit")

            if user_name:
                if st.session_state["submit_button"]:
                    update_leaderboard(user_name)
                    key = f"paycode_{st.session_state['paycode']['catalog']['paycode']}.json"
                    submit_paycode(
                        json.dumps(st.session_state.paycode, ensure_ascii=False), key
                    )
                    st.success(f"Document submitted by {user_name}!")

    else:
        st.info("No paycode selected", icon="ℹ")


if __name__ == "__main__":
    main()
