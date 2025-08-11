import base64
import json
import os
from unittest.mock import MagicMock, patch

import pytest
from scipy import sparse

import model


# Factory functions for test setup
def create_mock_model(return_value=15.5):
    """Create a mock model with configurable return value"""
    mock = MagicMock()
    mock.predict.return_value = [return_value]
    return mock


def create_mock_preprocessor(feature_count=100):
    """Create a mock preprocessor with configurable feature count"""
    mock = MagicMock()
    mock.transform.return_value = sparse.csr_matrix([[1, 0, 1] + [0] * feature_count])
    return mock


def create_model_service(mock_model=None, preprocessor=None, run_id="test-run-id"):
    """Create a ModelService with sensible defaults for testing"""
    mock_model = mock_model or create_mock_model()
    mock_preprocessor = preprocessor or create_mock_preprocessor()
    return model.ModelService(mock_model, mock_preprocessor, run_id, "test-model-id", True)


def create_kinesis_event(ride_event):
    """Create a Kinesis event from a ride event dictionary"""
    encoded_data = base64.b64encode(json.dumps(ride_event).encode('utf-8')).decode('utf-8')
    return {'Records': [{'kinesis': {'data': encoded_data}}]}


def create_sample_ride_data():
    """Create standard ride data for testing"""
    return {"PU_DO": "43_151", "trip_distance": 18.4}


def create_sample_ride_event(ride_id="test_ride_123"):
    """Create standard ride event for testing"""
    return {"ride": create_sample_ride_data(), "ride_id": ride_id}


def test_prepare_features():
    model_service = create_model_service(
        mock_model=None,
        preprocessor=create_mock_preprocessor(feature_count=5000),
    )
    ride_data = create_sample_ride_data()

    actual_features = model_service.process_features(ride_data)

    rows, dims = actual_features.shape
    nonzero_count = actual_features.nnz
    expected_nonzero = 2

    assert (
        nonzero_count == expected_nonzero
    ), f"Expected {expected_nonzero} non-zero values, got {nonzero_count}"
    assert sparse.issparse(actual_features), "Output should be a sparse matrix"
    assert rows == 1, "Should have exactly 1 row"
    assert dims > 5000, "Expected more dimensions (>5k)"

    # Test that same input gives consistent outputs
    features1 = model_service.process_features(ride_data)
    features2 = model_service.process_features(ride_data)
    assert (features1 != features2).nnz == 0, "Same input gives inconsistent outputs"


def test_predict_returns_float():
    """Test that predict function returns a float value"""
    model_service = create_model_service()
    ride_data = create_sample_ride_data()
    features = model_service.process_features(ride_data)
    prediction = model_service.predict(features)

    assert isinstance(prediction, float), f"Expected float, got {type(prediction)}"
    assert prediction > 0, "Prediction should be positive"


def test_predict_consistency():
    """Test that predict function returns consistent results for same input"""
    model_service = create_model_service()
    ride_data = create_sample_ride_data()
    features = model_service.process_features(ride_data)

    prediction1 = model_service.predict(features)
    prediction2 = model_service.predict(features)

    assert prediction1 == prediction2, "Same input should produce same prediction"


def test_lambda_handler_single_record():
    """Test lambda_handler with single Kinesis record using base64_decode"""
    model_service = create_model_service()
    ride_event = create_sample_ride_event()

    # Create encoded data and verify it decodes correctly with base64_decode
    encoded_data = base64.b64encode(json.dumps(ride_event).encode('utf-8')).decode('utf-8')
    decoded_data = model.base64_decode(encoded_data)
    assert decoded_data == ride_event

    event = create_kinesis_event(ride_event)

    with patch.dict(os.environ, {'TEST_RUN': 'true'}):
        result = model_service.lambda_handler(event)

    assert len(result['predictions']) == 1
    prediction = result['predictions'][0]

    assert prediction['statusCode'] == 200
    assert prediction['model'] == 'ride_duration_prediction_test'
    assert prediction['version'] == 'test-run-id'
    assert 'prediction' in prediction
    assert prediction['prediction']['ride_id'] == 'test_ride_123'
    assert isinstance(prediction['prediction']['predicted_duration'], float)


