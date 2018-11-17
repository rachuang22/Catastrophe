import boto3
from PIL import Image
import urllib.request
import io

# pass on url.jpg + image itself to s3
def my_handler(event, context):
    output = []

# getting the image from the url
with urllib.request.urlopen(URL) as url:
    f = io.BytesIO(url.read())

img = Image.open(f)

s3.put_object(Bucket=BUCKET,
              Key=url,
              Body=img)
