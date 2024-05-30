

from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    HumanMessage
)

from streamlit_utils import add_to_streamlit_session_state

# load the model
chat = ChatOpenAI(model_name="gpt-4", temperature=0)

template = """You are an advanced AI assistant that summarizes info about paycodes.
You do not comment on the language, provide any translation, or comment on the paycode.
You only summarize the paycode.
You do not provide any thoughts on the paycode.

Provide a summary that is no longer than the actual paycode information itself.

Here's information on a paycode you want to summarize.

==================
Paycode: {paycode_text}
==================
"""


@add_to_streamlit_session_state(name="ai_summary")
def ai_summary(paycode):
    # format prompt
    prompt = template.format(paycode_text=paycode)
    # generate summary
    summary = chat([HumanMessage(content=prompt)])
    return summary.content


