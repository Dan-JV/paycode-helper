import boto3
import random
import datetime
import streamlit as st
import json
from io import BytesIO
import polars as pl

# S3 config
s3 = boto3.client("s3")
template_bucket = "paycodehelper-templates"
processing_bucket = "paycodehelper-processing"
documented_bucket = "paycodehelper-documented"
lock_timeout = datetime.timedelta(minutes=30)

extras_bucket = "paycodehelper-extras"
leaderboard_file = "leaderboard.json"


@st.cache_data
def load_streamlit_template():
    with open("paycode_input_template.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    return data


def list_available_paycodes(bucket: str) -> list:
    paginator = s3.get_paginator("list_objects_v2")
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
        s3.copy_object(
            Bucket="paycodehelper-templates",
            CopySource={"Bucket": "paycodehelper-processing", "Key": paycode},
            Key=paycode,
        )
        s3.delete_object(Bucket="paycodehelper-processing", Key=paycode)


def move_paycode_from_source_to_target(
    source_bucket: str, target_bucket: str, paycode: str
):
    s3.copy_object(
        Bucket=target_bucket,
        CopySource={"Bucket": source_bucket, "Key": paycode},
        Key=paycode,
    )
    s3.delete_object(Bucket=source_bucket, Key=paycode)


def add_to_streamlit_session_state(name: str):
    def wrapper(func, *args, **kwargs):
        result = func(*args, **kwargs)
        st.session_state[name] = result
        return result

    return wrapper


def pick_random_paycode_click():
    result = get_random_paycode(
        source_bucket="paycodehelper-templates",
        target_bucket="paycodehelper-processing",
    )
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
def get_random_paycode(source_bucket: str, target_bucket: str) -> dict:
    """Retrieves a random paycode json file from the source bucket and the moves it to processing bucket. Fianlly it deleted the file from the source bucket."""
    available_paycodes = list_available_paycodes(bucket=source_bucket)
    if not available_paycodes:
        return None
    paycode = random.choice(available_paycodes)

    # Copy the paycode to the processing bucket
    s3.copy_object(
        Bucket=target_bucket,
        CopySource={"Bucket": source_bucket, "Key": paycode},
        Key=paycode,
    )

    # Get the paycode json file from the processing bucket and load it as a dictionary
    paycode_json_string = s3.get_object(Bucket=target_bucket, Key=paycode)
    paycode_json = json.loads(paycode_json_string.get("Body").read().decode("utf-8"))

    # Delete the paycode from the source bucket
    # s3.delete_object(Bucket=source_bucket, Key=paycode)

    # return the paycode json file
    return paycode_json


@st.cache_data
def read_leaderboard():
    try:
        obj = s3.get_object(Bucket=extras_bucket, Key=leaderboard_file)
        leaderboard = json.loads(obj["Body"].read().decode("utf-8"))
    except s3.exceptions.NoSuchKey:
        leaderboard = {}
    return leaderboard

    # try:
    #     obj = s3.get_object(Bucket=extras_bucket, Key=leaderboard_file)
    #     df = pl.read_csv(BytesIO(obj["Body"].read()))
    # except s3.exceptions.NoSuchKey:
    #     df = pl.DataFrame(columns=["name", "score"])
    # return df


def write_leaderboard(leaderboard):
    json_buffer = BytesIO(json.dumps(leaderboard).encode("utf-8"))
    s3.put_object(
        Bucket=extras_bucket, Key=leaderboard_file, Body=json_buffer.getvalue()
    )

    # csv_buffer = BytesIO()
    # df.to_csv(csv_buffer, index=False)
    # s3.put_object(
    #     Bucket=extras_bucket, Key=leaderboard_file, Body=csv_buffer.getvalue()
    # )


def update_leaderboard(user_name):
    json_file = read_leaderboard()
    leaderboard = json_file["leaderboard"]
    user_found = False
    for entry in leaderboard["leaderboard"]:
        if entry["name"] == user_name:
            entry["score"] += 1
            user_found = True
            break
    if not user_found:
        leaderboard.append({"namne": user_name, "score": 1})
    leaderboard = sorted(leaderboard, key=lambda x: x["score"], ascending=False)
    write_leaderboard(leaderboard)
