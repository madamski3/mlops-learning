import os
import json
import base64
import pytest
from scipy import sparse
from unittest.mock import patch, MagicMock
import model


def test_prepare_features():
    # Mock the preprocessor to avoid None error
    mock_preprocessor = MagicMock()
    mock_preprocessor.transform.return_value = sparse.csr_matrix([[1, 0, 1] + [0] * 5000])
    
    model_service = model.ModelService(None, mock_preprocessor, "test-run-id", "test-model-id", True)
    
    ride_data = {
        "PU_DO": "43_151",
        "trip_distance": 18.4
    }
       
    actual_features = model_service.process_features(ride_data)
    
    rows, dims = actual_features.shape
    nonzero_count = actual_features.nnz
    expected_nonzero = 2
    
    assert nonzero_count == expected_nonzero, f"Expected {expected_nonzero} non-zero values, got {nonzero_count}"
    assert sparse.issparse(actual_features), "Output should be a sparse matrix"
    assert rows == 1, "Should have exactly 1 row"
    assert dims > 5000, "Expected more dimensions (>5k)"
        
    # Test that same input gives consistent outputs
    features1 = model_service.process_features(ride_data)
    features2 = model_service.process_features(ride_data)
    assert (features1 != features2).nnz == 0, "Same input gives inconsistent outputs"


def test_predict_returns_float():
    """Test that predict function returns a float value"""
    mock_model = MagicMock()
    mock_model.predict.return_value = [15.5]
    mock_preprocessor = MagicMock()
    mock_preprocessor.transform.return_value = sparse.csr_matrix([[1, 0, 1] + [0] * 100])
    
    model_service = model.ModelService(mock_model, mock_preprocessor, "test-run-id", "test-model-id", True)
    ride_data = {"PU_DO": "43_151", "trip_distance": 18.4}
    features = model_service.process_features(ride_data)
    prediction = model_service.predict(features)
    
    assert isinstance(prediction, float), f"Expected float, got {type(prediction)}"
    assert prediction > 0, "Prediction should be positive"


def test_predict_consistency():
    """Test that predict function returns consistent results for same input"""
    mock_model = MagicMock()
    mock_model.predict.return_value = [15.5]
    mock_preprocessor = MagicMock()
    mock_preprocessor.transform.return_value = sparse.csr_matrix([[1, 0, 1] + [0] * 100])
    
    model_service = model.ModelService(mock_model, mock_preprocessor, "test-run-id", "test-model-id", True)
    ride_data = {"PU_DO": "43_151", "trip_distance": 18.4}
    features = model_service.process_features(ride_data)
    
    prediction1 = model_service.predict(features)
    prediction2 = model_service.predict(features)
    
    assert prediction1 == prediction2, "Same input should produce same prediction"


def test_lambda_handler_single_record():
    """Test lambda_handler with single Kinesis record using base64_decode"""
    mock_model = MagicMock()
    mock_model.predict.return_value = [15.5]
    mock_preprocessor = MagicMock()
    mock_preprocessor.transform.return_value = sparse.csr_matrix([[1, 0, 1] + [0] * 100])
    
    model_service = model.ModelService(mock_model, mock_preprocessor, "test-run-id", "test-model-id", True)
    
    ride_data = {"PU_DO": "43_151", "trip_distance": 18.4}
    ride_event = {"ride": ride_data, "ride_id": "test_ride_123"}
    
    # Create encoded data and verify it decodes correctly with base64_decode
    encoded_data = base64.b64encode(json.dumps(ride_event).encode('utf-8')).decode('utf-8')
    decoded_data = model.base64_decode(encoded_data)
    assert decoded_data == ride_event
    
    event = {
        'Records': [{
            'kinesis': {
                'data': encoded_data
            }
        }]
    }
    
    with patch.dict(os.environ, {'TEST_RUN': 'true'}):
        result = model_service.lambda_handler(event)
    
    assert 'predictions' in result
    assert len(result['predictions']) == 1
    assert result['predictions'][0]['prediction']['ride_id'] == 'test_ride_123'
    assert 'predicted_duration' in result['predictions'][0]['prediction']


def test_lambda_handler_multiple_records():
    """Test lambda_handler with multiple Kinesis records using base64_decode"""
    mock_model = MagicMock()
    mock_model.predict.return_value = [15.5]
    mock_preprocessor = MagicMock()
    mock_preprocessor.transform.return_value = sparse.csr_matrix([[1, 0, 1] + [0] * 100])
    
    model_service = model.ModelService(mock_model, mock_preprocessor, "test-run-id", "test-model-id", True)
    
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
        assert prediction['prediction']['ride_id'] == f'test_ride_{i}'


