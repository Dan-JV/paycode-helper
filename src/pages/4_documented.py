from datetime import datetime
import streamlit as st
import boto3
from src.field_model import load_template
from src.config import get_bucket_config

# Get the appropriate bucket configuration
bucket_config = get_bucket_config()


st.set_page_config(
    page_title="Lønarter",
    page_icon="imgs/page_icon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.pages.utils import sidebar_navigation
from src.utils.aws_helper_functions import list_available_paycodes, get_paycode
from src.utils.ai_summary import ai_summary
from src.utils.aws_helper_functions import upload_feedback
from src.utils.aws_helper_functions import list_available_paycodes, get_paycode
from src.app_utils import create_field, create_paycode_form


# If user reloads the page, redirect to login page
if "user_name" not in st.session_state or not st.session_state.user_name:
    st.switch_page("app_v3.py")


# @st.cache_data(ttl=5)
def get_paycode_list():
    paycodes_list = list_available_paycodes(bucket=bucket_config.documented_bucket)
    if len(paycodes_list) == 0:
        st.session_state["paycode_list"] = None

    else:
        st.session_state["paycode_list"] = paycodes_list


s3 = boto3.client("s3")


def submit_paycode(paycode, key):
    s3.put_object(Body=paycode, Bucket=bucket_config.documented_bucket, Key=key)


if "paycode_list" not in st.session_state:
    get_paycode_list()


def main():
    st.title("Paycodes📂")

    sidebar_navigation()

    # check if there are any paycodes available
    if st.session_state["paycode_list"] is not None:

        paycode = st.selectbox(
            "Vælg en Lønart",
            options=st.session_state["paycode_list"],
            on_change=get_paycode_list,
        )
        paycodenr = paycode.split("_")[1].split(".")[0]
        st.session_state["paycodenr"] = paycodenr

        paycode = get_paycode(bucket=bucket_config.documented_bucket, key=paycode)

        # st.json(st.session_state["paycode"], expanded=False)

        file_path = "src/templates/field_templates.yaml"
        template = load_template(file_path).model_dump()
        form_template = template["form_template"]
        feedback_template = template["feedback_template"]

        col1, col2, col3, col4, col5 = st.columns(5)

        form_template["areas"] = paycode["areas"]

        with col2:
            st.button(
                "Generer et AI Referat",
                on_click=ai_summary,
                args=(st.session_state["documented_paycode"],),
            )
            if "ai_summary" in st.session_state:
                form_template["areas"][2]["fields"][0]["input"] = st.session_state[
                    "ai_summary"
                ]
        with col3:
            with st.popover("Feedback😅"):
                with st.form(key="feedback_form", clear_on_submit=True):
                    for index, field in enumerate(
                        template["feedback_template"]["fields"]
                    ):

                        if field["name"] == "user_name":
                            field["input"] = st.session_state["user_name"]
                            disabled = True
                        elif field["name"] == "paycodenr":
                            field["input"] = st.session_state["paycodenr"]
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
                    submitted = st.form_submit_button(
                        "Submit", on_click=get_paycode_list
                    )

                    if submitted:
                        upload_feedback(feedback_dict, key=key)
                        st.success("Tak for din feedback!")

        create_paycode_form(form_template, "documented_paycode")


if __name__ == "__main__":  #
    main()
