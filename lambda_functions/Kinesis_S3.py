import boto3
import base64
import json
from PIL import Image
import urllib
import io
import time

AWS_KEY=""
AWS_SECRET=""
REGION=""
BUCKET = ""

s3 = boto3.client('s3', aws_access_key_id=AWS_KEY,
                        aws_secret_access_key=AWS_SECRET)

# pass on url.jpg + image itself to s3
def my_handler(event, context):

    records = event['Records']
    url = base64.b64decode(records[0]['kinesis']['data'])

    lambda_path = urllib.urlretrieve(url)[0]

    words = url.split('/')
    newurl = ''
    for word in words:
        newurl+=('\\'+word)


    s3.upload_file(lambda_path, BUCKET, newurl[1:])
    return event


