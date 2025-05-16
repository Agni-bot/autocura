# test_integration.py - Integration Tests for Will System API

import unittest
import json
import os

# To run these tests, the Flask app (app.py) should be running.
# For a CI/CD environment, you would typically start the app as a service before running tests.
# For local testing, ensure app.py is running in a separate terminal: `python app.py` or `gunicorn ...`

# We will use the `requests` library to make HTTP calls. 
# Add it to requirements.txt if not already there (though for this test, we might mock if app is not running)
# For simplicity, these tests assume the app is running and accessible at API_BASE_URL.
# If using Flask's test_client, the setup is different.

# Let's assume we will use Flask's test_client for more controlled testing without needing a live server.
# This requires `app.py` to be importable and to have the Flask `app` instance.

# Attempt to import the Flask app instance from app.py
# This assumes app.py is in the same directory or accessible via PYTHONPATH

# Since app.py is in /home/ubuntu/will_system_enhancements/
# and this test file will be in /home/ubuntu/will_system_enhancements/tests/
# we need to adjust the Python path or structure the project as a package.

# For now, let's write tests that would use `requests` against a running server.
# If we were to use Flask's test_client, we'd need to ensure `app.py` is structured to allow importing `app`.

import requests # Add 'requests' to requirements.txt

API_BASE_URL = os.environ.get("WILL_API_URL", "http://localhost:5000/api/will")

class TestWillAPIIntegration(unittest.TestCase):

    def test_01_status_endpoint(self):
        """Test the /status endpoint for a successful response and basic structure."""
        try:
            response = requests.get(f"{API_BASE_URL}/status")
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("system_name", data)
            self.assertEqual(data["system_name"], "Will Predictive Trading System")
            self.assertIn("status", data)
            self.assertEqual(data["status"], "OPERATIONAL")
            self.assertIn("version", data)
            logger.info("Test /api/will/status PASSED")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error during /api/will/status test: {e}. Ensure the API server is running.")
            self.fail(f"API server not reachable at {API_BASE_URL}/status. {e}")
        except Exception as e:
            logger.error(f"Error during /api/will/status test: {e}")
            self.fail(f"Test /api/will/status FAILED with error: {e}")

    def test_02_decision_endpoint_valid_payload(self):
        """Test the /decision endpoint with a valid payload."""
        payload = {
            "request_id": "TEST_REQ_001",
            "timestamp": "2025-05-09T11:00:00Z",
            "source_module": "IntegrationTestRunner",
            "asset": "USD/CAD",
            "timeframe": "M15",
            "market_conditions": {
                "volatility_index": 18.2,
                "current_price": 1.3750
            },
            "requested_volume": 25000
        }
        try:
            response = requests.post(f"{API_BASE_URL}/decision", json=payload)
            response.raise_for_status()

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("trade_signal", data)
            self.assertIn("confidence_score", data)
            self.assertEqual(data["input_parameters"]["request_id"], "TEST_REQ_001")
            self.assertEqual(data["target_asset"], "USD/CAD")
            logger.info("Test /api/will/decision with valid payload PASSED")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error during /api/will/decision test: {e}. Ensure the API server is running.")
            self.fail(f"API server not reachable at {API_BASE_URL}/decision. {e}")
        except Exception as e:
            logger.error(f"Error during /api/will/decision test (valid payload): {e}")
            self.fail(f"Test /api/will/decision (valid payload) FAILED with error: {e}")

    def test_03_decision_endpoint_invalid_payload_missing_field(self):
        """Test the /decision endpoint with an invalid payload (missing required field)."""
        payload = {
            "request_id": "TEST_REQ_002",
            # "asset": "EUR/JPY", # Missing asset
            "requested_volume": 10000
        }
        try:
            response = requests.post(f"{API_BASE_URL}/decision", json=payload)
            # Expecting a 400 Bad Request or similar error based on app.py mock logic
            self.assertEqual(response.status_code, 400) # Based on get_will_decision_mock
            data = response.json()
            self.assertIn("error", data)
            self.assertEqual(data["error"], "Invalid input data") # Specific to the mock
            logger.info("Test /api/will/decision with invalid payload (missing field) PASSED")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error during /api/will/decision test (invalid payload): {e}. Ensure the API server is running.")
            self.fail(f"API server not reachable at {API_BASE_URL}/decision. {e}")
        except Exception as e:
            logger.error(f"Error during /api/will/decision test (invalid payload): {e}")
            self.fail(f"Test /api/will/decision (invalid payload) FAILED with error: {e}")

    def test_04_decision_endpoint_not_json(self):
        """Test the /decision endpoint with a non-JSON payload."""
        try:
            response = requests.post(f"{API_BASE_URL}/decision", data="not a json string", headers={"Content-Type": "text/plain"})
            self.assertEqual(response.status_code, 400)
            data = response.json()
            self.assertIn("error", data)
            self.assertEqual(data["error"], "Request must be JSON")
            logger.info("Test /api/will/decision with non-JSON payload PASSED")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error during /api/will/decision test (non-JSON): {e}. Ensure the API server is running.")
            self.fail(f"API server not reachable at {API_BASE_URL}/decision. {e}")
        except Exception as e:
            logger.error(f"Error during /api/will/decision test (non-JSON): {e}")
            self.fail(f"Test /api/will/decision (non-JSON) FAILED with error: {e}")

# --- Setup for structured logging in tests ---
import logging
from pythonjsonlogger import jsonlogger

logger = logging.getLogger("will_api_integration_tests")
logger.setLevel(logging.INFO)
# Prevent duplicate handlers if script is run multiple times in same session (e.g. in some IDEs)
if not logger.handlers:
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(module)s %(funcName)s %(lineno)d %(message)s"
    )
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)

if __name__ == "__main__":
    logger.info("Starting Will API Integration Tests...")
    # Note: These tests require the Flask server (app.py) to be running on http://localhost:5000
    # You can run it with: python ../app.py (if in tests/ directory)
    # Or using Gunicorn: gunicorn -w 4 -b 0.0.0.0:5000 app:app (from will_system_enhancements directory)
    print("Please ensure the Will API server (app.py) is running on http://localhost:5000 before running these tests.")
    print(f"Tests will target: {API_BASE_URL}")
    
    # A simple way to check if the server is up before running all tests
    try:
        requests.get(f"{API_BASE_URL}/status", timeout=2)
        logger.info(f"Successfully connected to API server at {API_BASE_URL}.")
        unittest.main()
    except requests.exceptions.ConnectionError:
        logger.critical(f"Failed to connect to Will API server at {API_BASE_URL}. Aborting tests.")
        print(f"CRITICAL: Could not connect to the API server at {API_BASE_URL}. Please start the server and try again.")
    except requests.exceptions.Timeout:
        logger.critical(f"Connection to Will API server at {API_BASE_URL} timed out. Aborting tests.")
        print(f"CRITICAL: Connection to the API server at {API_BASE_URL} timed out. Please ensure it is responsive.")


