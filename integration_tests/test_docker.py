# pylint: disable=broad-exception-caught, wrong-import-position

import json
import os
import sys

from deepdiff import DeepDiff

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lambda_function import lambda_handler


def test_lambda_invocation():
    with open('input_event.json', 'r', encoding='utf-8') as f_i:
        input_event = json.load(f_i)
    actual_response = lambda_handler(input_event, None)

    with open('output_event.json', 'r', encoding='utf-8') as f_o:
        expected_response = json.load(f_o)

    diff = DeepDiff(actual_response, expected_response, significant_digits=1)
    assert 'type_changes' not in diff
    assert 'values_changed' not in diff
    assert (
        actual_response == expected_response
    )  # catch-all for any other mismatches that might be keyed differently


if __name__ == "__main__":
    try:
        test_lambda_invocation()
        print("Docker tests passed!")
    except AssertionError as e:
        print(f"Docker tests failed assertion: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
