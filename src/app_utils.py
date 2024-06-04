import yaml
import streamlit as st

from streamlit_tags import st_tags

from src.utils.leaderboard_utils import update_leaderboard
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
        st.markdown(
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
    else:
        st.error(f'Unsupported field type: {field["type"]}')

    return field


def create_paycode_form(form_template, paycode_session_state_name):
    with st.form(key="data_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)

        # Use form_template to structure the layout dynamically
        for area in form_template["areas"]:
            with col1:
                if area["name"] == "User Input":
                    st.header(
                        f"User Input for paycode {st.session_state[paycode_session_state_name]['areas'][1]['fields'][0]['input']}"
                    )
                    st.subheader(
                        f"{st.session_state[paycode_session_state_name]['areas'][1]['fields'][1]['input']}"
                    )

                    with st.expander(area["name"], expanded=True):
                        for field in area["fields"]:
                            create_field(field, disabled=False)
            with col2:
                if area["name"] == "Catalog Input":
                    st.header("Paycode Information")

                    with st.expander(area["name"], expanded=True):
                        for field in area["fields"]:
                            create_field(field, disabled=True)
            with col3:
                if area["name"] == "AI Input":
                    st.header("AI Paycode Summary")

                    with st.expander(area["name"], expanded=True):
                        for field in area["fields"]:
                            create_field(field, disabled=True)
        
        st.info("Please review the paycode information and AI summary before submitting")

        st.session_state["submit_button"] = st.form_submit_button(label="Submit")

        if st.session_state["user_name"]:
            if st.session_state["submit_button"]:
                update_leaderboard(st.session_state["user_name"])
                key = f"paycode_{st.session_state['paycodenr']}.yaml"

                yaml_string = yaml.dump(
                    form_template, allow_unicode=True
                )  # Convert to YAML string

                submit_paycode(yaml_string, key)
                st.success(f"Document submitted by {st.session_state['user_name']}!")


st.cache_data(ttl=60)


def paycode_progress():
    num_documented_paycodes = len(
        list_available_paycodes(bucket_config.documented_bucket)
    )

    if num_documented_paycodes > 100:
        progress_text = (
            f"All paycodes documented 🎉 - Count : {num_documented_paycodes} / 100"
        )
        st.progress(num_documented_paycodes, text=progress_text)

    else:
        progress_text = (
            f"Documented paycodes 🚀 - Count : {num_documented_paycodes} / 100"
        )
        st.progress(num_documented_paycodes, text=progress_text)
