import boto3
import datetime
import json
import random
import re
import streamlit as st
import yaml

from src.streamlit_utils.streamlit_utils import add_to_streamlit_session_state


# S3 config
s3 = boto3.client("s3")
template_bucket = "paycodehelper-templates"
processing_bucket = "paycodehelper-processing"
documented_bucket = "paycodehelper-documented"
feedback_bucket = "paycodehelper-feedback"
lock_timeout = datetime.timedelta(minutes=30)


def upload_yaml_object(
    s3_client, bucket_name, paycode_yaml_string, paycodenr, verbose=False
):
    key = f"paycode_{paycodenr}.yaml"
    s3_client.put_object(Body=paycode_yaml_string, Bucket=bucket_name, Key=key)
    if verbose:
        print(f"Uploaded paycode {key} to S3 bucket {bucket_name}")


@add_to_streamlit_session_state(name="paycodenr")
def get_paycodenr(paycode: str) -> str:
    return paycode.split("_")[1].split(".")[0]


def submit_paycode(paycode, key):
    s3.put_object(Body=paycode, Bucket="paycodehelper-documented", Key=key)
    s3.delete_object(Bucket="paycodehelper-processing", Key=key)
    st.write("Submitting paycode")
    st.success("Thank you!")


def list_available_paycodes(bucket: str) -> list:
    paginator = s3.get_paginator("list_objects_v2")
    response_iterator = paginator.paginate(Bucket=bucket)

    available_paycodes = []

    for page in response_iterator:
        if "Contents" in page:
            for object in page["Contents"]:
                available_paycodes.append(object["Key"])
    return available_paycodes


@add_to_streamlit_session_state(name="paycode")
def get_random_paycode(source_bucket: str, target_bucket: str) -> dict:
    """Retrieves a random paycode json file from the source bucket and the moves it to processing bucket. Fianlly it deleted the file from the source bucket."""

    available_paycodes = list_available_paycodes(bucket=source_bucket)

    if not available_paycodes:
        return None
    paycode = random.choice(available_paycodes)
    paycodenr = get_paycodenr(paycode)

    # Copy the paycode to the processing bucket
    s3.copy_object(
        Bucket=target_bucket,
        CopySource={"Bucket": source_bucket, "Key": paycode},
        Key=paycode,
    )

    # Get the paycode json file from the processing bucket and load it as a dictionary
    paycode_object = s3.get_object(Bucket=target_bucket, Key=paycode)
    paycode_string = paycode_object.get("Body").read().decode("utf-8")
    paycode_yaml = yaml.safe_load(paycode_string)

    # Delete the paycode from the source bucket
    # s3.delete_object(Bucket=source_bucket, Key=paycode_object)

    return paycode_yaml


@add_to_streamlit_session_state(name="paycode")
def get_paycode(bucket: str, key: str) -> dict:
    """Retrieves a specific paycode json from the bucket given a filename key"""
    try:
        paycode_object = s3.get_object(Bucket=bucket, Key=key)
        paycode = yaml.safe_load(paycode_object.get("Body").read().decode("utf-8"))

    except Exception as e:
        print(e)
        paycode = None

    return paycode


def cleanup_inprocessing_bucket():
    # move objects to other bucket and delete the bucket
    available_paycodes = list_available_paycodes(bucket="paycodehelper-processing")

    for paycode in available_paycodes:
        move_paycode_from_source_to_target(
            source_bucket="paycodehelper-processing",
            target_bucket="paycodehelper-templates",
            src_key=paycode,
            target_key=paycode,
        )


def move_paycode_from_source_to_target(
    source_bucket: str, target_bucket: str, src_key: str, target_key: str
):
    s3.copy_object(
        Bucket=target_bucket,
        CopySource={"Bucket": source_bucket, "Key": src_key},
        Key=target_key,
    )
    s3.delete_object(Bucket=source_bucket, Key=src_key)


def upload_feedback(feedback: dict, key: str):
    feedback_json = json.dumps(feedback, ensure_ascii=False)
    s3.put_object(Body=feedback_json, Bucket=feedback_bucket, Key=key)


def read_feedback():
    files = list_available_paycodes(bucket=feedback_bucket)
    feedback_data = {}
    for file in files:
        file_content = s3.get_object(Bucket=feedback_bucket, Key=file)
        feedback = json.loads(file_content.get("Body").read().decode("utf-8"))
        split_file_name = re.split("_|\.", file)
        file_name = f"{split_file_name[2]}_{split_file_name[3]}"

        if file_name not in feedback_data:
            feedback_data[file_name] = []
        feedback_data[file_name].append(feedback)

    return feedback_data
