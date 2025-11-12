# Production-Grade Model Registry & Deployment Best Practices

**Generated:** November 12, 2025  
**Context:** Moving from development to production-grade ML deployment

---

## 🎯 Current State vs. Production-Grade

### Current Implementation (Development/MVP)

```yaml
Current Flow:
  Training → Evaluation → Auto-Register → Manual Approval → Deploy

Issues:
  ❌ Auto-approval bypasses quality checks
  ❌ No multi-stage deployment (dev → staging → prod)
  ❌ Manual approval bottleneck
  ❌ No rollback strategy
  ❌ No A/B testing capability
  ❌ Single model version in production
  ❌ No canary deployments
```

### Production-Grade System

```yaml
Production Flow:
  Training → Evaluation → Quality Gates → Model Registry
    → Dev Deployment (auto) → Integration Tests
    → Staging Deployment (auto) → Load Tests
    → Approval Workflow → Canary Deployment (prod)
    → Monitor → Gradual Rollout → Full Production

Benefits:
  ✅ Automated quality gates
  ✅ Multi-stage progressive deployment
  ✅ Automated testing at each stage
  ✅ Safe rollback mechanisms
  ✅ A/B testing & shadow mode
  ✅ Blue/green deployments
  ✅ Gradual traffic shifting
  ✅ Automated rollback on errors
```

---

## 🏗️ Production Architecture Overview

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                        MODEL LIFECYCLE STAGES                           │
└─────────────────────────────────────────────────────────────────────────┘

STAGE 1: TRAINING & REGISTRATION
════════════════════════════════════════════════════════════════════════════
┌──────────────┐      ┌──────────────┐      ┌──────────────────────┐
│   Training   │─────>│  Evaluation  │─────>│   Quality Gates      │
│   Pipeline   │      │  Metrics     │      │   ✓ Accuracy >= 0.75 │
└──────────────┘      └──────────────┘      │   ✓ F1 >= 0.70       │
                                            │   ✓ ROC-AUC >= 0.80  │
                                            │   ✓ Latency < 200ms  │
                                            │   ✓ Model size < 100MB│
                                            └──────────┬───────────┘
                                                       │ PASS
                                                       ▼
                                            ┌──────────────────────┐
                                            │   Model Registry     │
                                            │   Status: Pending    │
                                            │   Version: v23       │
                                            └──────────┬───────────┘
                                                       │
                                                       ▼
                                            ┌──────────────────────┐
                                            │  Automated Tests     │
                                            │  ✓ Schema validation │
                                            │  ✓ Inference test    │
                                            │  ✓ Load test         │
                                            └──────────┬───────────┘
                                                       │ PASS
                                                       ▼
                                            ┌──────────────────────┐
                                            │   Status: Approved   │
                                            └──────────────────────┘


STAGE 2: DEV ENVIRONMENT (Auto-Deploy)
════════════════════════════════════════════════════════════════════════════
                        ┌──────────────────────┐
                        │   Dev Endpoint       │
                        │   ml.t2.medium       │
                        │   1 instance         │
                        │   Auto-deploy v23    │
                        └──────────┬───────────┘
                                   │
                        ┌──────────▼───────────┐
                        │  Integration Tests   │
                        │  ✓ API response      │
                        │  ✓ Feature drift     │
                        │  ✓ Output schema     │
                        └──────────┬───────────┘
                                   │ PASS
                                   ▼
                        ┌──────────────────────┐
                        │   Tag: tested-dev    │
                        └──────────────────────┘


STAGE 3: STAGING ENVIRONMENT (Auto-Deploy after Dev)
════════════════════════════════════════════════════════════════════════════
                        ┌──────────────────────┐
                        │  Staging Endpoint    │
                        │  ml.m5.large         │
                        │  2 instances         │
                        │  Production-like     │
                        └──────────┬───────────┘
                                   │
                        ┌──────────▼───────────┐
                        │  Load Tests          │
                        │  ✓ 1000 req/sec      │
                        │  ✓ Latency p95<500ms │
                        │  ✓ No memory leaks   │
                        │  ✓ Auto-scaling      │
                        └──────────┬───────────┘
                                   │ PASS
                                   ▼
                        ┌──────────────────────┐
                        │  Shadow Mode Test    │
                        │  (Parallel to prod)  │
                        │  Compare predictions │
                        └──────────┬───────────┘
                                   │ PASS
                                   ▼
                        ┌──────────────────────┐
                        │  Tag: staging-ready  │
                        └──────────────────────┘