def test_process_features_missing_fields():
    """Test process_features with missing required fields"""
    mock_preprocessor = MagicMock()
    mock_preprocessor.transform.side_effect = KeyError("trip_distance")
    
    model_service = model.ModelService(None, mock_preprocessor, "test-run-id", "test-model-id", True)
    incomplete_ride = {"PU_DO": "43_151"}  # missing trip_distance
    
    with pytest.raises(KeyError):
        model_service.process_features(incomplete_ride)


def test_lambda_handler_invalid_json():
    """Test lambda_handler with invalid JSON data"""
    mock_model = MagicMock()
    mock_preprocessor = MagicMock()
    model_service = model.ModelService(mock_model, mock_preprocessor, "test-run-id", "test-model-id", True)
    
    invalid_data = base64.b64encode("invalid json".encode('utf-8')).decode('utf-8')
    event = {'Records': [{'kinesis': {'data': invalid_data}}]}
    
    with pytest.raises(json.JSONDecodeError):
        model_service.lambda_handler(event)


def test_lambda_handler_missing_ride_fields():
    """Test lambda_handler with missing ride or ride_id fields"""
    mock_model = MagicMock()
    mock_preprocessor = MagicMock()
    model_service = model.ModelService(mock_model, mock_preprocessor, "test-run-id", "test-model-id", True)
    
    incomplete_event = {"ride_id": "test_123"}  # missing 'ride'
    
    # Use base64_decode to verify the data can be decoded, even though it's incomplete
    encoded_data = base64.b64encode(json.dumps(incomplete_event).encode('utf-8')).decode('utf-8')
    decoded_data = model.base64_decode(encoded_data)
    assert decoded_data == incomplete_event
    
    event = {'Records': [{'kinesis': {'data': encoded_data}}]}
    
    with pytest.raises(KeyError):
        model_service.lambda_handler(event)


def test_process_features_negative_trip_distance():
    """Test process_features with negative trip distance"""
    mock_preprocessor = MagicMock()
    mock_preprocessor.transform.return_value = sparse.csr_matrix([[1, 0, -1] + [0] * 100])
    
    model_service = model.ModelService(None, mock_preprocessor, "test-run-id", "test-model-id", True)
    ride_data = {"PU_DO": "43_151", "trip_distance": -5.0}
    features = model_service.process_features(ride_data)
    
    # Should still process but may affect prediction quality
    assert sparse.issparse(features)
    assert features.shape[0] == 1


def test_prediction_event_structure():
    """Test that prediction event has correct structure using base64_decode"""
    mock_model = MagicMock()
    mock_model.predict.return_value = [15.5]
    mock_preprocessor = MagicMock()
    mock_preprocessor.transform.return_value = sparse.csr_matrix([[1, 0, 1] + [0] * 100])
    
    model_service = model.ModelService(mock_model, mock_preprocessor, "70123647ea1f49a2889fcff4d7032960", "test-model-id", True)
    
    ride_data = {"PU_DO": "43_151", "trip_distance": 18.4}
    ride_event = {"ride": ride_data, "ride_id": "test_ride_123"}
    
    # Use base64_decode to verify encoding/decoding works correctly
    encoded_data = base64.b64encode(json.dumps(ride_event).encode('utf-8')).decode('utf-8')
    decoded_result = model.base64_decode(encoded_data)
    assert decoded_result == ride_event
    
    event = {'Records': [{'kinesis': {'data': encoded_data}}]}
    
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
    """Test base64_decode function with static encoded input"""
    # Static base64 encoded string for {"PU_DO": "43_151", "trip_distance": 18.4}
    encoded_input = "eyJQVV9ETyI6ICI0M18xNTEiLCAidHJpcF9kaXN0YW5jZSI6IDE4LjR9"
    
    expected_output = {
        "PU_DO": "43_151",
        "trip_distance": 18.4
    }
    
    # Test the decode function
    result = model.base64_decode(encoded_input)
    
    # Verify the result matches expected output
    assert result == expected_output
    assert result["PU_DO"] == "43_151"
    assert result["trip_distance"] == 18.4


def test_base64_decode_with_ride_event():
    """Test base64_decode function with complete ride event structure"""
    ride_data = {
        "PU_DO": "43_151",
        "trip_distance": 18.4
    }
    ride_event = {
        "ride": ride_data,
        "ride_id": "test_ride_456"
    }
    
    # Encode the complete ride event
    encoded_data = base64.b64encode(json.dumps(ride_event).encode('utf-8')).decode('utf-8')
    
    # Test the decode function
    decoded_result = model.base64_decode(encoded_data)
    
    # Verify the decoded result matches the original
    assert decoded_result == ride_event
    assert decoded_result["ride"]["PU_DO"] == "43_151"
    assert decoded_result["ride"]["trip_distance"] == 18.4
    assert decoded_result["ride_id"] == "test_ride_456"
    