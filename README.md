# NYC Taxi Trip Duration Prediction - MLOps Pipeline
[![CI Tests](https://github.com/madamski3/mlops-learning/actions/workflows/ci-test.yml/badge.svg)](https://github.com/madamski3/mlops-learning/actions/workflows/ci-test.yml)
[![CD Deployment](https://github.com/madamski3/mlops-learning/actions/workflows/cd-deploy.yml/badge.svg)](https://github.com/madamski3/mlops-learning/actions/workflows/cd-deploy.yml)

An end-to-end MLOps pipeline for predicting NYC taxi trip duration using XGBoost, with real-time inference via AWS Lambda and Kinesis.

**Purpose**: Educational project to learn MLOps through hands-on implementation of a production ML system.

## Architecture Overview

**train → package → deploy → inference** with MLflow experiment tracking and automated testing.

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐    ┌──────────────┐
│   Training      │───▶│   MLflow     │───▶│     Docker      │───▶│   AWS Lambda │
│   Pipeline      │    │  Tracking    │    │ Container       │    │  + Kinesis   │
└─────────────────┘    └──────────────┘    └─────────────────┘    └──────────────┘
         │                                           │                      │
         ▼                                           ▼                      ▼
┌─────────────────┐                     ┌─────────────────┐    ┌──────────────┐
│    Testing      │                     │  Integration    │    │   Real-time  │
│    Suite        │                     │    Testing      │    │  Predictions │
└─────────────────┘                     └─────────────────┘    └──────────────┘
```

## Project Structure

```
├── duration_prediction.py     # Training pipeline with MLflow
├── lambda_function.py         # AWS Lambda entry point
├── model.py                   # ML service logic
├── Dockerfile                 # Container for deployment
├── tests/                     # Unit tests
├── integration_tests/         # End-to-end testing with LocalStack
└── data/                      # Training data and outputs
```

## Key Features

### Training Pipeline
- **MLflow Experiment Tracking**: Metrics, artifacts, and model versioning
- **Feature Engineering**: Pickup-dropoff location combinations
- **Time-Series Validation**: Train on month N, validate on N+1
- **Automated Data Management**: Download and cache NYC taxi data

### Real-time Inference
- **AWS Lambda + Kinesis**: Event-driven predictions
- **Model Loading**: MLflow artifacts from S3
- **Containerized Deployment**: Multi-stage Docker build

### Testing Infrastructure
- **Unit Tests**: 15+ test functions with mocking
- **Integration Tests**: End-to-end testing with LocalStack
- **Automated Quality**: Pre-commit hooks for formatting and linting

## Getting Started

### Setup Environment
```bash
pip install -r requirements.txt
pre-commit install  # Enable code quality automation
```

### Complete Workflow

1. **Start MLflow Server**
```bash
mlflow server --backend-store-uri {AWS_EC2_INSTANCE} --default-artifact-root {AWS_S3_BUCKET}
```

2. **Train Model**
```bash
python duration_prediction.py --year 2022 --month 1
```

3. **Run Tests**
```bash
pytest tests/                    # Unit tests
./integration_tests/run.sh       # Integration tests
```

4. **Build & Test Container**
```bash
docker build -t ride-prediction-service:v1 .
docker run --env-file .env -p 8080:8080 ride-prediction-service:v1
```

## Configuration

Key environment variables:
- `RUN_ID`: MLflow run ID for model artifacts
- `MODEL_ID`: MLflow model registry ID
- `PREDICTIONS_STREAM_NAME`: Kinesis output stream name
- `TEST_RUN`: Skip Kinesis for local testing

## Data

**Source**: NYC Taxi & Limousine Commission
**Features**: Pickup/dropoff locations, trip distance
**Target**: Trip duration (1-60 minutes)
**Split**: Temporal validation (train month N, validate N+1)
