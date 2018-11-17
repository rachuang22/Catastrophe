import boto3
import pandas as pd
import json
from mapReduce import MRmyjob
import os

# ------ Set Up Credential File ------ #
# pip install configparser
# create a credentials.ini file with AWS_KEY, AWS_SECRET, REGION
from configparser import ConfigParser
config = ConfigParser()  
config.read('credentials.ini')  
AWS_KEY = str(config.get('auth', 'AWS_KEY'))
AWS_SECRET = config.get('auth', 'AWS_SECRET').encode('utf-8')
REGION = config.get('auth', 'REGION').encode('utf-8')

dynamodb = boto3.resource('dynamodb', aws_access_key_id=AWS_KEY,
                            aws_secret_access_key=AWS_SECRET,
                            region_name=REGION)
table = dynamodb.Table('CatStats')

response = table.scan()
with open('out.json', 'w') as f:
	json.dump(response['Items'], f)

df = pd.read_json("out.json")
response = df.to_csv("out.csv")

out = os.popen('python mapReduce.py out.csv').read()
out = out.splitlines()

for i in out:
	print i