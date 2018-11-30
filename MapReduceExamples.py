#!flask/bin/python
from flask import Flask, jsonify, abort, request, make_response, url_for
from flask import render_template, redirect
import boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime, timedelta
import json
from mapReduceClass import MRclassification
from mapReduceCount import MRcount
from objClasses import Dog, Cat, Bird, Mammals, Reptile, Marine, Insect, Plant, Food, Cloth, Human, Structure, Baby, Inanimate

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

table = dynamodb.Table('catastrophe')

response = table.scan()

# Write every post's type into txt
with open('out.txt', 'w') as f:
	for items in response["Items"]:
		f.write(items['object'])
		f.write('\n')

#---Run MapReduce for Classification Reduced counts
mr_job = MRclassification(args=['out.txt'])
with mr_job.make_runner() as runner:
	runner.run()
	# Keep running count of items
	counts = {}
	for line in runner.stream_output():
		# Save MapReduce outputs
		category, amount = mr_job.parse_output_line(line)
		counts[category] = amount
		#print category + " " + str(amount)
	print counts

	# get item with most frequent appearance

#--- Retrieve last 100 posts for most popular category
mostPopular = max(counts, key=counts.get)
postList = []
timeList = []
if mostPopular == "Dog":
    for item in response['Items']:
        if item['object'] in Dog:
            postList.append(item['link'])
            timeList.append(item['timestamp'])
elif mostPopular == Cat:
    for item in response['Items']:
        if item['object'] in Cat:
            postList.append(item['link'])
            timeList.append(item['timestamp'])
elif mostPopular == Bird:
    for item in response['Items']:
        if item['object'] in Bird:
            postList.append(item['link'])
            timeList.append(item['timestamp'])
elif mostPopular == Mammals:
    for item in response['Items']:
        if item['object'] in Mammals:
            postList.append(item['link'])
            timeList.append(item['timestamp'])
elif mostPopular == Reptile:
    for item in response['Items']:
        if item['object'] in Reptile:
            postList.append(item['link'])
            timeList.append(item['timestamp'])
elif mostPopular == Marine:
    for item in response['Items']:
        if item['object'] in Marine:
            postList.append(item['link'])
            timeList.append(item['timestamp'])
elif mostPopular == Insect:
    for item in response['Items']:
        if item['object'] in Insect:
            postList.append(item['link'])
            timeList.append(item['timestamp'])
elif mostPopular == Plant:
    for item in response['Items']:
        if item['object'] in Plant:
            postList.append(item['link'])
            timeList.append(item['timestamp'])
elif mostPopular == Food:
    for item in response['Items']:
        if item['object'] in Food:
            postList.append(item['link'])
            timeList.append(item['timestamp'])
elif mostPopular == Cloth:
    for item in response['Items']:
        if item['object'] in Cloth:
            postList.append(item['link'])
            timeList.append(item['timestamp'])
elif mostPopular == Human:
    for item in response['Items']:
        if item['object'] in Human:
            postList.append(item['link'])
            timeList.append(item['timestamp'])
elif mostPopular == Structure:
    for item in response['Items']:
        if item['object'] in Structure:
            postList.append(item['link'])
            timeList.append(item['timestamp'])
elif mostPopular == Baby:
    for item in response['Items']:
        if item['object'] in Baby:
            postList.append(item['link'])
            timeList.append(item['timestamp'])
elif mostPopular == Inanimate:
    for item in response['Items']:
        if item['object'] in Inanimate:
            postList.append(item['link'])
            timeList.append(item['timestamp'])
#print postList
#print timeList

#---Run MapReduce for object type count
mr_job = MRcount(args=['out.txt'])
with mr_job.make_runner() as runner:
	runner.run()
	for line in runner.stream_output():
		# Save MapReduce outputs
		category, amount = mr_job.parse_output_line(line)
		if category in Dog:
			classif = "Dog"
		elif category in Cat:
			classif = "Cat"
		elif category in Bird:
			classif = "Bird"
		elif category in Mammals:
			classif = "Mammal"
		elif category in Reptile:
			classif = "Reptile"
		elif category in Marine:
			classif = "Marine"
		elif category in Insect:
			classif = "Insect"
		elif category in Plant:
			classif = "Plant"
		elif category in Food:
			classif = "Food"
		elif category in Cloth:
			classif = "Cloth"
		elif category in Human:
			classif = "Human"
		elif category in Structure:
			classif = "Structure"
		elif category in Baby:
			classif = "Baby"
		elif category in Inanimate:
			classif = "Inanimate"
		else:
			classif = ("Other")
		#print category + " " + str(amount) + " " + classif

#---Retrieve posts from 24hrs ago or less
response = table.scan(
	FilterExpression=Key('timestamp').gt(str(datetime.now() - timedelta(hours = 24)))
	)
# Write every post's type into txt
with open('out.txt', 'w') as f:
	for items in response["Items"]:
		f.write(items['object'])
		f.write('\n')

#---Run MapReduce for Classification Reduced counts within last day
mr_job = MRclassification(args=['out.txt'])
with mr_job.make_runner() as runner:
	runner.run()
	for line in runner.stream_output():
		# Save MapReduce outputs
		category, amount = mr_job.parse_output_line(line)
		#print category + " " + str(amount)

#---Run MapReduce for object type count within last day
mr_job = MRcount(args=['out.txt'])
with mr_job.make_runner() as runner:
	runner.run()
	for line in runner.stream_output():
		# Save MapReduce outputs
		category, amount = mr_job.parse_output_line(line)
		if category in Dog:
			classif = "Dog"
		elif category in Cat:
			classif = "Cat"
		elif category in Bird:
			classif = "Bird"
		elif category in Mammals:
			classif = "Mammal"
		elif category in Reptile:
			classif = "Reptile"
		elif category in Marine:
			classif = "Marine"
		elif category in Insect:
			classif = "Insect"
		elif category in Plant:
			classif = "Plant"
		elif category in Food:
			classif = "Food"
		elif category in Cloth:
			classif = "Cloth"
		elif category in Human:
			classif = "Human"
		elif category in Structure:
			classif = "Structure"
		elif category in Baby:
			classif = "Baby"
		elif category in Inanimate:
			classif = "Inanimate"
		else:
			classif = ("Other", 1)
		#print category + " " + str(amount) + " " + classif

#---display wrong images
client = boto3.client('dynamodb', aws_access_key_id=AWS_KEY,
							aws_secret_access_key=AWS_SECRET,
							region_name=REGION)

response = client.query(
	hash_key='timestamp', ScanIndexForward=True, limit=1
	)
print response
# Write every post's type into txt
with open('out.txt', 'w') as f:
	for items in response["Items"]:
		f.write(items['object'])
		f.write('\n')



# Convert to csv
# df = pd.read_json("out.json")
# response = df.to_csv("out.csv")
