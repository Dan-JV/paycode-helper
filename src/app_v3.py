from datetime import datetime
import streamlit as st
from src.field_model import load_template

st.set_page_config(
    page_title="Future Paycodes",
    page_icon="imgs/page_icon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.image("imgs/visma_enterprise.png")
st.title("Future Paycodes🙏")

from src.pages.utils import sidebar_navigation
from src.utils.aws_helper_functions import (
    upload_feedback,
    get_random_paycode,
)
from src.utils.leaderboard_utils import update_leaderboard
from src.utils.ai_summary import ai_summary
from src.app_utils import create_field, create_paycode_form



def main():
    file_path = "src/templates/field_templates.yaml"
    template = load_template(file_path).model_dump()
    form_template = template["form_template"]
    feedback_template = template["feedback_template"]

    sidebar_navigation()

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.button(
            "Pick Random Paycode🎲",
            on_click=get_random_paycode,
            args=("paycodehelper-templates", "paycodehelper-processing"),
        )
    if not "paycode" in st.session_state:
        st.info("No paycode selected", icon="ℹ")
    else:
        paycode = st.session_state["paycode"]
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
                        update_leaderboard(user_name)

        create_paycode_form(form_template)





if __name__ == "__main__":
    if "user_name" not in st.session_state or not st.session_state.user_name:
        with st.form(key="name_form"):
            user_name = st.text_input("Enter your name", placeholder="Your Name")
            submitted = st.form_submit_button("Submit")

            if submitted and user_name:
                st.session_state.user_name = user_name
                st.rerun()
            elif submitted and not user_name:
                st.warning("Name cannot be empty. Please enter your name.")
    else:
        main()
