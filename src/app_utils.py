import math
import yaml
import streamlit as st
from time import sleep

from streamlit_tags import st_tags
from src.utils.ai_summary import ai_summary


from src.utils.leaderboard_utils import display_leaderboard, update_leaderboard
from src.utils.aws_helper_functions import (
    get_random_paycode,
    submit_paycode,
    list_available_paycodes,
)


from src.config import get_bucket_config

# Get the appropriate bucket configuration
bucket_config = get_bucket_config()


def create_field(field: dict, disabled: bool = False):
    field_type = field["type"]
    label = field["front_end_name"]
    value = field["input"]

    # if value is None, set it to an empty string
    if value == "nan":
        value = ""

    if field_type == "text_input":
        field["input"] = st.text_input(
            label,
            value=value,
            help=field["help"],
            disabled=disabled,
            placeholder=field["placeholder"],
        )
    elif field_type == "selectbox":
        field["input"] = st.selectbox(
            label,
            options=field["options"],
            index=field["options"].index(field["default"]) if field["default"] else 0,
            help=field["help"],
            disabled=disabled,
        )
    elif field_type == "multiselect":
        field["input"] = st.multiselect(
            label,
            options=field["options"],
            default=field["input"],
            help=field["help"],
            disabled=disabled,
            placeholder=field["placeholder"],
        )
    elif field_type == "text_area":
        field["input"] = st.text_area(
            label,
            value=value,
            help=field["help"],
            placeholder=field["placeholder"],
            disabled=disabled,
        )
    elif field_type == "tags":
        field["input"] = st_tags(
            label=label,
            text="Press enter to add more",
            value=value,
        )
    elif field_type == "toggle":
        field["input"] = st.toggle(
            label=label,
            value=value == True,
            help=field["help"],
            disabled=disabled,
        )
    elif field_type == "write":
        field["input"] = st.write(label)

    elif field_type == "markdown":
        placeholder = st.empty()
        placeholder.markdown(
            body=value,
            help=field["help"],
        )
    elif field_type == "bool_Ja_Nej":
        if value == "Ja":
            st.text(label, help=field["help"])
            st.markdown("✅")

        elif value == "Nej":
            st.text(label, help=field["help"])
            st.markdown("❌")

    elif field_type == "radio":
        field["input"] = st.radio(
            label=label,
            options=[True, False],
            format_func=lambda x: "Ja" if x else "Nej",
            index=1,
        )
    else:
        st.error(f'Unsupported field type: {field["type"]}')

    return field


def create_paycode_form(key, form_template, paycode_session_state_name):
    with st.form(key=key, clear_on_submit=True):
        col1, col2, col3 = st.columns(3)

        for area in form_template["areas"]:
            with col1:
                if area["name"] == "User Input":
                    st.header(
                        f"Lønart: {st.session_state[paycode_session_state_name]['areas'][1]['fields'][0]['input']}"
                    )
                    st.subheader(
                        f"{st.session_state[paycode_session_state_name]['areas'][1]['fields'][1]['input']}"
                    )
                    create_area_fields(area, fields_disabled=False)

            with col2:
                if area["name"] == "Catalog Input":
                    st.header("Standard Lønartskatalog")
                    create_area_fields(area, fields_disabled=True)

        with col3:
            # leaderboard
            st.header("Leaderboard")
            display_leaderboard()

        st.session_state["submit_button"] = st.form_submit_button(label="Submit")

        if st.session_state["user_name"]:
            if st.session_state["submit_button"]:
                # TODO: Add validation for tags field and use_case_1
                # This solution is duct tape on here please fix
                # if the tags input is none or empty list then stop the submission
                if (
                    form_template["areas"][0]["fields"][0]["input"] is None
                    or not form_template["areas"][0]["fields"][0]["input"]
                    and form_template["areas"][0]["fields"][1]["input"] is None
                    or not form_template["areas"][0]["fields"][1]["input"]
                ):
                    st.error(
                        "Du skal udfylde tags og mindst én use case, før du kan indsende!"
                    )
                    st.stop()

                update_leaderboard(st.session_state["user_name"])
                key = f"paycode_{st.session_state['paycodenr']}.yaml"

                yaml_string = yaml.dump(
                    form_template, allow_unicode=True
                )  # Convert to YAML string

                submit_paycode(yaml_string, key)
                st.success(f"Document submitted by {st.session_state['user_name']}!")

                del st.session_state["paycode"]
                # get_random_paycode(
                #     source_bucket="paycodehelper-templates",
                #     target_bucket="paycodehelper-processing",
                # )
                sleep(5)
                st.rerun()


def create_area_fields(area: dict, fields_disabled=False):
    with st.expander(area["name"], expanded=True):
        fields = area["fields"]

        for field in fields:
            create_field(field, disabled=fields_disabled)


@st.cache_data(ttl=20)
def paycode_progress():
    num_documented_paycodes = len(
        list_available_paycodes(bucket_config.documented_bucket)
    )
    if num_documented_paycodes > 100:
        progress_text = (
            f"Alle lønarter dokumenteret 🎉 - Antal : {num_documented_paycodes} / 100"
        )
        st.progress(num_documented_paycodes, text=progress_text)

    else:
        progress_text = (
            f"Dokumenterede Lønarter 🚀 - Antal: {num_documented_paycodes} / 100"
        )
        st.progress(num_documented_paycodes, text=progress_text)