def test_lambda_handler_multiple_records():
    """Test lambda_handler with multiple Kinesis records using base64_decode"""
    model_service = create_model_service()

    records = []
    for i in range(3):
        ride_data = {"PU_DO": f"43_{150+i}", "trip_distance": 10.0 + i}
        ride_event = {"ride": ride_data, "ride_id": f"test_ride_{i}"}

        # Create encoded data and verify base64_decode works for each record
        encoded_data = base64.b64encode(json.dumps(ride_event).encode('utf-8')).decode('utf-8')
        decoded_data = model.base64_decode(encoded_data)
        assert decoded_data == ride_event

        records.append({'kinesis': {'data': encoded_data}})

    event = {'Records': records}

    with patch.dict(os.environ, {'TEST_RUN': 'true'}):
        result = model_service.lambda_handler(event)

    assert len(result['predictions']) == 3
    for i, prediction in enumerate(result['predictions']):
        assert prediction['statusCode'] == 200
        assert prediction['model'] == 'ride_duration_prediction_test'
        assert prediction['prediction']['ride_id'] == f'test_ride_{i}'


def test_process_features_missing_fields():
    """Test process_features with missing required fields"""
    error_preprocessor = create_mock_preprocessor()
    error_preprocessor.transform.side_effect = KeyError("trip_distance")

    model_service = create_model_service(mock_model=None, preprocessor=error_preprocessor)
    incomplete_ride = {"PU_DO": "43_151"}  # missing trip_distance

    with pytest.raises(KeyError):
        model_service.process_features(incomplete_ride)


def test_lambda_handler_invalid_json():
    """Test lambda_handler with invalid JSON data"""
    model_service = create_model_service()

    invalid_data = base64.b64encode("invalid json".encode('utf-8')).decode('utf-8')
    event = {'Records': [{'kinesis': {'data': invalid_data}}]}

    with pytest.raises(json.JSONDecodeError):
        model_service.lambda_handler(event)


def test_lambda_handler_missing_ride_fields():
    """Test lambda_handler with missing ride or ride_id fields"""
    model_service = create_model_service()

    incomplete_event = {"ride_id": "test_123"}  # missing 'ride'

    # Use base64_decode to verify the data can be decoded, even though it's incomplete
    encoded_data = base64.b64encode(json.dumps(incomplete_event).encode('utf-8')).decode('utf-8')
    decoded_data = model.base64_decode(encoded_data)
    assert decoded_data == incomplete_event

    event = create_kinesis_event(incomplete_event)

    with pytest.raises(KeyError):
        model_service.lambda_handler(event)


def test_process_features_negative_trip_distance():
    """Test process_features with negative trip distance"""
    negative_preprocessor = create_mock_preprocessor()
    negative_preprocessor.transform.return_value = sparse.csr_matrix([[1, 0, -1] + [0] * 100])

    model_service = create_model_service(mock_model=None, preprocessor=negative_preprocessor)
    ride_data = {"PU_DO": "43_151", "trip_distance": -5.0}
    features = model_service.process_features(ride_data)

    # Should still process but may affect prediction quality
    assert sparse.issparse(features)
    assert features.shape[0] == 1


def test_prediction_event_structure():
    """Test that prediction event has correct structure using base64_decode"""
    model_service = create_model_service(run_id="70123647ea1f49a2889fcff4d7032960")
    ride_event = create_sample_ride_event()

    # Use base64_decode to verify encoding/decoding works correctly
    encoded_data = base64.b64encode(json.dumps(ride_event).encode('utf-8')).decode('utf-8')
    decoded_result = model.base64_decode(encoded_data)
    assert decoded_result == ride_event

    event = create_kinesis_event(ride_event)

    with patch.dict(os.environ, {'TEST_RUN': 'true'}):
        result = model_service.lambda_handler(event)

    prediction = result['predictions'][0]

    assert prediction['statusCode'] == 200
    assert prediction['model'] == 'ride_duration_prediction_test'
    assert prediction['version'] == '70123647ea1f49a2889fcff4d7032960'
    assert 'prediction' in prediction
    assert prediction['prediction']['ride_id'] == 'test_ride_123'
    assert isinstance(prediction['prediction']['predicted_duration'], float)


def test_base64_decode():
    """Test base64_decode function with simple data"""
    test_data = {"message": "hello", "number": 42}
    encoded = base64.b64encode(json.dumps(test_data).encode('utf-8')).decode('utf-8')

    decoded = model.base64_decode(encoded)

    assert decoded == test_data
    assert isinstance(decoded, dict)


def test_base64_decode_with_ride_event():
    """Test base64_decode function with ride event data"""
    ride_event = create_sample_ride_event()
    encoded = base64.b64encode(json.dumps(ride_event).encode('utf-8')).decode('utf-8')

    decoded = model.base64_decode(encoded)

    assert decoded == ride_event
    assert 'ride' in decoded
    assert 'ride_id' in decoded
    assert decoded['ride']['PU_DO'] == "43_151"
    assert decoded['ride']['trip_distance'] == 18.4
