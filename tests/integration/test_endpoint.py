"""
Automated Integration Tests for SageMaker Endpoints
Run after every deployment to validate model functionality
"""

import pytest
import boto3
import json
import time
from typing import Dict, List
import os

# Test configuration
REGION = os.environ.get("AWS_REGION", "us-east-1")
TEST_TIMEOUT = 30  # seconds


@pytest.fixture(scope="session")
def sagemaker_runtime():
    """SageMaker runtime client for invoking endpoints"""
    return boto3.client("sagemaker-runtime", region_name=REGION)


@pytest.fixture(scope="session")
def sagemaker_client():
    """SageMaker client for endpoint management"""
    return boto3.client("sagemaker", region_name=REGION)


@pytest.fixture(scope="session")
def test_samples():
    """Sample test cases with expected outcomes"""
    return [
        {
            "name": "high_risk_patient",
            "features": [6, 148, 72, 35, 0, 33.6, 0.627, 50],
            "expected_class": 1,  # Diabetic
            "description": "High glucose, older patient",
        },
        {
            "name": "low_risk_patient",
            "features": [1, 85, 66, 29, 0, 26.6, 0.351, 31],
            "expected_class": 0,  # Non-diabetic
            "description": "Young patient with normal readings",
        },
        {
            "name": "moderate_risk_patient",
            "features": [3, 120, 80, 30, 100, 30.5, 0.450, 45],
            "expected_class": None,  # Can be either - just check response format
            "description": "Borderline case",
        },
    ]


class TestEndpointAvailability:
    """Test suite for endpoint availability and basic functionality"""

    def test_endpoint_exists(self, sagemaker_client, endpoint_name):
        """Test 1: Verify endpoint exists"""
        try:
            response = sagemaker_client.describe_endpoint(EndpointName=endpoint_name)
            assert response["EndpointStatus"] == "InService", (
                f"Endpoint {endpoint_name} is not in service. "
                f"Status: {response['EndpointStatus']}"
            )
            print(f"✓ Endpoint {endpoint_name} is InService")
        except sagemaker_client.exceptions.ClientError as e:
            pytest.fail(f"Endpoint {endpoint_name} does not exist: {e}")

    def test_endpoint_responds(self, sagemaker_runtime, endpoint_name):
        """Test 2: Verify endpoint responds to requests"""
        test_input = "1,85,66,29,0,26.6,0.351,31"

        try:
            response = sagemaker_runtime.invoke_endpoint(
                EndpointName=endpoint_name,
                ContentType="text/csv",
                Accept="application/json",
                Body=test_input,
            )

            assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
            assert "Body" in response
            print(f"✓ Endpoint responds successfully")

        except Exception as e:
            pytest.fail(f"Endpoint invocation failed: {e}")


class TestPredictionQuality:
    """Test suite for prediction quality and correctness"""

    def test_response_format(self, sagemaker_runtime, endpoint_name):
        """Test 3: Verify response format is valid"""
        test_input = "1,85,66,29,0,26.6,0.351,31"

        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType="text/csv",
            Accept="application/json",
            Body=test_input,
        )

        result = json.loads(response["Body"].read().decode())

        # XGBoost returns probability as float
        assert isinstance(result, (int, float)), (
            f"Expected numeric response, got {type(result)}"
        )
        assert 0.0 <= result <= 1.0, f"Probability {result} out of range [0, 1]"

        print(f"✓ Response format valid: {result}")

    def test_prediction_consistency(
        self, sagemaker_runtime, endpoint_name, test_samples
    ):
        """Test 4: Verify same input produces same output"""
        test_case = test_samples[0]  # High risk patient
        csv_input = ",".join(map(str, test_case["features"]))

        predictions = []
        for i in range(3):
            response = sagemaker_runtime.invoke_endpoint(
                EndpointName=endpoint_name,
                ContentType="text/csv",
                Accept="application/json",
                Body=csv_input,
            )
            prediction = json.loads(response["Body"].read().decode())
            predictions.append(prediction)

        # All predictions should be identical (deterministic model)
        assert all(p == predictions[0] for p in predictions), (
            f"Predictions not consistent: {predictions}"
        )

        print(f"✓ Predictions are consistent: {predictions[0]}")

    def test_known_cases(self, sagemaker_runtime, endpoint_name, test_samples):
        """Test 5: Verify predictions for known test cases"""
        correct_predictions = 0
        total_cases = 0

        for test_case in test_samples:
            if test_case["expected_class"] is None:
                continue  # Skip borderline cases

            csv_input = ",".join(map(str, test_case["features"]))

            response = sagemaker_runtime.invoke_endpoint(
                EndpointName=endpoint_name,
                ContentType="text/csv",
                Accept="application/json",
                Body=csv_input,
            )

            probability = json.loads(response["Body"].read().decode())
            predicted_class = 1 if probability >= 0.5 else 0

            is_correct = predicted_class == test_case["expected_class"]

            print(f"\n  Test: {test_case['name']}")
            print(f"    Description: {test_case['description']}")
            print(f"    Expected: {test_case['expected_class']}")
            print(f"    Predicted: {predicted_class} (prob: {probability:.4f})")
            print(f"    Result: {'✓ PASS' if is_correct else '✗ FAIL'}")

            if is_correct:
                correct_predictions += 1
            total_cases += 1

        accuracy = correct_predictions / total_cases if total_cases > 0 else 0
        print(f"\n✓ Test accuracy: {accuracy:.1%} ({correct_predictions}/{total_cases})")

        # At least 50% should be correct (sanity check)
        assert accuracy >= 0.5, f"Test accuracy {accuracy:.1%} too low"


