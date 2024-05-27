import json
import boto3
import polars as pl

# Config
paycodes = pl.read_csv("data/parcode_variabel_count.csv")['LOENARTNR'].to_list()

with open("paycode_template.json", "r", encoding="utf-8") as file:
    paycode_template = json.load(file)

bucket_name = 'paycodehelper'

paycode_df = pl.read_excel("data/Paycodes Standard.xlsx", sheet_name="Lønartskatalog")


def create_json_objects_and_upload_to_s3(paycodes, bucket_name, json_template, paycode_df):
    s3 = boto3.client('s3')
    
    for paycode in paycodes:
        json_object = json_template

        # Get the paycode data from the DataFrame
        paycode_data = paycode_df.filter(pl.col("Lønartnr") == paycode).to_dict()

        try:
            json_object["prefilled"]['paycode'] = paycode
            json_object["prefilled"]['name'] = paycode_data['Navn'][0]
            json_object["prefilled"]['type'] = paycode_data['Type'][0]
            json_object["prefilled"]['print_sequence'] = paycode_data['Udskrivnings sekvens'][0]
            json_object["text_fields"]['input'] = paycode_data['Input'][0]

        except Exception as e:
            print(f"Paycode {paycode} had error {e}")
            continue
        
        # Convert the JSON object to a string
        json_data = json.dumps(json_object,ensure_ascii=False)
        
        # Generate a unique key for each JSON object
        key = f'paycode_{paycode}.json'
        
        # Upload the JSON object to S3
        s3.put_object(Body=json_data, Bucket=bucket_name, Key=key)


        json_data = json.dumps(json_object,ensure_ascii=False)
        
        # Generate a unique key for each JSON object
        key = f'paycode_{paycode}.json'
        
        # Upload the JSON object to S3
        s3.put_object(Body=json_data, Bucket=bucket_name, Key=key)





create_json_objects_and_upload_to_s3(paycodes, bucket_name,paycode_template,paycode_df=paycode_df)