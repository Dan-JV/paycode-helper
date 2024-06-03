import boto3
import polars as pl
import yaml

from src.field_model import load_template
from src.utils.aws_helper_functions import upload_yaml_object
from src.utils.helper_functions import create_yaml_object

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


s3 = boto3.client("s3")
bucket_name = "paycodehelper-templates"  # Update with your S3 bucket name

for paycode in paycodes:
    paycode_data = paycode_df.filter(pl.col("Lønartnr") == paycode).to_dict(as_series=False)

    if len(paycode_data["Lønartnr"]) == 1:
        yaml_object = create_yaml_object(paycode_data, form_template.model_dump())
        yaml_string = yaml.dump(
            yaml_object, allow_unicode=True
        )  # Convert to YAML string
        upload_yaml_object(s3, bucket_name, yaml_string, paycode)
    else:
        print(f"Paycode {paycode} not found in paycode_df")
