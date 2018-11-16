import praw
import boto3
import json
from boto import kinesis
from datetime import datetime

# ------ Set Up Credential File ------ #
# pip install configparser
# create a credentials.ini file with AWS_KEY, AWS_SECRET, REGION
from configparser import ConfigParser
config = ConfigParser()  
config.read('credentials.ini')  
AWS_KEY = str(config.get('auth', 'AWS_KEY'))
AWS_SECRET = config.get('auth', 'AWS_SECRET').encode('utf-8')
REGION = config.get('auth', 'REGION').encode('utf-8')

# ------ Get newest postings from Reddit ------ #
reddit = praw.Reddit(client_id='iW3F2X0p_3e9ag',
                     client_secret='ciLt6KkvKawJYzLG5wWQTzADMq0',
                     user_agent='Cloud Computing Project (catappstrophe) by sgalang3')

for submission in reddit.subreddit('aww').new(limit=10):
	# https://praw.readthedocs.io/en/latest/code_overview/models/submission.html?highlight=.url
    link = submission.url # url of the image

    # ------ Logic to get only images ------ #
    # if subdomain is https://i.redd.it/, then is a pullable image
    if link[:18] == "https://i.redd.it/" or link[:18] == "https://imgur.com/":
	    passData = {
	    	"title": submission.title.encode('utf-8'),
	    	"img-url": submission.url, # url of the image
	    	"timestamp": datetime.utcfromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S'), # time created in utc
	    	"permalink": submission.permalink # path to the page, str
	    }
	    print (passData)
	    
	    break

# ------ Kinesis stream code ------ #
#Connect to Kinesis Stream
client = boto3.client('kinesis', aws_access_key_id=AWS_KEY,
                            aws_secret_access_key=AWS_SECRET,
                            region_name=REGION)

# print client.list_streams() # read what streams exist in client

# publish a record
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kinesis.html#Kinesis.Client.put_record
response = client.put_record(
    StreamName='Catappstrophe',
    Data=json.dumps(passData),
    PartitionKey='partitionKey1'
)

print (response)