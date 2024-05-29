import streamlit as st
from streamlit_tags import st_tags

# must be the first line called to avoid it being called twice
st.set_page_config(
    page_title="guide buddy",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

from helper_functions import (
    move_paycode_from_source_to_target,
    get_random_paycode,
    load_streamlit_template,
    read_leaderboard,
    write_leaderboard,
    update_leaderboard,
)

st.title("Paycode Helper")


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


# Leaderboard function
def display_leaderboard():
    leaderboard_json = read_leaderboard()
    leaderboard = leaderboard_json["leaderboard"]

    st.markdown("## Leaderboard")

    for i, entry in enumerate(leaderboard):
        if i == 0:
            medal = "🥇"
        elif i == 1:
            medal = "🥈"
        elif i == 2:
            medal = "🥉"
        else:
            medal = ""

        st.write(f"{medal} {entry['name']}: {entry['score']} documents")


def main():
    # Set up the layout with three columns
    streamlit_input_template = load_streamlit_template()

    col1, col2, col3, col4 = st.columns(4)

    # User input form based on the provided JSON structure
    with st.form(key="data_form"):
        with col1:
            st.subheader("Data Entry Form")

            st.button(
                "Pick Random Paycode",
                on_click=get_random_paycode,
                args=("paycodehelper-templates", "paycodehelper-processing"),
            )
            user_name = st.text_input("Enter your name: ")

            if "paycode" in st.session_state:
                prefilled_fields = st.session_state["paycode"]["prefilled"]

                st.markdown("#### Paycode: ")
                st.info(f'{prefilled_fields["paycode"]}')
                st.markdown("#### Name: ")
                st.info(f'{prefilled_fields["name"]}')
                st.markdown("#### Type: ")
                st.info(f'{prefilled_fields["type"]}')
                st.markdown("#### Kommentar: ")
                st.info(f'{prefilled_fields["kommentar"]}')

            else:
                st.info("No paycode selected", icon="ℹ")
                st.markdown("#### Paycode Name: ")
                st.info("")
                st.markdown("#### Type: ")
                st.info("")
                st.markdown("#### Kommentar: ")
                st.info("")

            st.subheader("Information")
            st.toggle("AM-bidrag", value=False)
            for key in streamlit_input_template["text_area"]:
                st.text_area(
                    key, help=streamlit_input_template["text_area"][key]["help"]
                )

            st_tags(
                label="Enter Keywords",
                suggestions=streamlit_input_template["input"],
                text="Press enter to add more",
                maxtags=100,
            )

        with col2:

            st.subheader("Lønart input")
            st.multiselect(
                "test", options=streamlit_input_template["input"], help="test help"
            )

            # TODO: Bools should be static information displayted in the middle column
            st.subheader("lønbehandlingskategorier")
            for key in streamlit_input_template["bools"]:
                st.toggle(
                    key,
                    help=streamlit_input_template["bools"][key]["help"],
                    value=streamlit_input_template["bools"][key]["default"],
                    disabled=True,
                )

        submit_button = st.form_submit_button(label="Submit")

        if user_name and submit_button:
            update_leaderboard(user_name)
            # submit_paycode()
            st.success(f"Document submitted by {user_name}!")

    with col3:
        st.header("AI Summary")

        # Update placeholders
        st.write(
            """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam molestie erat tortor, at mollis lorem iaculis ut. Aliquam erat volutpat. Sed mauris metus, congue ac quam ac, tincidunt sodales nulla. Nunc fermentum fringilla augue, sit amet mattis dolor finibus at. Etiam id feugiat diam, non imperdiet nisi. Cras vulputate suscipit tortor, a malesuada neque tristique id. Aliquam egestas, est eget pulvinar lacinia, tortor purus semper tortor, nec lacinia dolor sem a nisi. Vestibulum tincidunt quam magna, eu cursus justo ultrices quis. Vestibulum aliquet, eros in mollis sollicitudin, arcu odio finibus ante, vitae convallis lorem orci vitae orci."""
        )

        st.header("Sources")
        st.write(
            """
        1. Source one: https://example.com/source1
        2. Source two: https://example.com/source2
        3. Source three: https://example.com/source3
        """
        )

    with col4:
        display_leaderboard()


if __name__ == "__main__":
    main()
