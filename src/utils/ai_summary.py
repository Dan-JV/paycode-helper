from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

from src.streamlit_utils.streamlit_utils import add_to_streamlit_session_state

# load the model
chat = ChatOpenAI(model_name="gpt-4", temperature=0)

template = """
You are a helpful and advanced expert AI assistant working at Visma Enterprise A/S. 
Your coworkers describe lønarter and you provide summaries of their descriptions Lønarter.


You do not comment on the language, provide any translation, or comment on the lønart.
You only summarize the lønart.
You do not provide any thoughts on the lønart.

Provide a summary that is no longer than the actual lønart information itself.
Highlight the most important parts.
Provide the summary in danish.

Here's information on a lønart you want to summarize.

==================
Lønart: {paycode_text}
==================
"""


# some helper func 

def format_paycode_for_ai(paycode: dict) -> str:
    """
    Extracts name and input for fields in the paycode and returns a string that can be used to generate a summary.
    """

    paycode_description_string = ""

    for area in paycode["areas"]:
        for field in area["fields"]:
            paycode_description_string += field["name"] + ": " + str(field["input"]) + "\n"
        paycode_description_string += "\n\n"

    return paycode_description_string


@add_to_streamlit_session_state(name="ai_summary")
def ai_summary(paycode):
    paycode_text = format_paycode_for_ai(paycode)
    prompt = template.format(paycode_text=paycode_text)
    summary = chat([HumanMessage(content=prompt)])
    return summary.content
