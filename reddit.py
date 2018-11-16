import praw
import boto3
from boto import kinesis
import credentials.ini


# ------ Get newest postings from Reddit ------ #
reddit = praw.Reddit(client_id='iW3F2X0p_3e9ag',
                     client_secret='ciLt6KkvKawJYzLG5wWQTzADMq0',
                     user_agent='Cloud Computing Project (catappstrophe) by sgalang3')

print(reddit.read_only)  # Output: False

for submission in reddit.subreddit('aww').new(limit=10):
    print(submission.title.encode('utf-8'))
    #print(submission.permalink) link to the page
    #print(submission.created_utc) time created
    print(submission.url) # if subdomain is https://i.redd.it/, then is a pullable image

# ------ Get newest postings from Reddit ------ #
#Connect to Kinesis Stream
client = boto3.client('kinesis', aws_access_key_id=AWS_KEY,
                            aws_secret_access_key=AWS_SECRET,
                            region_name=REGION)

print client.list_streams()

# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kinesis.html#Kinesis.Client.put_record
# response = client.put_record(
#     StreamName='Catappstrophe',
#     Data=b'bytes',
#     PartitionKey='string'
# )