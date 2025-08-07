# NYC Taxi Trip Duration Prediction - MLOps Pipeline

A complete MLOps pipeline for predicting NYC taxi trip duration using XGBoost, with real-time inference via AWS Lambda and Kinesis.

## Architecture Overview

This project implements an end-to-end machine learning pipeline that follows the workflow: **train → package → deploy → inference**, with experiment tracking via MLflow and real-time predictions through AWS Lambda + Kinesis.

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐    ┌──────────────┐
│   Training      │───▶│   MLflow     │───▶│     Docker      │───▶│   AWS Lambda │
│   Pipeline      │    │  Tracking    │    │  Containerization│    │  + Kinesis   │
└─────────────────┘    └──────────────┘    └─────────────────┘    └──────────────┘
```

## Project Structure

```
├── duration-prediction.py    # Training script with MLflow integration
├── lambda_function.py        # Lambda function for inference endpoint
├── Dockerfile               # Multi-stage container build
├── requirements.txt         # Python dependencies
├── data/                    # Training data and outputs
│   ├── green_tripdata_*.csv # Locally cached NYC taxi trip data (cached)
│   └── training_outputs/    # Model predictions and analysis
├── models/                  # Locally cached models
└── tests/                   # Unit and integration tests
```

## Features

### Training Pipeline (`duration-prediction.py`)

- **Data Management**: Automatically downloads and caches NYC taxi trip data
- **Feature Engineering**: Creates composite pickup-dropoff location features
- **Model Training**: XGBoost with pre-tuned hyperparameters
- **Experiment Tracking**: Full MLflow integration with metrics and artifacts
- **Validation**: Time-series split (train on month N, validate on N+1)

### Real-time Inference (`lambda_function.py`)

- **Event Processing**: Handles AWS Kinesis stream events
- **Model Loading**: Loads pre-trained models from S3 MLflow artifacts
- **Feature Preprocessing**: Uses saved scikit-learn DictVectorizer
- **Output Publishing**: Sends predictions to Kinesis output stream

### Containerization (`Dockerfile`)

- **Multi-stage Build**: Optimized for AWS Lambda deployment
- **Dependency Management**: Pre-built packages for faster cold starts
- **Runtime Optimization**: Minimal runtime image with Lambda base

## Getting Started

### Prerequisites

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### Complete Local Training + Docker Testing Flow

#### 1. Start MLflow Server

```bash
# Start MLflow server with S3 artifact store
mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root s3://mlops-learning-madamski/
```

#### 2. Train Model

```bash
# Train model on January 2022 data (validates on February 2022)
# Artifacts automatically uploaded to S3 via MLflow
python duration-prediction.py --year 2022 --month 1
```

#### 3. Update Environment Variables (if needed)

```bash
# Get the new run_id from MLflow UI or training output
export RUN_ID=new_run_id_from_training
export MODEL_ID=new_model_id_from_mlflow
```

#### 4. Build and Test Docker

```bash
# Build Docker image
docker build -t ride-prediction-service:v1 .

# Run container with environment variables
docker run --env-file .env -p 8080:8080 ride-prediction-service:v1

# Or run with specific environment variables
docker run -p 8080:8080 \
  -e RUN_ID=$RUN_ID \
  -e MODEL_ID=$MODEL_ID \
  -e TEST_RUN=true \
  ride-prediction-service:v1
```

#### 5. Test Inference

```bash
# Run unit tests
pytest tests/

# Test Lambda function locally
python test.py
```

### View MLflow Experiments

```bash
# Navigate to MLflow UI to view experiments, metrics, and artifacts
# Open browser to: http://localhost:5000
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PREDICTIONS_STREAM_NAME` | Kinesis output stream | `ride-predictions` |
| `RUN_ID` | MLflow run ID for model artifacts | `70123647ea1f49a2889fcff4d7032960` |
| `MODEL_ID` | MLflow model registry ID | `m-b312b4c1155a4197af44793c03b32ad4` |
| `TEST_RUN` | Skip Kinesis publishing for testing | `False` |

### MLflow Configuration

Currently configured for local development:
```python
TRACKING_SERVER_URI = 'http://localhost:5000'
```

For production, update to use remote MLflow server or S3 backend.


### Input Data
- **Source**: NYC Taxi & Limousine Commission open data
- **Format**: Parquet files from `d37ci6vzurychx.cloudfront.net`
- **Features**: Pickup/dropoff locations, trip distance, timestamps
- **Target**: Trip duration (filtered to 1-60 minutes)

## Dependencies

```
scikit-learn==1.6.1
boto3==1.40.1
mlflow==3.1.4
xgboost==3.0.3
pandas==2.2.3
numpy==2.1.3
pytest==8.4.1
```

## License

This project is for educational purposes as part of MLOps learning.