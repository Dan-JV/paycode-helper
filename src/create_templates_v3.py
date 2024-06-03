import boto3
import polars as pl
import yaml

from src.field_model import load_template
from src.utils.aws_helper_functions import upload_yaml_object
from src.utils.helper_functions import create_yaml_object

from src.RAG_pipeline.pipeline import create_pipeline

form_template = load_template("src/templates/field_templates.yaml")
form_template = form_template.form_template

paycodes = pl.read_csv("data/paycode_variabel_count.csv")["LOENARTNR"].to_list()

catalog_input_columns = [
    field.catalog_name
    for area in form_template.areas
    if area.name == "Catalog Input"
    for field in area.fields
    if hasattr(field, "catalog_name")
]


paycode_df = pl.read_csv(
    "data/paycode_jens_cleaned_with_count.csv",
    infer_schema_length=int(1e10),
    columns=catalog_input_columns,
)


# RAG config and setup for AI guide summary
def load_config():
    with open("src/RAG_pipeline/conf/config.yaml", "r") as file:
        config = yaml.safe_load(file)
    return config


config = load_config()
chain = create_pipeline(**config["system_settings"])
system_prompts: list = chain.get_prompts()
system_prompt: str = system_prompts[1].messages[0].prompt.template


s3 = boto3.client("s3")
bucket_name = "paycodehelper-templates"  # Update with your S3 bucket name

for paycode in paycodes:
    paycode_data = paycode_df.filter(pl.col("Lønartnr") == paycode).to_dict(
        as_series=False
    )

    if len(paycode_data["Lønartnr"]) == 1:
        yaml_object = create_yaml_object(paycode_data, form_template.model_dump())

        chain_response = chain.invoke(
            {
                "input": f"Kan du beskrive variabel lønart {paycode}",
                "chat_history": chain.get_session_history(paycode),
            },
            config={"configurable": {"session_id": paycode}},
        )

        # Parse out the urls from the chain response
        guide_links = list(set([i.metadata["url"] for i in chain_response["context"]]))
        guide_titels = list(
            set([i.metadata["Header 1"] for i in chain_response["context"]])
        )
        guide_markdown = [
            f"- [{guide_titels[i]}]({url})" for i, url in enumerate(guide_links)
        ]
        guide_markdown = "\n".join(guide_markdown)
        guide_markdown = "#### Guides:\n" + guide_markdown

        # Add the AI guide summary to the yaml object
        yaml_object["areas"][2]["fields"][1]["input"] = chain_response["answer"]

        # Add the guides to the yaml object
        yaml_object["areas"][2]["fields"][2]["input"] = guide_markdown

        yaml_string = yaml.dump(
            yaml_object, allow_unicode=True
        )  # Convert to YAML string
        upload_yaml_object(s3, bucket_name, yaml_string, paycode)
    else:
        print(f"Paycode {paycode} not found in paycode_df")
