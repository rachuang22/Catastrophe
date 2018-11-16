import boto3
import time

# ------ Set Up Credential File ------ #
# pip install configparser
# create a credentials.ini file with AWS_KEY, AWS_SECRET, REGION
from configparser import ConfigParser
config = ConfigParser()  
config.read('credentials.ini')  
AWS_KEY = str(config.get('auth', 'AWS_KEY'))
AWS_SECRET = config.get('auth', 'AWS_SECRET').encode('utf-8')
REGION = config.get('auth', 'REGION').encode('utf-8')

# ------ Connect to Kinesis Stream ------ #
client = boto3.client('kinesis', aws_access_key_id=AWS_KEY,
							aws_secret_access_key=AWS_SECRET,
							region_name=REGION)

streamData = client.describe_stream(StreamName='Catappstrophe')
shardID = streamData['StreamDescription']['Shards'][0]['ShardId']
shard_iterator = client.get_shard_iterator(
	StreamName='Catappstrophe',
	ShardId=shardID,
	ShardIteratorType='LATEST')
my_shard_iterator = shard_iterator['ShardIterator']

record = client.get_records(
	ShardIterator=my_shard_iterator,
	Limit=2)
print streamData['StreamDescription']['Shards'][0]
print record['Records']
while 'NextShardIterator' in record:
	print len(record['Records'])
	response = client.get_records(
		ShardIterator=record['NextShardIterator'],
		Limit=2)
	print response['Records']
	time.sleep(5) # slow processing down else will meet AWS cap