STAGE 4: PRODUCTION DEPLOYMENT (Approval Required)
════════════════════════════════════════════════════════════════════════════
                        ┌──────────────────────┐
                        │  Approval Required   │
                        │  • ML Lead review    │
                        │  • Stakeholder sign  │
                        │  • Change ticket     │
                        └──────────┬───────────┘
                                   │ APPROVED
                                   ▼
                    ┌───────────────────────────┐
                    │   DEPLOYMENT STRATEGY     │
                    │   (Choose one)            │
                    └───┬───────────────────┬───┘
                        │                   │
        ┌───────────────▼────┐     ┌───────▼────────────┐
        │  CANARY DEPLOYMENT │     │  BLUE/GREEN        │
        │  5% → 25% → 100%   │     │  Instant Switch    │
        └────────────────────┘     └────────────────────┘


CANARY DEPLOYMENT FLOW:
────────────────────────────────────────────────────────────────────────────
Phase 1: 5% Traffic (1 hour)
    │
    ├─> Monitor: Error rate, Latency, Accuracy
    │   ✓ Error rate < 1%
    │   ✓ Latency p95 < 500ms
    │   ✓ No drift detected
    │
    ▼
Phase 2: 25% Traffic (2 hours)
    │
    ├─> Monitor: Business metrics, User feedback
    │   ✓ Conversion rate stable
    │   ✓ No user complaints
    │
    ▼
Phase 3: 50% Traffic (4 hours)
    │
    ├─> Monitor: Cost, Resource usage
    │   ✓ Cost within budget
    │   ✓ Auto-scaling working
    │
    ▼
Phase 4: 100% Traffic
    │
    └─> Old model kept for 24h (rollback safety)


AUTOMATED ROLLBACK TRIGGERS:
────────────────────────────────────────────────────────────────────────────
IF any of these occur → INSTANT ROLLBACK to previous version:
  ⚠️  Error rate > 5%
  ⚠️  Latency p95 > 1000ms
  ⚠️  Model accuracy drop > 10%
  ⚠️  Endpoint invocation errors > 100/min
  ⚠️  Memory usage > 90%
  ⚠️  Manual rollback triggered
```

---

## 📋 Implementation Checklist

### Phase 1: Enhanced Model Registry (Week 1-2)

```yaml
Tasks:
  1. Multi-stage approval workflow
     - PendingTests → TestPassed → PendingApproval → Approved → Production
  
  2. Model metadata enrichment
     - Training data version
     - Feature schema
     - Performance benchmarks
     - Explainability artifacts
     - Bias metrics
  
  3. Model versioning strategy
     - Semantic versioning (v1.2.3)
     - Git commit SHA tagging
     - Dataset version tracking
  
  4. Model lineage tracking
     - Data source → Preprocessing → Training → Evaluation → Deployment
     - Full reproducibility
```

### Phase 2: Multi-Environment Setup (Week 2-3)

```yaml
Environments:
  dev:
    purpose: Development & integration testing
    instance: ml.t2.medium
    auto_deploy: true
    approval_required: false
    
  staging:
    purpose: Load testing & shadow mode
    instance: ml.m5.large (2 instances)
    auto_deploy: true (after dev tests pass)
    approval_required: false
    
  production:
    purpose: Live customer traffic
    instance: ml.m5.large (2-10 instances with auto-scaling)
    auto_deploy: false
    approval_required: true
    deployment_strategy: canary
```

### Phase 3: Automated Testing (Week 3-4)

```yaml
Test Levels:
  unit_tests:
    - Model loading
    - Inference function
    - Input validation
    
  integration_tests:
    - API endpoint response
    - Feature schema validation
    - Output format validation
    
  load_tests:
    - 1000 concurrent requests
    - Latency SLA validation
    - Memory leak detection
    
  shadow_tests:
    - Run new model parallel to production
    - Compare predictions
    - Analyze differences
```

### Phase 4: Deployment Strategies (Week 4-5)

```yaml
Strategies:
  canary:
    phases: [5%, 25%, 50%, 100%]
    duration_per_phase: [1h, 2h, 4h, stable]
    rollback_on_error: true
    
  blue_green:
    switch_time: instant
    validation_period: 30min
    rollback_option: available for 24h
    
  shadow_mode:
    duration: 7 days
    comparison_metrics: [accuracy, latency, predictions]
    promote_if: agreement > 95%
```

---

## 🔧 Implementation Code

### 1. Enhanced Model Registration

**File:** `src/model_registry/advanced_registration.py`

```python
"""
Production-grade model registration with enhanced metadata
"""

