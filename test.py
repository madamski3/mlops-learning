import requests

ride = {
    "PULocationID": 20,
    "DOLocationID": 24,
    "trip_distance": 20
}

event = {
    "Records": [
        {
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "1",
                "sequenceNumber": "49665671746834757094076188744155022966828126471987396610",
                "data": "ewogICAgICAicmlkZSI6IHsKICAgICAgICAgICJQVUxvY2F0aW9uSUQiOiAyMCwKICAgICAgICAgICJET0xvY2F0aW9uSUQiOiAyNCwKICAgICAgICAgICJ0cmlwX2Rpc3RhbmNlIjogMjAKICAgICAgfSwKICAgICAgInJpZGVfaWQiOiAxMjMKICB9",
                "approximateArrivalTimestamp": 1753907935.119
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49665671746834757094076188744155022966828126471987396610",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::891612547191:role/lambda-kinesis-role",
            "awsRegion": "us-east-2",
            "eventSourceARN": "arn:aws:kinesis:us-east-2:891612547191:stream/ride-events"
        }
    ]
}

# url = 'http://localhost:9696/predict'
url = 'http://localhost:8080/2015-03-31/functions/function/invocations'

response = requests.post(url=url, json=event)

# Check response details
print(f"Status Code: {response.status_code}")
print(f"Response Headers: {response.headers}")
print(f"Raw Response Text: '{response.text}'")
print(f"Response Length: {len(response.text)}")

# Only try to parse JSON if we got a successful response with content
if response.status_code == 200 and response.text.strip():
    try:
        print("JSON Response:", response.json())
    except requests.exceptions.JSONDecodeError as e: 
        print(f"JSON decode error: {e}")
else:
    print("No valid JSON response received")

# features = predict.process_features(ride)
# pred = predict.predict(features)
# print(pred)