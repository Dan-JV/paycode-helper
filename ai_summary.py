


from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.docstore.document import Document


summary_prompt = PromptTemplate(
    input_variables=["text"],
    template="{text}"
)

summary_variable_name = "data"

llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-1106")
prompt = PromptTemplate.from_template(
    "Summarize this content: {data}"
)
llm_chain = LLMChain(llm=llm, prompt=prompt)
chain = StuffDocumentsChain(
    llm_chain=llm_chain,
    document_prompt=summary_prompt,
    document_variable_name=summary_variable_name
)


def ai_summary(paycode):
    doc = [Document(page_content=paycode, metadata={"text": f"{paycode}"})]
    print(chain.run(doc))



ai_summary("Mit navn er Johan")