#!/usr/bin/env bash

if [[ -z "${GITHUB_ACTIONS}" ]]; then
    cd "$(dirname "$0")"
fi

LOCAL_TAG=`date +"%Y-%m-%d_%H%M"`
export LOCAL_IMAGE_NAME="ride-prediction-service-dev:${LOCAL_TAG}"
export LOCAL_KINESIS_ENDPOINT="http://localhost:4566/"
export PREDICTIONS_STREAM_NAME='ride-predictions'
export SHARD_ID='shardId-000000000000'


# Clean up existing compose containers and any processes on port 9999
echo "Cleaning up port 9999..."
docker stop $(docker ps -q --filter "publish=9999") 2>/dev/null || true
lsof -ti:9999 | xargs kill -9 2>/dev/null || true
sleep 1

# Build image and push it to a container on port 9999
echo "Building image and pushing to container..."
docker build -t ${LOCAL_IMAGE_NAME} ..
docker-compose up -d
sleep 5

# Wait for LocalStack to be ready and create Kinesis stream
echo "Creating local Kinesis stream..."
aws --endpoint-url ${LOCAL_KINESIS_ENDPOINT} \
    kinesis create-stream \
    --stream-name ${PREDICTIONS_STREAM_NAME} \
    --shard-count 1
sleep 2

# Source conda and activate mlops environment
eval "$(conda shell.bash hook)"
conda activate mlops

# Verify we're in the right environment
echo "Active conda environment: $CONDA_DEFAULT_ENV"

# Source environment variables
set -a  # automatically export all variables
source ../.env
set +a

# Run the Docker integration tests and log any error codes
echo "Running Docker integration tests..."
python test_docker.py
ERROR_CODE=$?
if [ ${ERROR_CODE} != 0 ]; then
    docker-compose logs
    docker-compose down
    exit ${ERROR_CODE}
fi

# Run the Kinesis integration tests and log any error codes
echo "Running Kinesis integration tests..."
python test_kinesis.py
ERROR_CODE=$?
if [ ${ERROR_CODE} != 0 ]; then
    docker-compose logs
    docker-compose down
    exit ${ERROR_CODE}
fi

echo "All tests successful!"
docker-compose down
