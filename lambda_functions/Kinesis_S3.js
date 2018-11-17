const AWS = require('aws-sdk');

// Reference to S3 client
var s3 = new AWS.S3();

// Getting records form Kinesis stream
processed_records = []
for r in records:
    processed_records.append({
        'PartitionKey': str(r['source']),
        'Data': json.dumps(r),
    })

kinesis.put_records(
    StreamName=stream,
    Records=processed_records,
)

var url = //Put url retrieved from Kinesis

// // Put the resulting image to S3
exports.handler = function(event, context) {
  https.get(url, function(res) {
    var body = '';
    res.on('data', function(chunk) {
      // Agregates chunks
      body += chunk;
    });
    res.on('end', function() {
      // Once you received all chunks, send to S3
      var params = {
        Bucket: 'example',
        Key: 'aws-logo.png',
        Body: body
      };
      s3.putObject(params, function(err, data) {
        if (err) {
          console.error(err, err.stack);
        } else {
          console.log(data);
        }
      });
    });
  });
};
