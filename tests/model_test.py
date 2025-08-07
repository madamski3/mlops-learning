import lambda_function
from scipy import sparse
from lambda_function import process_features

def test_prepare_features():
    
    ride_data = {
        "PU_DO": "43_151",
        "trip_distance": 18.4
    }
       
    actual_features = process_features(ride_data)
    
    rows, dims = actual_features.shape
    nonzero_count = actual_features.nnz
    expected_nonzero = 2
    
    assert nonzero_count == expected_nonzero, f"Expected {expected_nonzero} non-zero values, got {nonzero_count}"
    assert sparse.issparse(actual_features), "Output should be a sparse matrix"
    assert rows == 1, "Should have exactly 1 row"
    assert dims > 5000, "Expected more dimensions (>5k)"
        
    # Test that same input gives consistent outputs
    features1 = process_features(ride_data)
    features2 = process_features(ride_data)
    assert (features1 != features2).nnz == 0, "Same input gives inconsistent outputs"
    