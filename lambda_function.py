import os

import model

PREDICTIONS_STREAM_NAME = os.getenv('PREDICTIONS_STREAM_NAME', 'ride-predictions')
RUN_ID = os.getenv('RUN_ID', '70123647ea1f49a2889fcff4d7032960')
MODEL_ID = os.getenv('MODEL_ID', 'm-b312b4c1155a4197af44793c03b32ad4')
TEST_RUN = os.getenv('TEST_RUN', 'False').lower() == 'true'

model_service = model.init(
    prediction_stream_name=PREDICTIONS_STREAM_NAME,
    run_id=RUN_ID,
    model_id=MODEL_ID,
    test_run=TEST_RUN,
)


def lambda_handler(event, _):
    return model_service.lambda_handler(event)
