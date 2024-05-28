import boto3
import random
import datetime
import streamlit as st
import json

# S3 config
s3 = boto3.client('s3')
template_bucket = 'paycodehelper-templates'
processing_bucket = 'paycodehelper-processing'
documented_bucket = 'paycodehelper-documented'
lock_timeout = datetime.timedelta(minutes=30)

def list_available_paycodes(bucket: str) -> list:
    # TODO: this only returns the top 1000 objects, need to implement pagination
    response = s3.list_objects_v2(Bucket=bucket)
    return response

def get_random_paycode(source_bucket:str,target_bucket:str) -> dict:
    """Retrieves a random paycode json file from the source bucket and the moves it to processing bucket. Fianlly it deleted the file from the source bucket."""
    available_paycodes = list_available_paycodes(bucket=source_bucket)
    if not available_paycodes:
        return None
    paycode = random.choice(available_paycodes)

    # Copy the paycode to the processing bucket
    s3.copy_object(Bucket=target_bucket, CopySource={'Bucket': source_bucket, 'Key': paycode}, Key=paycode)

    # Get the paycode json file from the processing bucket and load it as a dictionary
    paycode_json_string = s3.get_object(Bucket=target_bucket, Key=paycode)
    paycode_json = json.loads(paycode_json_string)

    # Delete the paycode from the source bucket
    s3.delete_object(Bucket=source_bucket, Key=paycode)

    #return the paycode json file
    return paycode_json

def submit_paycode(paycode):
    s3.copy_object(Bucket=bucket_name, CopySource={'Bucket': bucket_name, 'Key': paycode}, Key=paycode, Metadata={'status': 'done', 'locked_at': ''}, MetadataDirective='REPLACE')



if 'paycode' not in st.session_state:
    st.session_state.paycode = None

def get_new_paycode():
    paycode = get_random_paycode()
    if paycode:
        st.session_state.paycode = paycode
    else:
        st.warning("No available paycodes at the moment. Please try again later.")

if st.session_state.paycode is None:
    st.button("Get Random Paycode", on_click=get_new_paycode)
else:
    st.write(f"Current Paycode: {st.session_state.paycode}")
    if st.button("Submit Paycode"):
        submit_paycode(st.session_state.paycode)
        st.session_state.paycode = None
        st.success("Paycode submitted successfully!")
