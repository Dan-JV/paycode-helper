import streamlit as st


# Streamlit config
st.set_page_config(page_title= "guide buddy",
                   page_icon=None, 
                   layout="wide", 
                   initial_sidebar_state="collapsed", 
                #    menu_items={
                #         'Get Help': 'https://www.extremelycoolapp.com/help',
                #         'Report a bug': "https://www.extremelycoolapp.com/bug",
                #         'About': "# This is a header. This is an *extremely* cool app!"
                #     }
                    )

def main():
    # Set up the layout with three columns
    

    col1, col2, col3 = st.columns(3)

    with col1:
        paycode_gen_col, paycode_skip_col = st.columns(2)
        with paycode_gen_col:
            st.button("Generate paycode")
        with paycode_skip_col:
            st.button("Skip this paycode")
        
        st.header("Data Entry Form")
        
        # User input form based on the provided JSON structure
        with st.form(key='data_form'):
            name = st.text_input("Lønart name", placeholder="Name of the paycode")
            print_sequence = st.text_input("Print sequence number", placeholder="What is this used for?")
            type_ = st.selectbox("Type", ["fast", "variable", "STILLINGSKATEGORI", "VARIABELEFTREG" , "FRAVÆR"])
            input_ = st.text_input("Input", placeholder="What type of input the lønart uses")

            # Information entry
            st.subheader("Information")
            use_story = st.text_area("How this paycode is commonly used")
            critical_information = st.text_area("Any critical information that needs to be known when using the paycode")
            extra_notes = st.text_area("Extra information that might be useful to know when using the paycode")
            
            # Calculations booleans
            st.subheader("Calculations")
            calculations = {
                "Løndel/-felt standardnavn": st.toggle(label="Løndel/-felt standardnavn", value=False),
                "AM-bidrag": st.toggle(label="AM-bidrag", value=False),
                "A-indk. og A-skat": st.toggle(label="A-indk. og A-skat", value=False),
                "Feriepenge, SH opsp. og fritvalgs (0013)": st.toggle(label="Feriepenge, SH opsp. og fritvalgs (0013)", value=False),
                "Feriefridags opsp.": st.toggle(label="Feriefridags opsp.", value=False),
                "St. Bededagstillæg": st.toggle(label="St. Bededagstillæg", value=False),
                "Pension PO1 PO2 FO2 GRL 7)": st.toggle(label="Pension PO1 PO2 FO2 GRL 7)", value=False),
                "Arbejdsmarkeds pension 5)": st.toggle(label="Arbejdsmarkeds pension 5)", value=False),
                "ATP-bidrag": st.toggle(label="ATP-bidrag", value=False),
            }
            
            st.subheader("Used With")
            used_with = {
                "Negativt fortegn 4)": st.toggle(label="Negativt fortegn 4)", value=False),
                "Autoløn": st.toggle(label="Autoløn", value=False),
                "Egen teksttekst 9) ikke saldo-tekst": st.toggle(label="Egen teksttekst 9) ikke saldo-tekst", value=False),
            }
            
            feltnummer_i_ejndkomst = st.text_input("Feltnummer i ejndkomst 8)")

            st.subheader("Opsamling til lønstatistik IL-typer")
            opsamling_til_lonstatistik = {
                "Bruttoløn": st.toggle(label="Bruttoløn (0010)", value=False),
                "Fastlønnede": st.text_input("Fastlønnede"),
                "Timelønnede": st.text_input("Timelønnede"),
                "Akkord og tidlønnsarbejde": st.text_input("Akkord og tidlønnsarbejde"),
            }

            submit_button = st.form_submit_button(label='Submit')

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
