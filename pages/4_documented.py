import streamlit as st
import boto3
from streamlit_tags import st_tags
import json
import ast


st.set_page_config(
    page_title="Documented📂",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

from streamlit_utils import sidebar_navigation, load_streamlit_template
from aws_helper_functions import list_available_paycodes, get_paycode
from ai_summary import ai_summary


@st.cache_data(ttl=120)
def get_paycode_list():
    paycodes_list = list_available_paycodes(bucket="paycodehelper-documented")
    return paycodes_list


s3 = boto3.client("s3")


def submit_paycode(paycode, key):
    s3.put_object(Body=paycode, Bucket="paycodehelper-documented", Key=key)


def main():

    st.title("Lønarter📂")

    sidebar_navigation()

    streamlit_input_template = load_streamlit_template()

    paycode_list = get_paycode_list()

    paycode = st.selectbox(
        "Select a paycode",
        paycode_list,
        format_func=lambda s: s.replace("_", " ").replace(".json", "").title(),
    )

    # returns the paycode as a dictionary and a session state
    get_paycode(bucket="paycodehelper-documented", key=paycode)

    st.json(st.session_state["paycode"])

    col1, col2, col3 = st.columns(3)

    if "paycode" in st.session_state:
        with col2:
            st.button(
                "🤖Generate AI Summary🤖",
                on_click=ai_summary,
                args=(st.session_state["paycode"],),
            )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.header("Data Entry Form")

            st.session_state["paycode"]["user_input"]["bools"] = st.toggle(
                "AM-bidrag", value=False
            )
            for key in st.session_state["paycode"]["user_input"]["text_fields"]:
                st.session_state["paycode"]["user_input"]["text_fields"][key] = (
                    st.text_area(
                        label=key,
                        value=st.session_state["paycode"]["user_input"]["text_fields"][
                            key
                        ],
                    )
                )

            # Lønart input field
            st.session_state["paycode"]["user_input"]["input"] = st.multiselect(
                "Lønart input(s)",
                options=streamlit_input_template["input"],
                default=st.session_state["paycode"]["user_input"]["input"],
            )

            # Tags / keywords
            st.session_state["paycode"]["user_input"]["text_fields"]["tags"] = st_tags(
                label="Enter Keywords",
                text="Press enter to add more",
                value=ast.literal_eval(
                    st.session_state["paycode"]["user_input"]["text_fields"]["tags"]
                ),
                maxtags=100,
            )

        with col2:
            st.header("Lønart Information")

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
            st.text_input(label="Kommentar", value=catalog["kommentar"], disabled=True)
            st.info(f"Pensionsgrundlag: {catalog['Pensionsgrundlag']}")
            st.info(f"E-indkomst: {catalog['E-indkomst']}")

            for key in ["Ferieberettiget", "ATP-timer"]:
                checkbox_container = st.container()

                checked = catalog[key]
                st.session_state["paycode"]["catalog"][key] = checked

                checked = "✅" if catalog[key] == "Ja" else "❌"

                st.write(f"{key}: {checked}")

            st.info(f"IL-typer: {catalog['IL-typer']}")

        with col3:
            st.header("User Input Summary")

            if "ai_summary" in st.session_state:
                st.write(st.session_state["ai_summary"])

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
        st.session_state["submit_button"] = st.button(label="Save edits")

        if st.session_state.user_name:
            if st.session_state["submit_button"]:
                key = (
                    f"paycode_{st.session_state['paycode']['catalog']['paycode']}.json"
                )
                submit_paycode(
                    json.dumps(st.session_state.paycode, ensure_ascii=False), key
                )

                st.success("Paycode has been edited and saved!🚀")
                st.session_state.paycode = None


if __name__ == "__main__":  #
    main()