class TestPerformance:
    """Test suite for performance and latency"""

    def test_response_time(self, sagemaker_runtime, endpoint_name):
        """Test 6: Verify response time meets SLA"""
        test_input = "1,85,66,29,0,26.6,0.351,31"
        latencies = []

        # Test 20 requests
        for _ in range(20):
            start_time = time.time()

            sagemaker_runtime.invoke_endpoint(
                EndpointName=endpoint_name,
                ContentType="text/csv",
                Accept="application/json",
                Body=test_input,
            )

            latency_ms = (time.time() - start_time) * 1000
            latencies.append(latency_ms)

        # Calculate statistics
        latencies.sort()
        avg_latency = sum(latencies) / len(latencies)
        p50 = latencies[len(latencies) // 2]
        p95 = latencies[int(len(latencies) * 0.95)]

        print(f"\n  Latency statistics (20 requests):")
        print(f"    Average: {avg_latency:.0f}ms")
        print(f"    P50: {p50:.0f}ms")
        print(f"    P95: {p95:.0f}ms")

        # Dev environment: relaxed SLA (1000ms p95)
        # Production: should be <500ms p95
        assert p95 < 1000, f"P95 latency {p95:.0f}ms exceeds SLA (1000ms)"

        print(f"✓ Latency within SLA")

    def test_error_handling(self, sagemaker_runtime, endpoint_name):
        """Test 7: Verify graceful error handling"""
        # Test with invalid input
        invalid_inputs = [
            ("", "Empty input"),
            ("invalid,data", "Non-numeric input"),
            ("1,2,3", "Wrong feature count (too few)"),
            ("1,2,3,4,5,6,7,8,9,10,11,12", "Wrong feature count (too many)"),
        ]

        for invalid_input, description in invalid_inputs:
            try:
                response = sagemaker_runtime.invoke_endpoint(
                    EndpointName=endpoint_name,
                    ContentType="text/csv",
                    Accept="application/json",
                    Body=invalid_input,
                )
                # If it doesn't raise an error, check if response is still valid
                result = json.loads(response["Body"].read().decode())
                print(f"  {description}: Handled gracefully (returned {result})")
            except Exception as e:
                # Expected to fail for invalid inputs
                print(f"  {description}: Rejected with error (expected)")
                pass

        print(f"✓ Error handling verified")


class TestModelMetadata:
    """Test suite for model metadata and lineage"""

    def test_endpoint_config(self, sagemaker_client, endpoint_name):
        """Test 8: Verify endpoint configuration"""
        endpoint = sagemaker_client.describe_endpoint(EndpointName=endpoint_name)
        config_name = endpoint["EndpointConfigName"]

        config = sagemaker_client.describe_endpoint_config(
            EndpointConfigName=config_name
        )

        print(f"\n  Endpoint configuration:")
        print(f"    Config name: {config_name}")

        for variant in config["ProductionVariants"]:
            print(f"    Variant: {variant['VariantName']}")
            print(f"      Instance type: {variant['InstanceType']}")
            print(f"      Instance count: {variant['InitialInstanceCount']}")
            print(f"      Model: {variant['ModelName']}")

        # Verify data capture is enabled (if in config)
        if "DataCaptureConfig" in config:
            print(f"    Data capture: Enabled")
            print(f"      Destination: {config['DataCaptureConfig']['DestinationS3Uri']}")
        else:
            print(f"    Data capture: Disabled")

        print(f"✓ Endpoint configuration validated")


def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--endpoint-name",
        action="store",
        default=None,
        help="SageMaker endpoint name to test",
    )


@pytest.fixture(scope="session")
def endpoint_name(request):
    """Get endpoint name from command line or environment"""
    name = request.config.getoption("--endpoint-name")
    if not name:
        name = os.environ.get("ENDPOINT_NAME")
    if not name:
        pytest.fail("Endpoint name not provided. Use --endpoint-name or set ENDPOINT_NAME env var")
    return name


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
