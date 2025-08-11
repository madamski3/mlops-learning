# pylint: disable=broad-exception-caught

import json
import os
import sys

import boto3
from deepdiff import DeepDiff

kinesis_endpoint = os.getenv('KINESIS_ENDPOINT_URL', 'http://localhost:4566')
kinesis_client = boto3.client('kinesis', endpoint_url=kinesis_endpoint)

predictions_stream_name = os.getenv('PREDICTIONS_STREAM_NAME', 'ride-predictions')
SHARD_ID = 'shardId-000000000000'


def test_kinesis():
    shard_iterator = kinesis_client.get_shard_iterator(
        StreamName=predictions_stream_name,
        ShardId=SHARD_ID,
        ShardIteratorType='TRIM_HORIZON',
    )
    shard_iterator_id = shard_iterator['ShardIterator']

    records_response = kinesis_client.get_records(
        ShardIterator=shard_iterator_id,
        Limit=1,
    )
    records = records_response['Records']
    assert len(records) == 1

    actual_record = json.loads(records[0]['Data'])
    expected_record = {
        "statusCode": 200,
        "model": "ride_duration_prediction_test",
        "version": "70123647ea1f49a2889fcff4d7032960",
        "prediction": {
            "ride_id": 123,
            "predicted_duration": 41.28146743774414,
        },
    }

    diff = DeepDiff(actual_record, expected_record, significant_digits=1)

    assert 'type_changes' not in diff
    assert 'values_changed' not in diff
    assert (
        actual_record == expected_record
    )  # catch-all for any other mismatches that might be keyed differently


if __name__ == "__main__":
    try:
        test_kinesis()
        print("Kinesis tests passed!")
    except AssertionError as e:
        print(f"Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