import json
import boto3
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ProductionModelRegistry:
    """Enhanced model registry with production-grade features"""
    
    def __init__(self, sagemaker_client, model_package_group_name: str):
        self.sm_client = sagemaker_client
        self.model_package_group_name = model_package_group_name
    
    def register_model_with_metadata(
        self,
        model_data_url: str,
        metrics: Dict[str, float],
        training_job_name: str,
        model_version: str,
        git_commit_sha: str,
        data_version: str,
        feature_schema: Dict[str, Any],
        approval_status: str = "PendingManualApproval"
    ) -> str:
        """
        Register model with comprehensive metadata
        
        Args:
            model_data_url: S3 path to model.tar.gz
            metrics: Evaluation metrics
            training_job_name: SageMaker training job name
            model_version: Semantic version (e.g., "1.2.3")
            git_commit_sha: Git commit for reproducibility
            data_version: Dataset version used for training
            feature_schema: Expected input feature schema
            approval_status: Initial approval status
        
        Returns:
            model_package_arn: ARN of registered model package
        """
        
        # Construct model package metadata
        model_package_description = {
            "ModelPackageDescription": f"Diabetes classifier v{model_version}",
            "ModelPackageGroupName": self.model_package_group_name,
            "ModelApprovalStatus": approval_status,
            
            # Model artifacts
            "InferenceSpecification": {
                "Containers": [{
                    "Image": "683313688378.dkr.ecr.us-east-1.amazonaws.com/sagemaker-xgboost:1.5-1",
                    "ModelDataUrl": model_data_url
                }],
                "SupportedContentTypes": ["text/csv", "application/json"],
                "SupportedResponseMIMETypes": ["application/json"]
            },
            
            # Model metrics
            "ModelMetrics": {
                "ModelQuality": {
                    "Statistics": {
                        "ContentType": "application/json",
                        "S3Uri": f"{model_data_url.rsplit('/', 1)[0]}/evaluation_results.json"
                    }
                }
            },
            
            # Enhanced metadata
            "CustomerMetadataProperties": {
                "model_version": model_version,
                "git_commit_sha": git_commit_sha,
                "data_version": data_version,
                "training_job_name": training_job_name,
                "registration_date": datetime.utcnow().isoformat(),
                "accuracy": str(metrics.get("accuracy", 0)),
                "f1_score": str(metrics.get("f1_score", 0)),
                "roc_auc": str(metrics.get("roc_auc", 0)),
                "feature_count": str(len(feature_schema.get("features", []))),
                "feature_schema": json.dumps(feature_schema)
            },
            
            # Model versioning tags
            "Tags": [
                {"Key": "ModelVersion", "Value": model_version},
                {"Key": "GitCommit", "Value": git_commit_sha},
                {"Key": "DataVersion", "Value": data_version},
                {"Key": "Environment", "Value": "registered"},
                {"Key": "Project", "Value": "diabetes-classifier"}
            ]
        }
        
        # Register model package
        response = self.sm_client.create_model_package(**model_package_description)
        model_package_arn = response["ModelPackageArn"]
        
        logger.info(f"Model registered: {model_package_arn}")
        logger.info(f"Version: {model_version}")
        logger.info(f"Status: {approval_status}")
        
        return model_package_arn
    
    def update_approval_status(
        self,
        model_package_arn: str,
        new_status: str,
        approved_by: str = None,
        approval_notes: str = None
    ):
        """
        Update model approval status with audit trail
        
        Statuses: PendingManualApproval → Approved → Production
        """
        update_params = {
            "ModelPackageArn": model_package_arn,
            "ModelApprovalStatus": new_status
        }
        
        # Add approval metadata
        if approved_by or approval_notes:
            self.sm_client.add_tags(
                ResourceArn=model_package_arn,
                Tags=[
                    {"Key": "ApprovedBy", "Value": approved_by or "automated"},
                    {"Key": "ApprovalDate", "Value": datetime.utcnow().isoformat()},
                    {"Key": "ApprovalNotes", "Value": approval_notes or "Automated approval"}
                ]
            )
        
        self.sm_client.update_model_package(**update_params)
        logger.info(f"Model status updated to: {new_status}")
    
    def get_model_lineage(self, model_package_arn: str) -> Dict[str, Any]:
        """
        Get complete lineage for a model
        """
        # Get model package details
        model_package = self.sm_client.describe_model_package(
            ModelPackageName=model_package_arn
        )
        
        # Extract lineage information
        lineage = {
            "model_package_arn": model_package_arn,
            "version": model_package.get("CustomerMetadataProperties", {}).get("model_version"),
            "git_commit": model_package.get("CustomerMetadataProperties", {}).get("git_commit_sha"),
            "data_version": model_package.get("CustomerMetadataProperties", {}).get("data_version"),
            "training_job": model_package.get("CustomerMetadataProperties", {}).get("training_job_name"),
            "registration_date": model_package.get("CreationTime"),
            "approval_status": model_package.get("ModelApprovalStatus"),
            "metrics": {
                "accuracy": model_package.get("CustomerMetadataProperties", {}).get("accuracy"),
                "f1_score": model_package.get("CustomerMetadataProperties", {}).get("f1_score"),
                "roc_auc": model_package.get("CustomerMetadataProperties", {}).get("roc_auc")
            }
        }
        
        return lineage
