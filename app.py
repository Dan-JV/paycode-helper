import streamlit as st
import json

from helper_functions import *

@st.cache_data
def load_streamlit_template():
    with open ("paycode_input_template.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    return data

streamlit_input_template = load_streamlit_template()
    

# Streamlit config
# st.set_page_config(page_title= "guide buddy",
#                    page_icon=None, 
#                    layout="wide", 
#                    initial_sidebar_state="collapsed", 
#                 #    menu_items={
#                 #         'Get Help': 'https://www.extremelycoolapp.com/help',
#                 #         'Report a bug': "https://www.extremelycoolapp.com/bug",
#                 #         'About': "# This is a header. This is an *extremely* cool app!"
#                 #     }
#                     )


def update_leaderboard():
    pass

def fill_paycode_form():
    pass

def submit_paycode(paycode):
    move_paycode_from_source_to_target(source_bucket="paycodehelper-processing", target_bucket="paycodehelper-documented", paycode=paycode)
    st.write("Submitting paycode")
    st.success("Thank you!")
    update_leaderboard()




def main():
    # Set up the layout with three columns
    

    col1, col2, col3 = st.columns(3)

    with col1:
        st.button("Pick Random Paycode", on_click=get_random_paycode, args=("paycodehelper-templates", "paycodehelper-processing"))

        #if pick_random:
            #st.session_state.paycode = get_random_paycode(source_bucket="paycodehelper-templates", target_bucket="paycodehelper-processing")
        
        st.header("Data Entry Form")
        
        # User input form based on the provided JSON structure
        with st.form(key='data_form'):
            # TODO add prefilled fields box


            # Information entry
            st.subheader("Information")
            for key in streamlit_input_template["text_area"]:
                st.text_area(key, help=streamlit_input_template["text_area"][key]["help"])
            
            


            # TODO: for the multi selectionbox for the input field we sohuld use 9-18 in from this link https://help.vismaenterprise.dk/vismaloen-standard/decantral-registrering/00086-decentral-registrering
            # input entry
            st.subheader("Lønart input")
            st.multiselect("test", options=streamlit_input_template["input"], help="test help")
            
            # TODO: Bools should be static information displayted in the middle column
            st.subheader("lønbehandlingskategorier")
            for key in streamlit_input_template["bools"]:
                st.toggle(key, 
                            help=streamlit_input_template["bools"][key]["help"],
                            value=streamlit_input_template["bools"][key]["default"])


            submit_button = st.form_submit_button(label='Submit')

            if submit_button:
                submit_paycode()

    with col2:
        st.header("AI Summary")
        
        # Update placeholders
        st.write("""Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam molestie erat tortor, at mollis lorem iaculis ut. Aliquam erat volutpat. Sed mauris metus, congue ac quam ac, tincidunt sodales nulla. Nunc fermentum fringilla augue, sit amet mattis dolor finibus at. Etiam id feugiat diam, non imperdiet nisi. Cras vulputate suscipit tortor, a malesuada neque tristique id. Aliquam egestas, est eget pulvinar lacinia, tortor purus semper tortor, nec lacinia dolor sem a nisi. Vestibulum tincidunt quam magna, eu cursus justo ultrices quis. Vestibulum aliquet, eros in mollis sollicitudin, arcu odio finibus ante, vitae convallis lorem orci vitae orci.""")
        
        st.header("Sources")
        st.write("""
        1. Source one: https://example.com/source1
        2. Source two: https://example.com/source2
        3. Source three: https://example.com/source3
        """)

    with col3:
        st.header("Leaderboard")
        
        
        # Mockup leaderboard
        leaderboard = {
            "Alice": 10,
            "Bob": 8,
            "Charlie": 7,
            "David": 5,
            "Eve": 3
        }

        # Display leaderboard
        total = 0
        for user, count in leaderboard.items():
            st.write(f"{user}: {count} forms")
            total += count
        
        st.write(f"Total forms: {total}")



       


            

if __name__ == '__main__':
    main()
