from datetime import datetime
import streamlit as st
import boto3
from src.field_model import load_template


st.set_page_config(
    page_title="Documented📂",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.pages.utils import sidebar_navigation
from src.utils.aws_helper_functions import list_available_paycodes, get_paycode
from src.utils.ai_summary import ai_summary
from src.utils.aws_helper_functions import upload_feedback
from src.utils.aws_helper_functions import list_available_paycodes, get_paycode
from src.app_utils import create_field, create_paycode_form


@st.cache_data(ttl=120)
def get_paycode_list():
    paycodes_list = list_available_paycodes(bucket="paycodehelper-documented")
    return paycodes_list


s3 = boto3.client("s3")


def submit_paycode(paycode, key):
    s3.put_object(Body=paycode, Bucket="paycodehelper-documented", Key=key)


def main():
    st.title("Paycodes📂")

    sidebar_navigation()

    paycode_list = get_paycode_list()

    paycode = st.selectbox(
        "Select a paycode",
        paycode_list,
    )
    paycodenr = paycode.split("_")[1].split(".")[0]
    st.session_state["paycodenr"] = paycodenr

    # returns the paycode as a dictionary and a session state
    # TODO: make this paycode in session_state different from the one on the main page
    paycode = get_paycode(bucket="paycodehelper-documented", key=paycode)
    st.session_state["paycode"] = paycode

    # st.json(st.session_state["paycode"], expanded=False)

    file_path = "src/templates/field_templates.yaml"
    template = load_template(file_path).model_dump()
    form_template = template["form_template"]
    feedback_template = template["feedback_template"]

    col1, col2, col3, col4, col5 = st.columns(5)

    form_template["areas"] = paycode["areas"]

    with col2:
        st.button(
            "Generate AI Summary🤖",
            on_click=ai_summary,
            args=(st.session_state["paycode"],),
        )
        if "ai_summary" in st.session_state:
            form_template["areas"][2]["fields"][0]["input"] = st.session_state[
                "ai_summary"
            ]
    with col3:
        with st.popover("Feedback😅"):
            with st.form(key="feedback_form", clear_on_submit=True):
                for index, field in enumerate(template["feedback_template"]["fields"]):

                    if field["name"] == "user_name":
                        field["input"] = st.session_state.user_name
                        disabled = True
                    elif field["name"] == "paycodenr":
                        field["input"] = st.session_state.paycodenr
                        disabled = True
                    else:
                        disabled = False

                    create_field(field, disabled)

                paycodenr = st.session_state.get("paycodenr", "")
                user_name = st.session_state.get("user_name", "")
                email = feedback_template["fields"][2]["input"]
                feedback = feedback_template["fields"][3]["input"]
                feedback_dict = {
                    "paycodenr": paycodenr,
                    "name": user_name,
                    "email": email,
                    "feedback": feedback,
                }

                key = f'{user_name}_{datetime.now().strftime("%Y-%m-%d-%H:%M:%S")}_paycode_{paycodenr}.json'
                submitted = st.form_submit_button("Submit")

                if submitted:
                    upload_feedback(feedback_dict, key=key)
                    st.success("Thank you for your feedback!")

    create_paycode_form(form_template)


if __name__ == "__main__":  #
    main()
