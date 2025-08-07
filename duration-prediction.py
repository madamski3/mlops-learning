#!/usr/bin/env python
# coding: utf-8

import pickle
from pathlib import Path

import pandas as pd
import xgboost as xgb

from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import root_mean_squared_error

import mlflow

# TRACKING_SERVER_URI='s3://mlops-learning-madamski/artifacts/'
TRACKING_SERVER_URI='http://localhost:5000'

mlflow.set_tracking_uri(TRACKING_SERVER_URI)
mlflow.set_experiment("nyc-taxi-experiment")

models_folder = Path('models')
models_folder.mkdir(exist_ok=True)

data_folder = Path('data')
data_folder.mkdir(exist_ok=True)

training_outputs_folder = Path('data/training_outputs')
training_outputs_folder.mkdir(exist_ok=True)


def read_dataframe(year, month):
    file_path = f'./data/green_tripdata_{year}-{month:02d}.csv'
    url = f'https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_{year}-{month:02d}.parquet'
    
    if Path(file_path).exists():
        print(f"Dataset already cached. Reading from local storage...")
        df = pd.read_csv(file_path)
    else:
        print(f"Downloading dataset from URL...")
        df = pd.read_parquet(url)

        df['duration'] = df.lpep_dropoff_datetime - df.lpep_pickup_datetime
        df.duration = df.duration.apply(lambda td: td.total_seconds() / 60)

        df = df[(df.duration >= 1) & (df.duration <= 60)]

        categorical = ['PULocationID', 'DOLocationID']
        df[categorical] = df[categorical].astype(str)

        df['PU_DO'] = df['PULocationID'] + '_' + df['DOLocationID']
        
        df.to_csv(file_path)

    return df


def create_X(df, dv=None):
    categorical = ['PU_DO']
    numerical = ['trip_distance']
    dicts = df[categorical + numerical].to_dict(orient='records')

    if dv is None:
        dv = DictVectorizer(sparse=True)
        X = dv.fit_transform(dicts)
    else:
        X = dv.transform(dicts)

    return X, dv


def train_model(X_train, y_train, X_val, y_val, dv, val_year, val_month):
    with mlflow.start_run() as run:
        train = xgb.DMatrix(X_train, label=y_train)
        valid = xgb.DMatrix(X_val, label=y_val)

        run_params = {
            'learning_rate': 0.09585355369315604,
            'max_depth': 30,
            'min_child_weight': 1.060597050922164,
            'objective': 'reg:linear',
            'reg_alpha': 0.018060244040060163,
            'reg_lambda': 0.011658731377413597,
            'seed': 42
        }
        all_params = run_params
        all_params['val_data_year'] = val_year
        all_params['val_data_month'] = val_month

        mlflow.log_params(all_params)

        booster = xgb.train(
            params=run_params,
            dtrain=train,
            num_boost_round=30,
            evals=[(valid, 'validation')],
            early_stopping_rounds=50
        )

        run_id = run.info.run_id
        
        y_pred_train = booster.predict(train)
        y_pred_val = booster.predict(valid)
        
        rmse = root_mean_squared_error(y_val, y_pred_val)
        mlflow.log_metric("rmse", rmse)
        
        # Create a simple dataset with trip_distance and predictions
        feature_names = dv.get_feature_names_out()
        trip_distance_idx = feature_names.tolist().index('trip_distance')
        
        training_dataset = pd.DataFrame({
            'trip_distance': X_train[:, trip_distance_idx].toarray().flatten(),
            'actual_duration': y_train,
            'predicted_duration': y_pred_train,
            'prediction_error': y_pred_train - y_train,
            'absolute_error': abs(y_pred_train - y_train)
        })
        validation_dataset = pd.DataFrame({
            'trip_distance': X_val[:, trip_distance_idx].toarray().flatten(),
            'actual_duration': y_val,
            'predicted_duration': y_pred_val,
            'prediction_error': y_pred_val - y_val,
            'absolute_error': abs(y_pred_val - y_val)
        })
    
        run_id = run.info.run_id
        
        predictions_file = f"./data/training_outputs/{run_id}_predictions.csv"
        validation_dataset.to_csv(predictions_file, index=False)
        print(f"Validation dataset with predictions saved to: {predictions_file}")

        # Log the predictions file as an MLflow artifact
        mlflow.log_artifact(predictions_file, artifact_path="predictions")
        
        # Log additional metrics for analysis
        mean_absolute_error = validation_dataset['absolute_error'].mean()
        median_absolute_error = validation_dataset['absolute_error'].median()
        mlflow.log_metric("mean_absolute_error", mean_absolute_error)
        mlflow.log_metric("median_absolute_error", median_absolute_error)

        with open("models/preprocessor.b", "wb") as f_out:
            pickle.dump(dv, f_out)
        mlflow.log_artifact("models/preprocessor.b", artifact_path="preprocessor")

        booster.save_model(f"models/{run_id}.json")
        mlflow.xgboost.log_model(booster, artifact_path="models_mlflow")

        return run_id


def run(year, month):
    df_train = read_dataframe(year=year, month=month)

    next_year = year if month < 12 else year + 1
    next_month = month + 1 if month < 12 else 1
    df_val = read_dataframe(year=next_year, month=next_month)

    X_train, dv = create_X(df_train)
    X_val, _ = create_X(df_val, dv)

    target = 'duration'
    y_train = df_train[target].values
    y_val = df_val[target].values

    run_id = train_model(X_train, y_train, X_val, y_val, dv, next_year, next_month)
    print(f"MLflow run_id: {run_id}")
    return run_id


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Train a model to predict taxi trip duration.')
    parser.add_argument('--year', type=int, required=True, help='Year of the data to train on')
    parser.add_argument('--month', type=int, required=True, help='Month of the data to train on')
    args = parser.parse_args()

    run_id = run(year=args.year, month=args.month)