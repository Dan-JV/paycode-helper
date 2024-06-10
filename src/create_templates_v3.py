import boto3
import polars as pl
import yaml

from src.field_model import load_template
from src.utils.aws_helper_functions import upload_yaml_object
from src.utils.helper_functions import create_yaml_object

from src.config import get_bucket_config

# Get the appropriate bucket configuration
bucket_config = get_bucket_config()

form_template = load_template("src/templates/field_templates.yaml")
form_template = form_template.form_template


df_paycodes = pl.read_csv("data/raw/paycode_variabel_count.csv")

# filter df_paycodes by LOENARTNR <> 6000-6999
df_paycodes = df_paycodes.filter(~(pl.col("LOENARTNR").str.starts_with("6")))
paycodes = df_paycodes["LOENARTNR"].to_list()

# get first 100 paycodes
paycodes = paycodes[0:150]

catalog_input_columns = [
    field.catalog_name
    for area in form_template.areas
    if area.name == "Catalog Input"
    for field in area.fields
    if hasattr(field, "catalog_name")
]


paycode_df = pl.read_csv(
    "data/processed/paycode_jens_cleaned_final.csv",
    infer_schema_length=int(1e10),
    columns=catalog_input_columns,
)



s3 = boto3.client("s3")

count = 0

for paycode in paycodes:
    paycode_data = paycode_df.filter(pl.col("Lønartnr") == paycode).to_dict(
        as_series=False
    )

    if len(paycode_data["Lønartnr"]) == 1:
        yaml_object = create_yaml_object(paycode_data, form_template.model_dump())

        yaml_string = yaml.dump(
            yaml_object, allow_unicode=True
        )  # Convert to YAML string
        upload_yaml_object(s3, bucket_config.template_bucket, yaml_string, paycode, verbose=True)
        count += 1
    else:
        print(f"Paycode {paycode} not found in paycode_df")

print(count)