```

---

### 2. Multi-Stage Deployment

**File:** `src/deployment/progressive_deployment.py`

```python
"""
Progressive deployment strategies for production
"""

import time
import boto3
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class CanaryDeployment:
    """Canary deployment with gradual traffic shifting"""
    
    def __init__(self, sagemaker_client, cloudwatch_client):
        self.sm_client = sagemaker_client
        self.cw_client = cloudwatch_client
    
    def deploy_canary(
        self,
        endpoint_name: str,
        new_model_name: str,
        production_variant_name: str = "AllTraffic",
        phases: List[Dict] = None
    ):
        """
        Deploy new model with canary strategy
        
        Args:
            endpoint_name: Existing production endpoint
            new_model_name: New model to deploy
            production_variant_name: Variant name
            phases: List of [{traffic_percentage: 5, duration_minutes: 60}, ...]
        """
        
        if phases is None:
            # Default canary phases
            phases = [
                {"traffic_percentage": 5, "duration_minutes": 60},
                {"traffic_percentage": 25, "duration_minutes": 120},
                {"traffic_percentage": 50, "duration_minutes": 240},
                {"traffic_percentage": 100, "duration_minutes": 0}
            ]
        
        logger.info(f"Starting canary deployment to {endpoint_name}")
        logger.info(f"Phases: {phases}")
        
        # Get current endpoint config
        endpoint_desc = self.sm_client.describe_endpoint(EndpointName=endpoint_name)
        current_config_name = endpoint_desc["EndpointConfigName"]
        
        # Get current model from config
        config_desc = self.sm_client.describe_endpoint_config(
            EndpointConfigName=current_config_name
        )
        current_variant = config_desc["ProductionVariants"][0]
        current_model_name = current_variant["ModelName"]
        
        logger.info(f"Current model: {current_model_name}")
        logger.info(f"New model: {new_model_name}")
        
        # Execute canary phases
        for phase_num, phase in enumerate(phases, 1):
            traffic_pct = phase["traffic_percentage"]
            duration = phase["duration_minutes"]
            
            logger.info(f"\n{'='*60}")
            logger.info(f"PHASE {phase_num}: {traffic_pct}% traffic to new model")
            logger.info(f"Duration: {duration} minutes")
            logger.info(f"{'='*60}\n")
            
            # Create new endpoint config with traffic split
            new_config_name = f"{endpoint_name}-canary-{traffic_pct}pct-{int(time.time())}"
            
            production_variants = [
                {
                    "VariantName": "variant-old",
                    "ModelName": current_model_name,
                    "InitialInstanceCount": current_variant["InitialInstanceCount"],
                    "InstanceType": current_variant["InstanceType"],
                    "InitialVariantWeight": 100 - traffic_pct
                },
                {
                    "VariantName": "variant-new",
                    "ModelName": new_model_name,
                    "InitialInstanceCount": 1,
                    "InstanceType": current_variant["InstanceType"],
                    "InitialVariantWeight": traffic_pct
                }
            ]
            
            self.sm_client.create_endpoint_config(
                EndpointConfigName=new_config_name,
                ProductionVariants=production_variants,
                DataCaptureConfig=config_desc.get("DataCaptureConfig")
            )
            
            # Update endpoint
            self.sm_client.update_endpoint(
                EndpointName=endpoint_name,
                EndpointConfigName=new_config_name
            )
            
            # Wait for endpoint to be in service
            logger.info("Waiting for endpoint update...")
            waiter = self.sm_client.get_waiter('endpoint_in_service')
            waiter.wait(EndpointName=endpoint_name)
            logger.info("✓ Endpoint updated successfully")
            
            # Monitor phase
            if duration > 0:
                logger.info(f"Monitoring for {duration} minutes...")
                
                # Check metrics every 5 minutes
                check_interval = 5  # minutes
                checks = duration // check_interval
                
                for check_num in range(checks):
                    time.sleep(check_interval * 60)
                    
                    # Get metrics
                    metrics = self._get_endpoint_metrics(
                        endpoint_name,
                        variant_name="variant-new",
                        period_minutes=check_interval
                    )
                    
                    logger.info(f"Check {check_num + 1}/{checks}:")
                    logger.info(f"  Error rate: {metrics['error_rate']:.2f}%")
                    logger.info(f"  Avg latency: {metrics['latency']:.0f}ms")
                    logger.info(f"  Invocations: {metrics['invocations']}")
                    
                    # Check for rollback conditions
                    should_rollback, reason = self._should_rollback(metrics)
                    
                    if should_rollback:
                        logger.error(f"⚠️  ROLLBACK TRIGGERED: {reason}")
                        self._rollback_deployment(endpoint_name, current_config_name)
                        raise Exception(f"Canary deployment failed: {reason}")
                
                logger.info(f"✓ Phase {phase_num} completed successfully")
        
        logger.info("\n🎉 Canary deployment completed successfully!")
        logger.info(f"New model {new_model_name} is now serving 100% of traffic")
    
    def _get_endpoint_metrics(
        self,
        endpoint_name: str,
        variant_name: str,
        period_minutes: int
    ) -> Dict[str, float]:
        """Get CloudWatch metrics for endpoint variant"""
        
        from datetime import datetime, timedelta
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=period_minutes)
        
        # Get invocation count
        invocations = self._get_metric_statistics(
            endpoint_name, variant_name, "Invocations",
            start_time, end_time, "Sum"
        )
        
        # Get invocation errors
        errors_4xx = self._get_metric_statistics(
            endpoint_name, variant_name, "Invocation4XXErrors",
            start_time, end_time, "Sum"
        )
        
        errors_5xx = self._get_metric_statistics(
            endpoint_name, variant_name, "Invocation5XXErrors",
            start_time, end_time, "Sum"
        )
        
        # Get model latency
        latency = self._get_metric_statistics(
            endpoint_name, variant_name, "ModelLatency",
            start_time, end_time, "Average"
        )
        
        # Calculate error rate
        total_errors = errors_4xx + errors_5xx
        error_rate = (total_errors / invocations * 100) if invocations > 0 else 0
        
        return {
            "invocations": invocations,
            "error_rate": error_rate,
            "latency": latency
        }
    
    def _get_metric_statistics(
        self,
        endpoint_name: str,
        variant_name: str,
        metric_name: str,
        start_time,
        end_time,
        statistic: str
    ) -> float:
        """Get CloudWatch metric statistics"""
        
        response = self.cw_client.get_metric_statistics(
            Namespace='AWS/SageMaker',
            MetricName=metric_name,
            Dimensions=[
                {'Name': 'EndpointName', 'Value': endpoint_name},
                {'Name': 'VariantName', 'Value': variant_name}
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=300,  # 5 minutes
            Statistics=[statistic]
        )
        
        datapoints = response.get('Datapoints', [])
        if not datapoints:
            return 0.0
        
        return datapoints[0].get(statistic, 0.0)
    
    def _should_rollback(self, metrics: Dict[str, float]) -> tuple[bool, str]:
        """
        Check if deployment should be rolled back
        
        Rollback triggers:
        - Error rate > 5%
        - Latency > 1000ms
        - Invocations = 0 (endpoint not receiving traffic)
        """
        
        if metrics['error_rate'] > 5.0:
            return True, f"Error rate {metrics['error_rate']:.2f}% exceeds threshold (5%)"
        
        if metrics['latency'] > 1000:
            return True, f"Latency {metrics['latency']:.0f}ms exceeds threshold (1000ms)"
        
        if metrics['invocations'] == 0:
            return True, "Endpoint not receiving traffic"
        
        return False, ""
    
    def _rollback_deployment(self, endpoint_name: str, previous_config_name: str):
        """Rollback to previous endpoint configuration"""
        
        logger.warning(f"Rolling back endpoint {endpoint_name}")
        logger.warning(f"Reverting to config: {previous_config_name}")
        
        self.sm_client.update_endpoint(
            EndpointName=endpoint_name,
            EndpointConfigName=previous_config_name
        )
        
        # Wait for rollback to complete
        waiter = self.sm_client.get_waiter('endpoint_in_service')
        waiter.wait(EndpointName=endpoint_name)
        
        logger.info("✓ Rollback completed successfully")
```

---

### 3. Automated Testing Framework

**File:** `tests/integration/test_endpoint_deployment.py`

```python
"""
Integration tests for deployed models
"""

import pytest
import boto3
import json
from typing import List

class TestEndpointDeployment:
    """Test suite for deployed model endpoints"""
    
    @pytest.fixture
    def sagemaker_runtime(self):
        return boto3.client('sagemaker-runtime', region_name='us-east-1')
    
    @pytest.fixture
    def test_data(self):
        """Sample test cases with known outcomes"""
        return [
            {
                "features": [6, 148, 72, 35, 0, 33.6, 0.627, 50],
                "expected_class": 1,  # High risk
                "label": "High glucose patient"
            },
            {
                "features": [1, 85, 66, 29, 0, 26.6, 0.351, 31],
                "expected_class": 0,  # Low risk
                "label": "Healthy patient"
            }
        ]
    
    def test_endpoint_availability(self, sagemaker_runtime, endpoint_name):
        """Test 1: Endpoint is available and responding"""
        
        test_input = "1,85,66,29,0,26.6,0.351,31"
        
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType='text/csv',
            Accept='application/json',
            Body=test_input
        )
        
        assert response['ResponseMetadata']['HTTPStatusCode'] == 200
        assert 'Body' in response
    
    def test_prediction_schema(self, sagemaker_runtime, endpoint_name):
        """Test 2: Response follows expected schema"""
        
        test_input = "1,85,66,29,0,26.6,0.351,31"
        
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType='text/csv',
            Accept='application/json',
            Body=test_input
        )
        
        result = json.loads(response['Body'].read().decode())
        
        # XGBoost returns probability as float
        assert isinstance(result, (int, float))
        assert 0.0 <= result <= 1.0
    
    def test_prediction_accuracy(self, sagemaker_runtime, endpoint_name, test_data):
        """Test 3: Predictions match expected outcomes"""
        
        correct_predictions = 0
        
        for test_case in test_data:
            # Format features as CSV
            csv_input = ','.join(map(str, test_case['features']))
            
            response = sagemaker_runtime.invoke_endpoint(
                EndpointName=endpoint_name,
                ContentType='text/csv',
                Accept='application/json',
                Body=csv_input
            )
            
            probability = json.loads(response['Body'].read().decode())
            predicted_class = 1 if probability >= 0.5 else 0
            
            print(f"Test: {test_case['label']}")
            print(f"  Expected: {test_case['expected_class']}")
            print(f"  Predicted: {predicted_class} (prob: {probability:.4f})")
            
            if predicted_class == test_case['expected_class']:
                correct_predictions += 1
        
        accuracy = correct_predictions / len(test_data)
        assert accuracy >= 0.7, f"Accuracy {accuracy:.2%} below threshold (70%)"
    
    def test_latency_sla(self, sagemaker_runtime, endpoint_name):
        """Test 4: Response time meets SLA (< 500ms)"""
        
        import time
        
        test_input = "1,85,66,29,0,26.6,0.351,31"
        latencies = []
        
        # Test 100 requests
        for _ in range(100):
            start_time = time.time()
            
            sagemaker_runtime.invoke_endpoint(
                EndpointName=endpoint_name,
                ContentType='text/csv',
                Accept='application/json',
                Body=test_input
            )
            
            latency_ms = (time.time() - start_time) * 1000
            latencies.append(latency_ms)
        
        # Calculate percentiles
        latencies.sort()
        p50 = latencies[50]
        p95 = latencies[95]
        p99 = latencies[99]
        
        print(f"Latency p50: {p50:.0f}ms")
        print(f"Latency p95: {p95:.0f}ms")
        print(f"Latency p99: {p99:.0f}ms")
        
        assert p95 < 500, f"p95 latency {p95:.0f}ms exceeds SLA (500ms)"
    
    def test_concurrent_load(self, sagemaker_runtime, endpoint_name):
        """Test 5: Endpoint handles concurrent requests"""
        
        import concurrent.futures
        
        test_input = "1,85,66,29,0,26.6,0.351,31"
        num_concurrent = 50
        
        def make_request():
            response = sagemaker_runtime.invoke_endpoint(
                EndpointName=endpoint_name,
                ContentType='text/csv',
                Accept='application/json',
                Body=test_input
            )
            return response['ResponseMetadata']['HTTPStatusCode']
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = [executor.submit(make_request) for _ in range(num_concurrent)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        success_count = sum(1 for status in results if status == 200)
        success_rate = success_count / num_concurrent
        
        print(f"Concurrent requests: {num_concurrent}")
        print(f"Success rate: {success_rate:.1%}")
        
        assert success_rate >= 0.95, f"Success rate {success_rate:.1%} below threshold (95%)"
```

---

### 4. CI/CD Pipeline with Multi-Stage Deployment

**File:** `.github/workflows/model_deployment_production.yml`

```yaml
name: Production Model Deployment Pipeline

on:
  workflow_dispatch:
    inputs:
      model_version:
        description: 'Model version to deploy (e.g., v1.2.3)'
        required: true
      environment:
        description: 'Target environment'
        required: true
        type: choice
        options:
          - dev
          - staging
          - production
      deployment_strategy:
        description: 'Deployment strategy for production'
        required: false
        type: choice
        options:
          - canary
          - blue_green
        default: canary

env:
  AWS_REGION: us-east-1
  MODEL_REGISTRY_GROUP: mlops-diabetes-model-group

jobs:
  # Job 1: Validate Model
  validate_model:
    runs-on: ubuntu-latest
    outputs:
      model_package_arn: ${{ steps.get_model.outputs.arn }}
    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}
      
      - name: Get model from registry
        id: get_model
        run: |
          # Get approved model with specified version
          MODEL_ARN=$(aws sagemaker list-model-packages \
            --model-package-group-name ${{ env.MODEL_REGISTRY_GROUP }} \
            --model-approval-status Approved \
            --query "ModelPackageSummaryList[?CustomerMetadataProperties.model_version=='${{ github.event.inputs.model_version }}'].ModelPackageArn" \
            --output text)
          
          if [ -z "$MODEL_ARN" ]; then
            echo "❌ Model version ${{ github.event.inputs.model_version }} not found or not approved"
            exit 1
          fi
          
          echo "✓ Found model: $MODEL_ARN"
          echo "arn=$MODEL_ARN" >> $GITHUB_OUTPUT
      
      - name: Validate model metrics
        run: |
          # Get model package details
          aws sagemaker describe-model-package \
            --model-package-name ${{ steps.get_model.outputs.arn }} \
            --query 'CustomerMetadataProperties' \
            --output json > model_metadata.json
          
          # Extract metrics
          ACCURACY=$(jq -r '.accuracy' model_metadata.json)
          F1_SCORE=$(jq -r '.f1_score' model_metadata.json)
          
          echo "Model Metrics:"
          echo "  Accuracy: $ACCURACY"
          echo "  F1 Score: $F1_SCORE"
          
          # Validate thresholds
          if (( $(echo "$ACCURACY < 0.75" | bc -l) )); then
            echo "❌ Accuracy $ACCURACY below threshold (0.75)"
            exit 1
          fi

  # Job 2: Deploy to Dev (Auto)
  deploy_dev:
    needs: validate_model
    if: github.event.inputs.environment == 'dev' || github.event.inputs.environment == 'staging' || github.event.inputs.environment == 'production'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.8'
      
      - name: Install dependencies
        run: |
          pip install boto3 sagemaker pytest
      
      - name: Deploy to dev environment
        run: |
          python src/deployment/deploy.py \
            --environment dev \
            --model-package-arn ${{ needs.validate_model.outputs.model_package_arn }} \
            --endpoint-name diabetes-classifier-dev
      
      - name: Run integration tests
        run: |
          pytest tests/integration/test_endpoint_deployment.py \
            --endpoint-name diabetes-classifier-dev \
            -v
  
  # Job 3: Deploy to Staging (Auto after Dev)
  deploy_staging:
    needs: [validate_model, deploy_dev]
    if: github.event.inputs.environment == 'staging' || github.event.inputs.environment == 'production'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.8'
      
      - name: Deploy to staging environment
        run: |
          python src/deployment/deploy.py \
            --environment staging \
            --model-package-arn ${{ needs.validate_model.outputs.model_package_arn }} \
            --endpoint-name diabetes-classifier-staging
      
      - name: Run load tests
        run: |
          pytest tests/load/test_load_performance.py \
            --endpoint-name diabetes-classifier-staging \
            --target-rps 100 \
            -v
      
      - name: Run shadow mode test
        run: |
          python tests/shadow_mode/compare_predictions.py \
            --new-endpoint diabetes-classifier-staging \
            --prod-endpoint diabetes-classifier-prod \
            --sample-size 1000

  # Job 4: Production Approval Gate
  approve_production:
    needs: [validate_model, deploy_staging]
    if: github.event.inputs.environment == 'production'
    runs-on: ubuntu-latest
    environment:
      name: production-approval
    steps:
      - name: Production deployment approved
        run: echo "✓ Production deployment approved by ${{ github.actor }}"

  # Job 5: Deploy to Production (Canary)
  deploy_production:
    needs: [validate_model, approve_production]
    if: github.event.inputs.environment == 'production'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.8'
      
      - name: Install dependencies
        run: |
          pip install boto3 sagemaker pyyaml
      
      - name: Execute canary deployment
        run: |
          python src/deployment/progressive_deployment.py \
            --strategy ${{ github.event.inputs.deployment_strategy }} \
            --model-package-arn ${{ needs.validate_model.outputs.model_package_arn }} \
            --endpoint-name diabetes-classifier-prod \
            --phases "5,60;25,120;50,240;100,0"
      
      - name: Update model registry status
        run: |
          aws sagemaker update-model-package \
            --model-package-arn ${{ needs.validate_model.outputs.model_package_arn }} \
            --model-approval-status Production
          
          aws sagemaker add-tags \
            --resource-arn ${{ needs.validate_model.outputs.model_package_arn }} \
            --tags Key=DeployedBy,Value=${{ github.actor }} \
                   Key=DeploymentDate,Value=$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
                   Key=Environment,Value=production

  # Job 6: Post-Deployment Monitoring
  post_deployment_monitoring:
    needs: deploy_production
    runs-on: ubuntu-latest
    steps:
      - name: Monitor for 1 hour
        run: |
          echo "Monitoring production endpoint for 1 hour..."
          python scripts/monitor_deployment.py \
            --endpoint-name diabetes-classifier-prod \
            --duration-minutes 60 \
            --alert-on-error
