import json
import boto3
import polars as pl

# Config
paycodes = pl.read_csv("data/paycode_variabel_count.csv")["LOENARTNR"].to_list()

with open("paycode_template.json", "r", encoding="utf-8") as file:
    paycode_template = json.load(file)

bucket_name = "paycodehelper-templates"

paycode_df = pl.read_excel("data/Paycodes Standard.xlsx", sheet_name="Lønartskatalog")


def create_json_objects_and_upload_to_s3(
    paycodes, bucket_name, json_template, paycode_df
):
    s3 = boto3.client("s3")

    for paycode in paycodes:
        json_object = json_template.copy()

        try:
            # Get the paycode data from the DataFrame
            paycode_data = paycode_df.filter(pl.col("Lønartnr") == paycode).to_dict()

            catalog = json_object["catalog"]
            user_input = json_object["user_input"]
            ai_generated = json_object["ai_generated"]

            catalog["paycode"] = paycode
            catalog["name"] = paycode_data["Navn"][0]
            catalog["type"] = paycode_data["Type"][0]
            catalog["kommentar"] = paycode_data["Kommentar"][0]


            catalog["E-indkomst"] = True if paycode_data.get("E-indkomst timer", None)[0] else False
            catalog["Ferieberettiget"] = True if paycode_data.get("Ferieberretiget", None)[0] else False
            catalog["Pensionsgrundlag"] = True if paycode_data.get("Pensionsgrundlag", None)[0] else False
            catalog["ATP-timer"] = True if paycode_data.get("ATP-Timer", None)[0] else False
            
            # TODO: For IL-typer, if type=FAST, input=SATS, ATP-timer=blank -> IL-typer="indeholdt i normtid" -> see rules in notion
            catalog["IL-typer"] = paycode_data["IL-typer"][0] if paycode_data["IL-typer"][0] else None
            catalog["input"] = paycode_data["Input"][0]

            user_input["text_fields"]["Fastlønnede"] = ""
            user_input["text_fields"]["Timelønnede"] = ""
            user_input["text_fields"]["input"] = ""
            user_input["text_fields"]["general_description"] = ""
            user_input["text_fields"]["critical_information"] = ""
            user_input["text_fields"]["use_case_1"] = ""
            user_input["text_fields"]["use_case_2"] = ""
            user_input["text_fields"]["use_case_3"] = ""
            user_input["text_fields"]["tags"] = []

            user_input["bools"]["AM-bidrag"] = ""

            ai_generated["user_input_summary"] = ""
            guide_summary = ""
            guides = []

        except Exception as e:
            print(f"Paycode {paycode} had error {e}")
            continue


        try:
            json_data = json.dumps(json_object, ensure_ascii=False)
        except Exception as e:
            print(f"Paycode {paycode} had error {e}")
            continue

        # Generate a unique key for each JSON object
        key = f"paycode_{paycode}.json"

        # Upload the JSON object to S3
        s3.put_object(Body=json_data, Bucket=bucket_name, Key=key)

        # Generate a unique key for each JSON object
        key = f"paycode_{paycode}.json"

        # Upload the JSON object to S3
        s3.put_object(Body=json_data, Bucket=bucket_name, Key=key)


create_json_objects_and_upload_to_s3(
    paycodes, bucket_name, paycode_template, paycode_df=paycode_df
)
