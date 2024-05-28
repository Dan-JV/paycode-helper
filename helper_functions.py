import boto3
import random
import datetime
import streamlit as st
import json
import streamlit as st

# S3 config
s3 = boto3.client('s3')
template_bucket = 'paycodehelper-templates'
processing_bucket = 'paycodehelper-processing'
documented_bucket = 'paycodehelper-documented'
lock_timeout = datetime.timedelta(minutes=30)

def list_available_paycodes(bucket: str) -> list:
    paginator = s3.get_paginator('list_objects_v2')
    response_iterator = paginator.paginate(Bucket=bucket)
    
    available_paycodes = []

    for page in response_iterator:
        if "Contents" in page:
            for object in page["Contents"]:
                available_paycodes.append(object["Key"])
    return available_paycodes


def cleanup_inprocessing_bucket():
    # move objects to other bucket and delete the bucket
    available_paycodes = list_available_paycodes(bucket="paycodehelper-processing")
    for paycode in available_paycodes:
        s3.copy_object(Bucket="paycodehelper-templates", CopySource={'Bucket': 'paycodehelper-processing', 'Key': paycode}, Key=paycode)
        s3.delete_object(Bucket="paycodehelper-processing", Key=paycode)

def move_paycode_from_source_to_target(source_bucket: str, target_bucket: str, paycode: str):
    s3.copy_object(Bucket=target_bucket, CopySource={'Bucket': source_bucket, 'Key': paycode}, Key=paycode)
    s3.delete_object(Bucket=source_bucket, Key=paycode)



def add_to_streamlit_session_state(name: str):
    def wrapper(func, *args, **kwargs):
        result = func(*args, **kwargs)
        st.session_state[name] = result
        return result
    return wrapper


def pick_random_paycode_click():
    result = get_random_paycode(source_bucket="paycodehelper-templates", target_bucket="paycodehelper-processing")
    st.session_state.paycode = result


def add_to_streamlit_session_state(name: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            st.session_state[name] = result
            return result
        return wrapper
    return decorator


@add_to_streamlit_session_state(name="paycode")
def get_random_paycode(source_bucket:str, target_bucket:str) -> dict:
    """Retrieves a random paycode json file from the source bucket and the moves it to processing bucket. Fianlly it deleted the file from the source bucket."""
    available_paycodes = list_available_paycodes(bucket=source_bucket)
    if not available_paycodes:
        return None
    paycode = random.choice(available_paycodes)

    # Copy the paycode to the processing bucket
    s3.copy_object(Bucket=target_bucket, CopySource={'Bucket': source_bucket, 'Key': paycode}, Key=paycode)

    # Get the paycode json file from the processing bucket and load it as a dictionary
    paycode_json_string = s3.get_object(Bucket=target_bucket, Key=paycode)
    paycode_json = json.loads(paycode_json_string.get("Body").read().decode("utf-8"))

    # Delete the paycode from the source bucket
    s3.delete_object(Bucket=source_bucket, Key=paycode)

    #return the paycode json file
    return paycode_json

