import os
import json
import boto3
import base64
import pandas as pd
import pickle

import mlflow


def get_model_location(run_id, model_id):
    model_location = f's3://mlops-learning-madamski/1/models/{model_id}/artifacts'
    preprocessor_location = f's3://mlops-learning-madamski/1/{run_id}/artifacts/preprocessor/preprocessor.b'
    return model_location, preprocessor_location

def load_model(run_id, model_id):
    model_location, preprocessor_location = get_model_location(run_id, model_id)    
    model = mlflow.pyfunc.load_model(model_location)
    local_path_to_preproc = mlflow.artifacts.download_artifacts(preprocessor_location)
    with open(local_path_to_preproc, 'rb') as f:
        preprocessor = pickle.load(f)
    return model, preprocessor

def base64_decode(encoded_data):
    decoded_data = base64.b64decode(encoded_data).decode('utf-8')
    return json.loads(decoded_data)


class ModelService():
    
    def __init__(self, model, preprocessor, run_id, model_id, test_run, callbacks=None):
        self.model = model
        self.preprocessor = preprocessor
        self.run_id = run_id
        self.model_id = model_id
        self.test_run = test_run
        self.callbacks = callbacks or []
    
    def process_features(self, ride):
        processed_features = self.preprocessor.transform(ride)
        return processed_features

    def predict(self, features):
        pred = self.model.predict(features)
        return float(pred[0])
    
    def lambda_handler(self, event):
        
        predictions = []

        for record in event['Records']:
            encoded_data = record['kinesis']['data']
            ride_event = base64_decode(encoded_data)
            
            ride_data = ride_event['ride']
            ride_id = ride_event['ride_id']

            features = self.process_features(ride_data)
            prediction = self.predict(features)

            prediction_event = {
                    'statusCode': 200,
                    'model': 'ride_duration_prediction_test',
                    'version': self.run_id,
                    'prediction': {
                        'ride_id': ride_id,
                        'predicted_duration': prediction
                    }
                }
            
            for callback in self.callbacks:
                callback(prediction_event)
                
            predictions.append(prediction_event)
                
        output = {
            'predictions': predictions
        }

        return output

class KinesisCallback():
    
    def __init__(
            self,
            kinesis_client,
            prediction_stream_name
        ):
        self.prediction_stream_name = prediction_stream_name
        self.kinesis_client = kinesis_client
        
        
    def put_record(self, prediction_event):
        
        ride_id = prediction_event['prediction']['ride_id']
        self.kinesis_client.put_record(
            StreamName=self.prediction_stream_name,
            Data=json.dumps(prediction_event),
            PartitionKey=str(ride_id)
        )


def init(prediction_stream_name:str, run_id:str, model_id:str, test_run:bool):
    
    callbacks = []
    
    if not test_run:
        kinesis_client = boto3.client('kinesis')
        kinesis_callback = KinesisCallback(kinesis_client, prediction_stream_name)
        callbacks.append(kinesis_callback.put_record)
        
    if test_run:
        model, preprocessor = None, None
    else:
        model, preprocessor = load_model(run_id, model_id)
        
    model_service = ModelService(model, preprocessor, run_id, model_id, test_run, callbacks)
    return model_service