import boto3
import random
import datetime
import streamlit as st


s3 = boto3.client('s3')
bucket_name = 'paycodehelper'
lock_timeout = datetime.timedelta(minutes=30)

def list_available_paycodes():
    response = s3.list_objects_v2(Bucket=bucket_name)
    available_paycodes = []
    for item in response.get('Contents', []):
        metadata = s3.head_object(Bucket=bucket_name, Key=item['Key'])['Metadata']
        status = metadata.get('status')
        locked_at = metadata.get('locked_at')
        if status is None or (status == 'locked' and datetime.datetime.strptime(locked_at, '%Y-%m-%d %H:%M:%S') < datetime.datetime.now() - lock_timeout):
            available_paycodes.append(item['Key'])
    return available_paycodes

def get_random_paycode():
    available_paycodes = list_available_paycodes()
    if not available_paycodes:
        return None
    paycode = random.choice(available_paycodes)
    s3.copy_object(Bucket=bucket_name, CopySource={'Bucket': bucket_name, 'Key': paycode}, Key=paycode, Metadata={'status': 'locked', 'locked_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, MetadataDirective='REPLACE')
    return paycode

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