```

---

## 📊 Comparison: Current vs. Production-Grade

| Feature | Current System | Production-Grade | Implementation Effort |
|---------|---------------|------------------|----------------------|
| **Approval Workflow** | Manual, single-stage | Multi-stage automated | 2 weeks |
| **Testing** | None | Unit + Integration + Load | 2-3 weeks |
| **Deployment Strategy** | Direct replace | Canary/Blue-Green | 2 weeks |
| **Rollback** | Manual | Automated triggers | 1 week |
| **Environments** | 1 (prod) | 3 (dev, staging, prod) | 1 week |
| **Monitoring** | Basic CloudWatch | Comprehensive + alerting | 1-2 weeks |
| **Model Metadata** | Basic | Full lineage tracking | 1 week |
| **A/B Testing** | None | Built-in | 2 weeks |
| **Cost** | $84/month | $350/month (3 environments) | - |
| **Risk** | High | Very Low | - |

**Total Implementation Time:** 8-12 weeks for full production-grade system

---

## 🚀 Recommended Implementation Phases

### Phase 1 (Weeks 1-3): Foundation
```yaml
Priority: Critical
Tasks:
  - ✅ Enhanced model metadata in registry
  - ✅ Multi-environment configuration (dev, staging, prod)
  - ✅ Basic integration tests
  - ✅ CI/CD pipeline with manual approval gates
