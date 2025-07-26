import predict

import requests

ride = {
    "PULocationID": 20,
    "DOLocationID": 24,
    "trip_distance": 20
}

url = 'http://localhost:9696/predict'

response = requests.post(url=url, json=ride)

print(response.json())

# features = predict.process_features(ride)
# pred = predict.predict(features)
# print(pred)