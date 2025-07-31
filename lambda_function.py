import os
import json
import boto3
import base64
import pandas as pd
import pickle

import mlflow

kinesis_client = boto3.client('kinesis')
PREDICTIONS_STREAM_NAME = os.getenv('PREDICTIONS_STREAM_NAME', 'ride-predictions')
RUN_ID = os.getenv('RUN_ID', '28f22d8e0978455c83185318d10ea97c')
TEST_RUN = os.getenv('TEST_RUN', 'False')

logged_model = f's3://mlops-learning-madamski/1/models/m-3d67b01ef9144f3283832525bd912f4d/artifacts'
preprocessor_path = f's3://mlops-learning-madamski/1/{RUN_ID}/artifacts/preprocessor/preprocessor.b'


model = mlflow.pyfunc.load_model(logged_model)

local_preprocessor_path = mlflow.artifacts.download_artifacts(preprocessor_path)
with open(local_preprocessor_path, 'rb') as f:
    preprocessor = pickle.load(f)


def process_features(ride):
    processed_features = preprocessor.transform(ride)
    return processed_features
    
    # features = {}
    # features['PU_DO'] = '%s_%s' % (ride['PULocationID'], ride['DOLocationID'])
    # features['trip_distance'] = ride['trip_distance']
    # return features

def predict(features):
    # processed_features = preprocessor.transform([features])
    pred = model.predict(features)
    return float(pred[0])
    # features_df = pd.DataFrame([features])
    # return model.predict(features_df)

def lambda_handler(event, context):

    predictions = []

    for record in event['Records']:
        encoded_data = record['kinesis']['data']
        decoded_data = base64.b64decode(encoded_data).decode('utf-8')
        ride_event = json.loads(decoded_data)
        
        ride_data = ride_event['ride']
        ride_id = ride_event['ride_id']

        features = process_features(ride_data)
        prediction = predict(features)

        prediction_event = {
                'statusCode': 200,
                'model': 'ride_duration_prediction_test',
                'version': '1.0.1',
                'prediction': {
                    'ride_id': ride_id,
                    'predicted_duration': prediction
                }
            }
        
        if TEST_RUN.lower() != 'true':
            kinesis_client.put_record(
                StreamName=PREDICTIONS_STREAM_NAME,
                Data=json.dumps(prediction_event),
                PartitionKey=str(ride_id)
            )
             
        predictions.append(prediction_event)
    
    output = {
        'predictions': predictions
    }
    
    print(prediction_event)

    return output