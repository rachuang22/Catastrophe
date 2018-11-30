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

REGION="us-east-2"

dynamodb = boto3.resource('dynamodb', aws_access_key_id=AWS_KEY,
                            aws_secret_access_key=AWS_SECRET,
                            region_name=REGION)

table = dynamodb.Table('catastrophe')

# Create the application
app = Flask(__name__, static_url_path="")

#---------------------------------------------------------------------------------------------------------
# Homepage
@app.route('/', methods=['GET','POST'])
def index():
    #if user verifies image
    if request.method == 'POST': 

        # check if user agrees with alg.
        if request.form['userInput'] == "True":
	        entry = "Yes"
        elif request.form['userInput'] == "False":
	        entry = "No"
        print request.form
        print request.form['url']
        response = table.update_item(
            ExpressionAttributeNames={
                '#COR': 'correct'
            },
            ExpressionAttributeValues={
                ':cor': entry
            },
            Key={
                'url': request.form['url'],
                'timestamp': request.form['timestamp']
            },
            UpdateExpression='SET #COR = :cor'
        )
		
        return render_template('index.html')
    else:
        timeRange = str(datetime.utcnow() - timedelta(minutes = 30)).split(".")[0] # Time now minus 10 minutes

        # Timestamp format example: 2018-09-28 15:57:51, timestamp in db is in UTC
        response = table.scan(
            FilterExpression=Attr('timestamp').gt(timeRange) # string is temporary, use timeRange
        )
        timeList = []
        for item in response['Items']:
            timeList.append(item['timestamp'])

        maxIndex = timeList.index(max(timeList)) # index of newest fetched post

        post = response['Items'][maxIndex] # newest post data
        print post

        verif = "not"
        if 'correct' in post:
            verif = ""

        if post['object'] in Dog:
            classif = "Dog"
        elif post['object'] in Cat:
            classif = "Cat"
        elif post['object'] in Bird:
            classif = "Bird"
        elif post['object'] in Mammals:
            classif = "Mammal"
        elif post['object'] in Reptile:
            classif = "Reptile"
        elif post['object'] in Marine:
            classif = "Marine"
        elif post['object'] in Insect:
            classif = "Insect"
        elif post['object'] in Plant:
            classif = "Plant"
        elif post['object'] in Food:
            classif = "Food"
        elif post['object'] in Cloth:
            classif = "Cloth"
        elif post['object'] in Human:
            classif = "Human"
        elif post['object'] in Structure:
            classif = "Structure"
        elif post['object'] in Baby:
            classif = "Baby"
        elif post['object'] in Inanimate:
            classif = "Inanimate"
        else:
            classif = "Other"

        probability = '{:.5%}'.format(float(post['probability']))
        return render_template('index.html', name=post['url'], probability=probability, title = post['title'], permalink = post['permalink'], url = post['link'], object = post['object'], category = classif, timestamp = post['timestamp'], verified = verif)

#---------------------------------------------------------------------------------------------------------
#Database of Cute page
@app.route('/catstats', methods=['GET'])
def catdatabase():

    response = table.scan()
    data = response['Items']
    itemlist = []
    for item in data:
        entry={}
        entry['url'] = item['url']
        entry['author'] = item['author']
        entry['link'] = item['link']
        entry['object'] = item['object']
        entry['permalink'] = item['permalink']
        entry['timestamp'] = item['timestamp']
        entry['probability'] = item['probability']
        entry['title'] = item['title']
        entry['correct'] = ""
        if 'correct' in item:
            entry['correct'] = item['correct']
        else:
            entry['correct'] == "Not Sure"
        #entry['correct'] = item['correct']
        itemlist.append(entry)

    #FilterExpression=Attr('correct').eq("True") | Attr('correct').eq("False")

    return render_template('catstats.html', items=response, data=data, tablelist=itemlist)

