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
        json_object = json_template

        # Get the paycode data from the DataFrame
        paycode_data = paycode_df.filter(pl.col("Lønartnr") == paycode).to_dict()

        try:
            json_object["prefilled"]["paycode"] = paycode
            json_object["prefilled"]["name"] = paycode_data["Navn"][0]
            json_object["prefilled"]["type"] = paycode_data["Type"][0]
            json_object["prefilled"]["print_sequence"] = paycode_data[
                "Udskrivnings sekvens"
            ][0]
            json_object["prefilled"]["kommentar"] = paycode_data["Kommentar"][0]
            json_object["text_fields"]["input"] = paycode_data["Input"][0]


            # TODO: fill the bools by default from katalog
            bools = json_object["bools"]
            #bools["Løndel/-felt standardnavn"] = paycode_data.get("Løndel/-felt standardnavn", None)[0]
            
            # TODO: Maybe have a dict mapping between namings in a separate file or decide on a naming convention

            # e-indkomst
            bools["AM-bidrag"] = True if paycode_data.get("E-indkomst timer", None)[0] else False
            bools["A-indk. og A-skat"] = True if paycode_data.get("E-indkomst timer", None)[0] else False

            # ferie
            bools["St. Bededagstillæg"] = True if paycode_data.get("Ferieberretiget", None)[0] else False
            bools["Feriepenge, SH opsp. og fritvalgs (0013)"] = True if paycode_data.get("Ferieberretiget", None)[0] else False
            bools["Feriefridags opsp."] = True if paycode_data.get("Ferieberretiget", None)[0] else False
            
            IL_typer = paycode_data.get("IL-typer", None)[0]

            if IL_typer:
                IL_typer = IL_typer.split(",")

                if '10' in IL_typer:
                    bools["Bruttoløn (0010)"] = True
                elif '2020' in IL_typer: # TODO: should this be Akkord og tidlns arbejde in DL?
                    bools["Bruttoln (0010)"] = True
                else:
                    bools["Bruttoln (0010)"] = False
                

            # TODO: The rest

            #bools["Pension PO1 PO2 FO2 GRL 7)"] = paycode_data.get("Pension PO1 PO2 FO2 GRL 7)", None)[0]
            #bools["Arbejdsmarkeds pension 5)"] = paycode_data.get("Arbejdsmarkeds pension 5)", None)[0]
            #bools["ATP-bidrag"] = paycode_data.get("ATP-bidrag", None)[0]
            #bools["Negativt fortegn 4)"] = paycode_data.get("Negativt fortegn 4)", None)[0]
            #bools["Autoln"] = paycode_data.get("Autoln", None)[0]
            #bools["Egen teksttekst 9) ikke saldo-tekst"] = paycode_data.get("Egen teksttekst 9) ikke saldo-tekst", None)[0]


        except Exception as e:
            print(f"Paycode {paycode} had error {e}")
            continue

        # Convert the JSON object to a string
        json_data = json.dumps(json_object, ensure_ascii=False)

        # Generate a unique key for each JSON object
        key = f"paycode_{paycode}.json"

        # Upload the JSON object to S3
        s3.put_object(Body=json_data, Bucket=bucket_name, Key=key)

        json_data = json.dumps(json_object, ensure_ascii=False)

        # Generate a unique key for each JSON object
        key = f"paycode_{paycode}.json"

        # Upload the JSON object to S3
        s3.put_object(Body=json_data, Bucket=bucket_name, Key=key)


create_json_objects_and_upload_to_s3(
    paycodes, bucket_name, paycode_template, paycode_df=paycode_df
)
