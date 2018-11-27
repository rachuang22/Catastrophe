import praw
import boto3
import json
from datetime import datetime, timedelta

# ------ Set Up Credential File ------ #
# pip install configparser
# create a credentials.ini file with AWS_KEY, AWS_SECRET, REGION
from configparser import ConfigParser
config = ConfigParser()  
config.read('credentials.ini')  
AWS_KEY = str(config.get('auth', 'AWS_KEY'))
AWS_SECRET = config.get('auth', 'AWS_SECRET').encode('utf-8')
REGION = config.get('auth', 'REGION').encode('utf-8')

# ------ Connect to Reddit API ------ #
reddit = praw.Reddit(client_id='iW3F2X0p_3e9ag',
                     client_secret='ciLt6KkvKawJYzLG5wWQTzADMq0',
                     user_agent='Cloud Computing Project (catappstrophe) by sgalang3')

# ------ Connect to Kinesis Stream ------ #
client = boto3.client('kinesis', aws_access_key_id=AWS_KEY,
                            aws_secret_access_key=AWS_SECRET,
                            region_name=REGION)

if __name__ == '__main__':
    print ('Start: ' + str(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
    # ------ Get newest image postings from Reddit ------ #
    subreddit = reddit.subreddit('aww')
    for submission in subreddit.stream.submissions():
        if (datetime.utcnow() - timedelta(seconds=30) <= datetime.utcfromtimestamp(submission.created_utc)): # Only analyze images from past 30s+, else stream will provide previous hours' posts
            print ('----------------------------------------------------------------------')
            # https://praw.readthedocs.io/en/latest/code_overview/models/submission.html?highlight=.url
            link = submission.url # url of the image

            # ------ Logic to get only images ------ #
            # if domain is https://i.redd.it/ or https://imgur.com/, then is a pullable image
            if link[:18] == "https://i.redd.it/" or link[:18] == "https://imgur.com/" or link[:20] == 'https://i.imgur.com/':
                passData = {
                    "title": submission.title.encode('utf-8'),
                    "img-url": submission.url, # url of the image
                    "timestamp": datetime.utcfromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S'), # time created in utc
                    "author" : submission.author,
                    "num_comments" : submission.num_comments,
                    "upvotes": submission.score,
                    "upvote_ratio": submission.upvote_ratio,
                    "permalink": submission.permalink # path to the page, str
                }
                print (passData)
                
                # ------ Publish a record to Kinesis ------ #
                # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kinesis.html#Kinesis.Client.put_record
                response = client.put_record(
                    StreamName='catastrophe-images',
                    Data=json.dumps(passData),
                    PartitionKey='partitionKey1'
                )

                #print (response)
            else:
                print (submission.url)
                print ("Post is not an image!")

