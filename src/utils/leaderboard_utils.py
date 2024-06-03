import streamlit as st
from io import BytesIO
import polars as pl
import boto3
import json

s3 = boto3.client("s3")
extras_bucket = "paycodehelper-extras"
leaderboard_file = "leaderboard.json"


def read_leaderboard():
    try:
        obj = s3.get_object(Bucket=extras_bucket, Key=leaderboard_file)
        leaderboard = json.loads(obj["Body"].read().decode("utf-8"))
    except s3.exceptions.NoSuchKey:
        leaderboard = {}
    return leaderboard


def write_leaderboard(leaderboard):
    json_buffer = BytesIO(json.dumps(leaderboard).encode("utf-8"))
    s3.put_object(
        Bucket=extras_bucket, Key=leaderboard_file, Body=json_buffer.getvalue()
    )


def update_leaderboard(user_name):
    json_file = read_leaderboard()
    leaderboard = json_file["leaderboard"]
    user_found = False
    for entry in leaderboard:
        if entry["name"] == user_name:
            entry["score"] += 1
            user_found = True
            break
    if not user_found:
        leaderboard.append({"name": user_name, "score": 1})
    leaderboard = sorted(leaderboard, key=lambda x: x["score"], reverse=True)
    json_file["leaderboard"] = leaderboard
    write_leaderboard(json_file)


# Leaderboard function
def display_leaderboard():
    leaderboard_json = read_leaderboard()
    leaderboard = leaderboard_json["leaderboard"]

    for i, entry in enumerate(leaderboard):
        if i == 0:
            medal = "🥇"
        elif i == 1:
            medal = "🥈"
        elif i == 2:
            medal = "🥉"
        else:
            medal = ""

        st.write(f"{i+1} - {medal} {entry['name']}: {entry['score']} paycodes")


# Utility function to reset the leaderboard
def reset_leaderboard():
    write_leaderboard({"leaderboard": []})
