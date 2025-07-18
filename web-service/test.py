import predict

import requests

ride = {
    "PULocationID": 10,
    "DOLocationID": 54,
    "trip_distance": 40
}

url = 'http://localhost:9696/predict'

response = requests.post(url=url, json=ride)

print(response.json())

# features = predict.process_features(ride)
# pred = predict.predict(features)
# print(pred)