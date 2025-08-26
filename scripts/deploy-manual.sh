export MODEL_BUCKET_DEV='mlops-learning-madamski'
export MODEL_BUCKET_STG='ride-prediction-model-stg'
export MODEL_BUCKET_PROD='ride-prediction-model-prod'
export PREDICTION_STREAM_NAME_STG='ride-predictions-stg'
export PREDICTION_STREAM_NAME_PROD='ride-predictions-prod'
export LAMBDA_FUNCTION_STG='ride-duration-model-stg'
export LAMBDA_FUNCTION_PROD='ride-duration-model-prod'

# Set the relevant object names for deployment
export SOURCE_BUCKET=${MODEL_BUCKET_STG}
export DESTINATION_BUCKET=${MODEL_BUCKET_PROD}
export DESTINATION_STREAM_NAME=${PREDICTION_STREAM_NAME_PROD}
export DESTINATION_LAMBDA_FUNCTION=${LAMBDA_FUNCTION_PROD}

# Get the latest run_id from the dev s3 bucket
export RUN_ID=$(aws s3api list-objects-v2 --bucket ${SOURCE_BUCKET} \
--query 'sort_by(Contents[?!starts_with(Key, `1/models/`)], &LastModified)[-1].Key' --output=text | cut -f2 -d/)

# Copy the model with the designated run_id into the prod s3 bucket
aws s3 sync s3://${SOURCE_BUCKET} s3://${DESTINATION_BUCKET}

# Set new variables that will be pushed to our lambda function configuration
variables="{PREDICTIONS_STREAM_NAME=${DESTINATION_STREAM_NAME}, MODEL_BUCKET=${DESTINATION_BUCKET}, RUN_ID=${RUN_ID}}"

# Update the lambda function config with the new variables (namely, the new run_id) set previously
aws lambda update-function-configuration --function-name ${DESTINATION_LAMBDA_FUNCTION} --environment "Variables=${variables}"
