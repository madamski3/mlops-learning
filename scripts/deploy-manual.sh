export MODEL_BUCKET_DEV='mlops-learning-madamski'
export MODEL_BUCKET_PROD='ride-prediction-model-prod'
export PREDICTION_STREAM_NAME='ride-predictions'
export LAMBDA_FUNCTION='ride-duration-model'

# Get the latest run_id from the dev s3 bucket
export RUN_ID=$(aws s3api list-objects-v2 --bucket ${MODEL_BUCKET_DEV} \
--query 'sort_by(Contents[?!starts_with(Key, `1/models/`)], &LastModified)[-1].Key' --output=text | cut -f2 -d/)

# Copy the model with the designated run_id into the prod s3 bucket
aws s3 sync s3://${MODEL_BUCKET_DEV} s3://${MODEL_BUCKET_PROD}

# Set new variables that will be pushed to our lambda function configuration
variables="{PREDICTIONS_STREAM_NAME=${PREDICTION_STREAM_NAME}, MODEL_BUCKET=${MODEL_BUCKET_PROD}, RUN_ID=${RUN_ID}}"

# Update the lambda function config with the new variables (namely, the new run_id) set previously
aws lambda update-function-configuration --function-name ${LAMBDA_FUNCTION} --environment "Variables=${variables}"
