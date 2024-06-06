import streamlit as st

st.set_page_config(
    page_title="Guide📖",
    page_icon="imgs/page_icon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)


from src.pages.utils import sidebar_navigation

# If user reloads the page, redirect to login page
if "user_name" not in st.session_state or not st.session_state.user_name:
    st.switch_page("app_v3.py")

st.title("Guide📖")

sidebar_navigation()


st.markdown(
    """
## Paycode: 1181

### General
Lønart 1181, er en variabel lønart som ikke er ferieberettiget og kun går i pensionsgrundlag 6. Det eneste input der skal gives er et beløb.

### Critical
Du skal være opmærksom på at denne lønart IKKE er ferieberettiget, og at den kun indgår i pensionsgrundlag 6.

### Use Cases
1. Udbetaling af tillæg og bonuser til medarbejdere hvor de ikke skal optjene pension eller feriepenge af beløbet (kun hvis de ikke bruger pensionsgrundlag 6).
2. Udbetaling af beløb til fratrådte medarbejdere.

### Tags
Bonus, tillæg, ikke ferieberettiget, ikke pensionsgivende."""
)

st.divider()

st.markdown(
    """
## Paycode: 4760

### General
Lønart 4760 (udbetaling feriedage, primo), er en variabel lønart som bruges til at udbetale restferiedage, i henhold til ny ferielov. Det eneste input der skal gives er antal dage der ønskes udbetalt.

### Critical
Udbetaling af feriedage/-timer primo lønkørslen (behandles før afholdelse af ferie). Scenarie: Medarbejder har en restsaldo på 3 feriedage, som skal udbetales. Der registreres en uges ferie i januar, som skal anvende feriedage optjent i 2021.

### Use Cases
1. Udbetaling feriedage før træk af evt. registreret ferie.

### Tags
Udbetaling feriedage, overført ferie, årsskifte.

"""
)
