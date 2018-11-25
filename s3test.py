import boto3
from random import randint
import json

AWS_KEY="###"
AWS_SECRET="###"
REGION="us-east-2"
BUCKET = "###"

s3 = boto3.client('s3', aws_access_key_id=AWS_KEY,
                        aws_secret_access_key=AWS_SECRET)

# !! How to insert metadata
s3.upload_file(
    "localfile.txt", BUCKET, "uploadedfile.txt",
    ExtraArgs={
        "Metadata": {
            "mykey": str(randint(0,100)),
            "nextkey": "niceTest"
            }
        }
    )  

s3.put_object_acl(ACL='public-read', Bucket=BUCKET, Key="uploadedfile.txt")

# Reading file normally
response = s3.get_object(Bucket=BUCKET,
                         Key='uploadedfile.txt')
data = response['Body'].read()
print data 

# !! Getting file's metadata
response = s3.head_object(Bucket=BUCKET,
                         Key='uploadedfile.txt')
print response['Metadata']