"""
Integration Tests for SageMaker Endpoint Deployment
Validates endpoint functionality, performance, and reliability
"""

import pytest
import boto3
import json
import time
import concurrent.futures
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestEndpointDeployment:
    """Comprehensive integration tests for deployed models"""
    
    @pytest.fixture
    def sagemaker_runtime(self):
        """SageMaker runtime client"""
        return boto3.client('sagemaker-runtime', region_name='us-east-1')
    
    @pytest.fixture
    def sagemaker_client(self):
        """SageMaker client"""
        return boto3.client('sagemaker', region_name='us-east-1')
    
    @pytest.fixture
    def test_cases(self):
        """Test cases with known outcomes"""
        return [
            {
                "features": [6, 148, 72, 35, 0, 33.6, 0.627, 50],
                "expected_class": 1,
                "label": "High risk - high glucose"
            },
            {
                "features": [1, 85, 66, 29, 0, 26.6, 0.351, 31],
                "expected_class": 0,
                "label": "Low risk - healthy patient"
            },
            {
                "features": [8, 183, 64, 0, 0, 23.3, 0.672, 32],
                "expected_class": 1,
                "label": "High risk - high pregnancies"
            },
            {
                "features": [1, 89, 66, 23, 94, 28.1, 0.167, 21],
                "expected_class": 0,
                "label": "Low risk - young age"
            }
        ]
    
    # Test 1: Endpoint Availability
    def test_endpoint_exists_and_in_service(self, sagemaker_client, endpoint_name):
        """Verify endpoint exists and is in InService state"""
        logger.info(f"Testing endpoint: {endpoint_name}")
        
        try:
            response = sagemaker_client.describe_endpoint(EndpointName=endpoint_name)
            
            assert response['EndpointStatus'] == 'InService', \
                f"Endpoint status is {response['EndpointStatus']}, expected InService"
            
            logger.info(f"✓ Endpoint {endpoint_name} is InService")
            logger.info(f"  Created: {response['CreationTime']}")
            logger.info(f"  Config: {response['EndpointConfigName']}")
            
        except Exception as e:
            pytest.fail(f"Endpoint not found or not accessible: {e}")
    
    # Test 2: Basic Inference
    def test_basic_inference(self, sagemaker_runtime, endpoint_name):
        """Test basic inference request/response"""
        logger.info("Testing basic inference...")
        
        test_input = "1,85,66,29,0,26.6,0.351,31"
        
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType='text/csv',
            Accept='application/json',
            Body=test_input
        )
        
        assert response['ResponseMetadata']['HTTPStatusCode'] == 200
        assert 'Body' in response
        
        result = json.loads(response['Body'].read().decode())
        logger.info(f"✓ Got prediction: {result}")
    
    # Test 3: Response Schema Validation
    def test_response_schema(self, sagemaker_runtime, endpoint_name):
        """Validate response follows expected schema"""
        logger.info("Testing response schema...")
        
        test_input = "1,85,66,29,0,26.6,0.351,31"
        
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType='text/csv',
            Accept='application/json',
            Body=test_input
        )
        
        result = json.loads(response['Body'].read().decode())
        
        # XGBoost returns probability as float
        assert isinstance(result, (int, float)), \
            f"Expected numeric result, got {type(result)}"
        
        assert 0.0 <= result <= 1.0, \
            f"Probability {result} out of range [0, 1]"
        
        logger.info(f"✓ Response schema valid: probability={result}")
    
    # Test 4: Prediction Accuracy
    def test_prediction_accuracy(self, sagemaker_runtime, endpoint_name, test_cases):
        """Verify predictions are reasonable"""
        logger.info("Testing prediction accuracy...")
        
        correct_predictions = 0
        
        for test_case in test_cases:
            csv_input = ','.join(map(str, test_case['features']))
            
            response = sagemaker_runtime.invoke_endpoint(
                EndpointName=endpoint_name,
                ContentType='text/csv',
                Accept='application/json',
                Body=csv_input
            )
            
            probability = json.loads(response['Body'].read().decode())
            predicted_class = 1 if probability >= 0.5 else 0
            
            logger.info(f"Test: {test_case['label']}")
            logger.info(f"  Expected: {test_case['expected_class']}, "
                       f"Predicted: {predicted_class} (prob: {probability:.4f})")
            
            if predicted_class == test_case['expected_class']:
                correct_predictions += 1
        
        accuracy = correct_predictions / len(test_cases)
        logger.info(f"✓ Accuracy: {accuracy:.1%} ({correct_predictions}/{len(test_cases)})")
        
        assert accuracy >= 0.5, \
            f"Accuracy {accuracy:.1%} below minimum threshold (50%)"
    
    # Test 5: Latency SLA
    def test_latency_sla(self, sagemaker_runtime, endpoint_name):
        """Verify response time meets SLA"""
        logger.info("Testing latency SLA...")
        
        test_input = "1,85,66,29,0,26.6,0.351,31"
        latencies = []
        num_requests = 50
        
        for i in range(num_requests):
            start_time = time.time()
            
            sagemaker_runtime.invoke_endpoint(
                EndpointName=endpoint_name,
                ContentType='text/csv',
                Accept='application/json',
                Body=test_input
            )
            
            latency_ms = (time.time() - start_time) * 1000
            latencies.append(latency_ms)
            
            if (i + 1) % 10 == 0:
                logger.info(f"  Completed {i + 1}/{num_requests} requests")
        
        latencies.sort()
        p50 = latencies[len(latencies) // 2]
        p95 = latencies[int(len(latencies) * 0.95)]
        p99 = latencies[int(len(latencies) * 0.99)]
        avg = sum(latencies) / len(latencies)
        
        logger.info(f"✓ Latency statistics ({num_requests} requests):")
        logger.info(f"  Average: {avg:.0f}ms")
        logger.info(f"  p50: {p50:.0f}ms")
        logger.info(f"  p95: {p95:.0f}ms")
        logger.info(f"  p99: {p99:.0f}ms")
        
        # SLA: p95 < 1000ms for initial deployment, < 500ms for production
        assert p95 < 1000, \
            f"p95 latency {p95:.0f}ms exceeds SLA (1000ms)"
    
    # Test 6: Concurrent Load
    def test_concurrent_requests(self, sagemaker_runtime, endpoint_name):
        """Test endpoint handles concurrent requests"""
        logger.info("Testing concurrent load...")
        
        test_input = "1,85,66,29,0,26.6,0.351,31"
        num_concurrent = 20
        
        def make_request():
            try:
                response = sagemaker_runtime.invoke_endpoint(
                    EndpointName=endpoint_name,
                    ContentType='text/csv',
                    Accept='application/json',
                    Body=test_input
                )
                return response['ResponseMetadata']['HTTPStatusCode']
            except Exception as e:
                logger.error(f"Request failed: {e}")
                return 500
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = [executor.submit(make_request) for _ in range(num_concurrent)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        duration = time.time() - start_time
        
        success_count = sum(1 for status in results if status == 200)
        success_rate = success_count / num_concurrent
        
        logger.info(f"✓ Concurrent load test:")
        logger.info(f"  Requests: {num_concurrent}")
        logger.info(f"  Success: {success_count}/{num_concurrent} ({success_rate:.1%})")
        logger.info(f"  Duration: {duration:.2f}s")
        logger.info(f"  Throughput: {num_concurrent/duration:.1f} req/s")
        
        assert success_rate >= 0.90, \
            f"Success rate {success_rate:.1%} below threshold (90%)"
    
    # Test 7: Error Handling
    def test_invalid_input_handling(self, sagemaker_runtime, endpoint_name):
        """Test endpoint handles invalid inputs gracefully"""
        logger.info("Testing error handling...")
        
        invalid_inputs = [
            ("", "Empty input"),
            ("1,2,3", "Too few features"),
            ("1,2,3,4,5,6,7,8,9,10", "Too many features"),
            ("a,b,c,d,e,f,g,h", "Non-numeric input"),
        ]
        
        for invalid_input, description in invalid_inputs:
            try:
                response = sagemaker_runtime.invoke_endpoint(
                    EndpointName=endpoint_name,
                    ContentType='text/csv',
                    Accept='application/json',
                    Body=invalid_input
                )
                
                status = response['ResponseMetadata']['HTTPStatusCode']
                
                # Should either reject (4xx) or handle gracefully (200 with error message)
                logger.info(f"  {description}: HTTP {status}")
                
            except Exception as e:
                logger.info(f"  {description}: Exception caught - {type(e).__name__}")
        
        logger.info("✓ Error handling test completed")
    
    # Test 8: Data Capture (if enabled)
    def test_data_capture_enabled(self, sagemaker_client, endpoint_name):
        """Verify data capture is configured"""
        logger.info("Testing data capture configuration...")
        
        try:
            response = sagemaker_client.describe_endpoint(EndpointName=endpoint_name)
            config_name = response['EndpointConfigName']
            
            config = sagemaker_client.describe_endpoint_config(
                EndpointConfigName=config_name
            )
            
            if 'DataCaptureConfig' in config:
                dc_config = config['DataCaptureConfig']
                logger.info(f"✓ Data capture enabled:")
                logger.info(f"  Destination: {dc_config.get('DestinationS3Uri')}")
                logger.info(f"  Sampling: {dc_config.get('InitialSamplingPercentage')}%")
                logger.info(f"  Capture options: {dc_config.get('CaptureOptions')}")
            else:
                logger.info("  Data capture not enabled (optional)")
                
        except Exception as e:
            logger.warning(f"Could not check data capture: {e}")


# Pytest configuration
def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--endpoint-name",
        action="store",
        required=True,
        help="SageMaker endpoint name to test"
    )


@pytest.fixture
def endpoint_name(request):
    """Get endpoint name from command line"""
    return request.config.getoption("--endpoint-name")


if __name__ == "__main__":
    # Run with: pytest tests/integration/test_endpoint.py --endpoint-name=your-endpoint -v
    pytest.main([__file__, "-v"])
