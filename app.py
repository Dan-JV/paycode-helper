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

from aws_helper_functions import (
    move_paycode_from_source_to_target,
)

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


def submit_paycode(paycode):
    move_paycode_from_source_to_target(
        source_bucket="paycodehelper-processing",
        target_bucket="paycodehelper-documented",
        paycode=paycode,
    )
    st.write("Submitting paycode")
    st.success("Thank you!")



def main():
    streamlit_input_template = load_streamlit_template()

    choice = sidebar_navigation()

    col1, col2, col3 = st.columns(3)

    # User input form based on the provided JSON structure
    with st.form(key="data_form"):
        with col1:
            st.button(
                "Pick Random Paycode",
                on_click=get_random_paycode,
                args=("paycodehelper-templates", "paycodehelper-processing"),
            )
            st.header("Data Entry Form")

            st.toggle("AM-bidrag", value=False)
            for key in streamlit_input_template["text_area"]:
                st.text_area(
                    label=key, help=streamlit_input_template['text_area'][key]['help']
                )

            # Lønart input field
            st.multiselect(
                "Lønart input",
                options=streamlit_input_template["input"],
                help="Help us fill these",
            )

            st_tags(
                label="Enter Keywords",
                suggestions=streamlit_input_template["input"],
                text="Press enter to add more",
                maxtags=100,
            )

        with col2:

            st.header("Lønart Information")

            user_name = st.text_input("Enter your name: ")

            if "paycode" in st.session_state:
                catalog_fields = st.session_state["paycode"]["catalog"]
                st.text_input(
                    label="Paycode", value=catalog_fields["paycode"], disabled=True,
                )
                st.text_input(
                    label="Name", value=catalog_fields["name"], disabled=True,
                )
                st.text_input(
                    label="Type", value=catalog_fields["type"], disabled=True
                )
                st.text_input(
                    label="Kommentar", value=catalog_fields["kommentar"], disabled=True
                )

            else:
                st.info("No paycode selected", icon="ℹ")

            if "paycode" in st.session_state:
                catalog = st.session_state["paycode"]["catalog"]
                st.toggle("Pensionsgrundlag", value=catalog["Pensionsgrundlag"])
                st.toggle("E-indkomst", value=catalog["E-indkomst"])
                st.toggle("Ferieberettiget", value=catalog["Ferieberettiget"])
                st.toggle("ATP-timer", value=catalog["ATP-timer"])
                st.info(f"IL-typer: {catalog['IL-typer']}")

        submit_button = st.form_submit_button(label="Submit")

        if user_name and submit_button:
            # TODO: add all inputs to paycode (update json)
            update_leaderboard(user_name)
            submit_paycode(st.session_state.paycode)
            st.success(f"Document submitted by {user_name}!")

    with col3:
        st.header("User Input Summary")
        st.write(
            "AI Summary"
        )
        st.header("AI Summary")

        # Update placeholders
        st.write(
            "AI Summary"
        )

        st.header("Sources")
        st.write(
            """
        1. Source one: https://example.com/source1
        2. Source two: https://example.com/source2
        3. Source three: https://example.com/source3
        """
        )


if __name__ == "__main__":
    main()