```

### Phase 2 (Weeks 4-6): Advanced Deployment
```yaml
Priority: High
Tasks:
  - ✅ Canary deployment implementation
  - ✅ Automated rollback on errors
  - ✅ Load testing framework
  - ✅ CloudWatch alarms for deployment monitoring
```

### Phase 3 (Weeks 7-9): Testing & Validation
```yaml
Priority: Medium
Tasks:
  - ✅ Shadow mode testing
  - ✅ A/B testing framework
  - ✅ Performance benchmarking
  - ✅ Security testing (penetration, compliance)
```

### Phase 4 (Weeks 10-12): Advanced Features
```yaml
Priority: Nice-to-have
Tasks:
  - ✅ Blue/green deployment
  - ✅ Feature flags for model switching
  - ✅ Cost optimization automation
  - ✅ Self-healing endpoints
```

---

## 💡 Quick Wins (Implement First)

### 1. Enhanced Model Metadata (1 day)
Add git commit SHA and data version to model registration

### 2. Integration Tests (2 days)
Create basic endpoint health checks

### 3. Staging Environment (3 days)
Duplicate production with smaller instances

### 4. Manual Approval Gate (1 day)
Add GitHub Environment protection rule

### 5. CloudWatch Alarms (1 day)
Alert on high error rates

---

## 🎯 Success Metrics

Track these KPIs to measure improvement:

```yaml
Deployment Metrics:
  - Deployment frequency: > 1 per week
  - Lead time for changes: < 1 day
  - Mean time to recovery: < 1 hour
  - Change failure rate: < 5%

Model Performance:
  - Model accuracy: > 0.80
  - Prediction latency p95: < 500ms
  - Endpoint availability: > 99.9%
  - Cost per 1000 predictions: < $0.10

Quality Metrics:
  - Automated test coverage: > 80%
  - Production incidents: < 1 per month
  - Rollback success rate: 100%
  - Time to detect issues: < 5 minutes
```

---

## 📚 Additional Resources

- [AWS SageMaker MLOps Best Practices](https://docs.aws.amazon.com/sagemaker/latest/dg/mlops.html)
- [Model Registry Guide](https://docs.aws.amazon.com/sagemaker/latest/dg/model-registry.html)
- [Canary Deployments on AWS](https://aws.amazon.com/blogs/compute/bluegreen-and-canary-deployments-on-aws/)
- [MLOps Maturity Model](https://ml-ops.org/content/mlops-principles)

---

**Next Steps:** Choose your implementation phase and I can help you build it step by step!