#---------------------------------------------------------------------------------------------------------
#Verified Cute page
@app.route('/catverified', methods=['GET'])
def catverification():

    #---------------------------------------------------------------------------------------------
    # Calculations for Verification Statistics
    #---------------------------------------------------------------------------------------------
    response1 = table.scan(FilterExpression=Attr('correct').eq("Yes"))
    response2 = table.scan(FilterExpression=Attr('correct').eq("Yes") | Attr('correct').eq("No"))
    
    total_count = response1['ScannedCount']
    print total_count
    
    number_verified = response1['Count']
    print number_verified

    not_checked = total_count - response2['Count']
    print not_checked
    
    number_wrong = total_count - not_checked - number_verified
    print number_wrong
    
    not_checked_final = '%.2f'%(((float(not_checked) / total_count))*100)
    print not_checked_final
    
    alg_correct = '%.2f'%(((float(number_verified) / total_count))*100)
    print alg_correct

    alg_wrong = '%.2f'%((float(number_wrong) / total_count)*100)
    print alg_wrong
    
    #---------------------------------------------------------------------------------------------
    # MapReduce for Most Popular animal classification in the last hour
    #---------------------------------------------------------------------------------------------
    #---Retrieve posts from 24hrs ago or less
    response = table.scan(
	FilterExpression=Key('timestamp').gt(str(datetime.now() - timedelta(hours = 1)))
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
		    category1, amount1 = mr_job.parse_output_line(line)
		    print category1 + " " + str(amount1)
    
    #---------------------------------------------------------------------------------------------
    # MapReduce for Most Popular animal classification in the last 24 hours
    #---------------------------------------------------------------------------------------------
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
		    category2, amount2 = mr_job.parse_output_line(line)
		    print category2 + " " + str(amount2)

    #---------------------------------------------------------------------------------------------
    # MapReduce for Most Popular animal classification all time
    #---------------------------------------------------------------------------------------------
    #---Retrieve posts from the entire table
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
		    category3, amount3 = mr_job.parse_output_line(line)
		    counts[category3] = amount3
		    print category3 + " " + str(amount3)

    return render_template('catverified.html', total_count=total_count, number_verified=number_verified, number_wrong=number_wrong, alg_correct=alg_correct, alg_wrong=alg_wrong, alg_not_checked=not_checked_final, category1=category1, amount1=amount1, category2=category2, amount2=amount2, category3=category3, amount3=amount3)

#---------------------------------------------------------------------------------------------------------
#Aww MapReduce page
@app.route('/mapreduce', methods=['GET'])
def aww_map_reduce():
    
    #---------------------------------------------------------------------------------------------
    # MapReduce for classif object count all time
    #---------------------------------------------------------------------------------------------
    itemlist1 = []
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
        itemlist1 = []
        for line in runner.stream_output():
            entry = {}
            # Save MapReduce outputs
            category, amount = mr_job.parse_output_line(line)
            print category + " " + str(amount)
            entry['classif'] = category
            entry['amount'] = amount
            itemlist1.append(entry)

    #---------------------------------------------------------------------------------------------
    # MapReduce for classif object count all time
    #---------------------------------------------------------------------------------------------
    itemlist2 = []
    response = table.scan()
    
    # Write every post's type into txt
    with open('out.txt', 'w') as f:
        for items in response["Items"]:
            f.write(items['object'])
            f.write('\n')

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
            entry = {}
            entry['object'] = category
            entry['amount'] = amount
            entry['classif'] = classif
            itemlist2.append(entry)
            #print category + " " + str(amount) + " " + classif
    print itemlist2
    return render_template('mapreduce.html', itemlist1=itemlist1, itemlist2=itemlist2)

#---------------------------------------------------------------------------------------------------------
#Aww MapReduce for Most Popular Category page
@app.route('/mapreducepopular', methods=['GET'])
def aww_map_reduce_popular():

    #---------------------------------------------------------------------------------------------
    # MapReduce for retrieving last 100 posts for most popular category
    #---------------------------------------------------------------------------------------------

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
 
    #--- Retrieve last 100 posts for most popular category
    mostPopular = max(counts, key=counts.get)
    itemlist = []

    if mostPopular == "Dog":
        for item in response['Items']:
            if item['object'] in Dog:
                entry={}
                entry['post'] = item['link']
                entry['timestamp'] = item['timestamp']
                itemlist.append(entry)
    elif mostPopular == Cat:
        for item in response['Items']:
            if item['object'] in Cat:
                entry={}
                entry['post'] = item['link']
                entry['timestamp'] = item['timestamp']
                itemlist.append(entry)
    elif mostPopular == Bird:
        for item in response['Items']:
            if item['object'] in Bird:
                entry={}
                entry['post'] = item['link']
                entry['timestamp'] = item['timestamp']
                itemlist.append(entry)
    elif mostPopular == Mammals:
        for item in response['Items']:
            if item['object'] in Mammals:
                entry={}
                entry['post'] = item['link']
                entry['timestamp'] = item['timestamp']
                itemlist.append(entry)
    elif mostPopular == Reptile:
        for item in response['Items']:
            if item['object'] in Reptile:
                entry={}
                entry['post'] = item['link']
                entry['timestamp'] = item['timestamp']
                itemlist.append(entry)
    elif mostPopular == Marine:
        for item in response['Items']:
            if item['object'] in Marine:
                entry={}
                entry['post'] = item['link']
                entry['timestamp'] = item['timestamp']
                itemlist.append(entry)
    elif mostPopular == Insect:
        for item in response['Items']:
            if item['object'] in Insect:
                entry={}
                entry['post'] = item['link']
                entry['timestamp'] = item['timestamp']
                itemlist.append(entry)
    elif mostPopular == Plant:
        for item in response['Items']:
            if item['object'] in Plant:
                entry={}
                entry['post'] = item['link']
                entry['timestamp'] = item['timestamp']
                itemlist.append(entry)
    elif mostPopular == Food:
        for item in response['Items']:
            if item['object'] in Food:
                entry={}
                entry['post'] = item['link']
                entry['timestamp'] = item['timestamp']
                itemlist.append(entry)
    elif mostPopular == Cloth:
        for item in response['Items']:
            if item['object'] in Cloth:
                entry={}
                entry['post'] = item['link']
                entry['timestamp'] = item['timestamp']
                itemlist.append(entry)
    elif mostPopular == Human:
        for item in response['Items']:
            if item['object'] in Human:
                entry={}
                entry['post'] = item['link']
                entry['timestamp'] = item['timestamp']
                itemlist.append(entry)
    elif mostPopular == Structure:
        for item in response['Items']:
            if item['object'] in Structure:
                entry={}
                entry['post'] = item['link']
                entry['timestamp'] = item['timestamp']
                itemlist.append(entry)
    elif mostPopular == Baby:
        for item in response['Items']:
            if item['object'] in Baby:
                entry={}
                entry['post'] = item['link']
                entry['timestamp'] = item['timestamp']
                itemlist.append(entry)
    elif mostPopular == Inanimate:
        for item in response['Items']:
            if item['object'] in Inanimate:
                entry={}
                entry['post'] = item['link']
                entry['timestamp'] = item['timestamp']
                itemlist.append(entry)
    print response
    return render_template('mapreducepopular.html', itemlist=itemlist)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')