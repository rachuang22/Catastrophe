#!flask/bin/python
from flask import Flask, jsonify, abort, request, make_response, url_for
from flask import render_template, redirect
import boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime, timedelta

AWS_KEY="AKIAIDYW3QB6YVXKURVQ"
AWS_SECRET="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"
REGION="us-east-2"

dynamodb = boto3.resource('dynamodb', aws_access_key_id=AWS_KEY,
                            aws_secret_access_key=AWS_SECRET,
                            region_name=REGION)

table = dynamodb.Table('CatStats')

# Create the application
app = Flask(__name__, static_url_path="")

# Homepage
@app.route('/', methods=['GET','POST'])
def index():
    #if user verifies image
    if request.method == 'POST': 
        # check if user agrees with alg.
        correct = request.form['userInput']
        # if request.form['cat'] == "not":
        #     if request.form['userInput'] == "False":
        #             correct = "True"
        #     elif request.form['cat'] == "":
        #         if request.form['userInput'] == "True":
        #             correct = "True"

        # convert cat "not" input into string bool
        cat = request.form['cat']
        if cat == "not":
            cat = "False"
        else:
            cat = "True"

        # if original alg. is wrong, change cat value to opposite
        if correct == "False":
            if cat == "True":
                cat = "False"
            elif cat == "False":
                cat = "True"

        response = table.update_item(
            ExpressionAttributeNames={
                '#CAT': 'cat',
                '#COR': 'correct',
            },
            ExpressionAttributeValues={
                ':cat': cat,
                ':cor': correct,
            },
            Key={
                'url': request.form['url']
            },
            UpdateExpression='SET #CAT = :cat, #COR = :cor'
        )
        return render_template('index.html')
    else:
        timeRange = str(datetime.utcnow() - timedelta(hours = 4)).split(".")[0] # Time now minus 4 hours

        # Timestamp format example: 2018-09-28 15:57:51, timestamp in db is in UTC
        response = table.scan(
            FilterExpression=Attr('Timestamp').gt(timeRange) # string is temporary, use timeRange
        )

        items = response['Items'] # grab most recent entry
        
        fetchedTimestamp = datetime.strptime(items[0]['Timestamp'], '%Y-%m-%dT%H:%M:%S+00:00')
        print timeRange
        cat = ""
        if items[0]['cat'] == "False":
            cat = "not"

        verif = "not"
        if 'correct' in items[0]:
            verif = ""

        return render_template('index.html', url = items[0]['url'], cat = cat, timestamp = fetchedTimestamp, verified = verif)

if __name__ == '__main__':
    app.run(debug=True, port=5000)