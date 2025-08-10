import sys
import os
from deepdiff import DeepDiff

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lambda_function import lambda_handler

def test_lambda_invocation():
    url = 'http://localhost:9999/2015-03-31/functions/function/invocations'
    input_event = {
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
    actual_response = lambda_handler(input_event, None)
    expected_response = {
        "predictions": [
            {
                "statusCode": 200,
                "model": "ride_duration_prediction_test",
                "version": "70123647ea1f49a2889fcff4d7032960",
                "prediction": {
                    "ride_id": 123,
                    "predicted_duration": 41.28146743774414
                }
            }
        ]
    }
    diff = DeepDiff(actual_response, expected_response, significant_digits=1)
    assert 'type_changes' not in diff
    assert 'values_changed' not in diff
    assert actual_response == expected_response # catch-all for any other mismatches that might be keyed differently


if __name__ == "__main__":
    try:
        test_lambda_invocation()
        print("Docker tests passed!")
    except AssertionError as e:
        print(f"Docker tests failed assertion: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while u: {e}")
        sys.exit(1)