# Quick Start: Production-Grade Deployment in Dev Environment

**Branch:** `feature/production-grade-deployment`  
**Time to complete:** 30-60 minutes  
**Goal:** Implement automated multi-stage deployment with testing and monitoring

---

## 🎯 What You're Getting

### Before (Current State)
```
Training → Register → Manual Deploy → Hope it works ❌
```

### After (Production-Grade)
```
Training → Register → Dev Auto-Deploy → Integration Tests → 
Staging Auto-Deploy → Load Tests → Manual Approval → 
Production Deploy → Monitoring Alarms ✅
```

---

## 📋 Prerequisites

- ✅ AWS account with SageMaker access
- ✅ GitHub repository with Actions enabled
- ✅ Existing model in Model Registry (approved)
- ✅ AWS credentials configured in GitHub Secrets

---

## 🚀 Step-by-Step Setup

### Step 1: Review New Files (2 minutes)

You now have these new files in the `feature/production-grade-deployment` branch:

```
src/model_registry/
  └── enhanced_registration.py          # Git SHA + metadata tracking

tests/integration/
  └── test_endpoint_deploy.py           # 8 comprehensive tests

scripts/
  └── setup_cloudwatch_alarms.py        # Automated alarm setup

.github/workflows/
  └── multi_stage_deployment.yml        # Dev → Staging → Prod pipeline

config/
  └── environment_config.yaml            # Already has staging config
```

### Step 2: Deploy to Dev Environment (10 minutes)

**Option A: Using existing approved model**

```bash
# 1. Make sure you're on the feature branch
git status  # Should show: feature/production-grade-deployment

# 2. Find your approved model version
aws sagemaker list-model-packages \
  --model-package-group-name mlops-diabetes-model-group-dev \
  --model-approval-status Approved \
  --query 'ModelPackageSummaryList[0].[ModelPackageArn,CustomerMetadataProperties.model_version]' \
  --output table

# 3. Deploy to dev using Python
python src/deployment/deploy.py \
  --environment dev \
  --endpoint-name diabetes-classifier-dev

# This will create a small ml.t2.medium endpoint for cost-effective testing
```

**Option B: Train a new model first**

```bash
# 1. Run the training pipeline
python pipelines/training_pipeline.py \
  --environment dev \
  --execute

# 2. Wait for pipeline to complete (~15-20 minutes)
# Check progress in SageMaker Console → Pipelines

# 3. Once approved, deploy as shown in Option A
```

### Step 3: Run Integration Tests (5 minutes)

```bash
# Install test dependencies
pip install pytest boto3

# Run all integration tests
pytest tests/integration/test_endpoint_deploy.py \
  --endpoint-name diabetes-classifier-dev \
  -v

# Expected output:
# ✓ test_endpoint_exists_and_in_service
# ✓ test_basic_inference
# ✓ test_response_schema
# ✓ test_prediction_accuracy
# ✓ test_latency_sla
# ✓ test_concurrent_requests
# ✓ test_invalid_input_handling
# ✓ test_data_capture_enabled
```

### Step 4: Setup CloudWatch Alarms (3 minutes)

```bash
# Create alarms for dev endpoint
python scripts/setup_cloudwatch_alarms.py \
  --endpoint-name diabetes-classifier-dev \
  --environment dev \
  --region us-east-1

# This creates 4 alarms:
# 1. High error rate (>10% for dev)
# 2. High latency (>2000ms for dev)
# 3. No traffic detection
# 4. Model invocation errors

# Subscribe to SNS topic to receive alerts:
# aws sns subscribe \
#   --topic-arn <SNS_TOPIC_ARN_FROM_OUTPUT> \
#   --protocol email \
#   --notification-endpoint your-email@example.com
```

### Step 5: Test the Automated Workflow (10 minutes)

**Option 1: GitHub Actions (Recommended)**

1. **Push the branch:**
   ```bash
   git add -A
   git commit -m "feat: add production-grade deployment pipeline"
   git push origin feature/production-grade-deployment
   ```

2. **Trigger workflow:**
   - Go to GitHub → Actions → "Multi-Stage Production Deployment"
   - Click "Run workflow"
   - Select branch: `feature/production-grade-deployment`
   - Enter model version (e.g., "1.0.0")
   - Click "Run workflow"

3. **Watch the pipeline:**
   ```
   Stage 1: Validate Model ✅
   Stage 2: Deploy Dev    ✅ (auto-runs tests)
   Stage 3: Deploy Staging ✅ (auto-runs load tests)
   Stage 4: Approve Production ⏸️ (manual approval)
   Stage 5: Deploy Production ✅ (after approval)
   ```

**Option 2: Local Testing**

```bash
# Test dev deployment locally
python src/deployment/deploy.py \
  --environment dev \
  --endpoint-name diabetes-classifier-dev

# Test integration tests
pytest tests/integration/test_endpoint_deploy.py \
  --endpoint-name diabetes-classifier-dev \
  -v

# Test alarm setup
python scripts/setup_cloudwatch_alarms.py \
  --endpoint-name diabetes-classifier-dev \
  --environment dev
```

---

## 📊 What to Check

### 1. Endpoint Status
```bash
aws sagemaker describe-endpoint \
  --endpoint-name diabetes-classifier-dev \
  --query '[EndpointStatus,EndpointConfigName,CreationTime]' \
  --output table
```

### 2. CloudWatch Alarms
```bash
aws cloudwatch describe-alarms \
  --alarm-name-prefix "diabetes-classifier-dev" \
  --query 'MetricAlarms[*].[AlarmName,StateValue]' \
  --output table
```

### 3. Test Predictions
```bash
# Create a test file
echo "6,148,72,35,0,33.6,0.627,50" > test_input.csv

# Invoke endpoint
aws sagemaker-runtime invoke-endpoint \
  --endpoint-name diabetes-classifier-dev \
  --content-type text/csv \
  --body fileb://test_input.csv \
  output.json

# View result
cat output.json
# Expected: probability between 0 and 1
```

### 4. View Metrics in CloudWatch
```bash
# Open CloudWatch console
# https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#metricsV2:

# Look for metrics:
# - AWS/SageMaker → Invocations
# - AWS/SageMaker → ModelLatency
# - AWS/SageMaker → Invocation4XXErrors
# - AWS/SageMaker → Invocation5XXErrors
```

---

## 🎨 Customization Options

### Adjust Test Thresholds

Edit `tests/integration/test_endpoint_deploy.py`:

```python
# Line ~95: Accuracy threshold
assert accuracy >= 0.5  # Change to 0.7 for stricter validation

# Line ~130: Latency SLA
assert p95 < 1000  # Change to 500 for production-like SLA
```

### Adjust Alarm Thresholds

Edit `scripts/setup_cloudwatch_alarms.py`:

```python
# Line ~180: Dev thresholds
'dev': {
    'error_rate': 10.0,   # Change to 5.0 for stricter
    'latency_ms': 2000,   # Change to 1000 for stricter
    'model_errors': 20    # Change to 10 for stricter
}
```

### Add More Environments

Edit `config/environment_config.yaml`:

```yaml
# Add a new environment
testing:
  aws:
    region: us-east-1
  sagemaker:
    endpoint:
      endpoint_name: diabetes-classifier-test
      instance_type: ml.t2.medium
      initial_instance_count: 1
```

---

## 🧪 Testing Checklist

- [ ] Endpoint deployed successfully to dev
- [ ] Integration tests pass (all 8 tests)
- [ ] CloudWatch alarms created (4 alarms)
- [ ] Test prediction returns valid probability
- [ ] Metrics visible in CloudWatch console
- [ ] SNS topic subscribed for alerts (optional)
- [ ] GitHub Actions workflow runs successfully

---

## 🐛 Troubleshooting

### Issue: Tests fail with "Endpoint not found"

**Solution:**
```bash
# Check if endpoint exists
aws sagemaker list-endpoints --query 'Endpoints[*].EndpointName'

# If missing, deploy again:
python src/deployment/deploy.py --environment dev --endpoint-name diabetes-classifier-dev
```

### Issue: "Resource limit exceeded"

**Solution:**
```bash
# You have too many endpoints running. List them:
aws sagemaker list-endpoints --output table

# Delete old ones:
python scripts/cleanup_old_endpoints.py --keep 2
```

### Issue: Latency test fails

**Solution:**
```bash
# This is normal for first deployment (cold start)
# Run test again after 5 minutes:
pytest tests/integration/test_endpoint_deploy.py::TestEndpointDeployment::test_latency_sla \
  --endpoint-name diabetes-classifier-dev \
  -v
```

### Issue: Model package not found

**Solution:**
```bash
# Check approved models:
aws sagemaker list-model-packages \
  --model-package-group-name mlops-diabetes-model-group-dev \
  --model-approval-status Approved

# If none exist, train a model first:
python pipelines/training_pipeline.py --environment dev --execute
```

---

## 📈 Next Steps

### 1. Deploy to Staging (Optional but Recommended)

```bash
# Deploy to staging with production-like config
python src/deployment/deploy.py \
  --environment staging \
  --endpoint-name diabetes-classifier-staging

# Run load tests
pytest tests/integration/test_endpoint_deploy.py::TestEndpointDeployment::test_latency_sla \
  --endpoint-name diabetes-classifier-staging \
  -v
```

### 2. Merge to Main Branch

After testing in feature branch:

```bash
# Create pull request
git push origin feature/production-grade-deployment

# Go to GitHub → Pull Requests → Create PR
# Title: "feat: Add production-grade deployment pipeline"
# Description: Link to this guide

# After review and approval, merge to main
```

### 3. Setup Production Deployment

```bash
# Configure GitHub Environment Protection
# GitHub → Settings → Environments → New environment
# Name: production-approval
# Required reviewers: Add team members
# Save protection rules

# Now production deploys require manual approval
```

### 4. Monitor and Iterate

```bash
# Check CloudWatch metrics daily
# Review alarm notifications
# Adjust thresholds based on actual traffic
# Add more tests as needed
```

---

## 💰 Cost Estimate (Dev Environment)

```
Dev Endpoint (ml.t2.medium):
  - Hourly: $0.065/hour
  - Daily: $1.56/day
  - Monthly: ~$47/month

CloudWatch:
  - Alarms (4): $0.40/month
  - Metrics: Free tier
  - Logs: ~$1/month

Total: ~$48/month for dev environment
```

**Cost Savings Tips:**
- Stop dev endpoint when not in use
- Use spot instances for training
- Set auto-shutdown for overnight

---

## 📚 Additional Resources

- [Full Production Guide](./PRODUCTION_MODEL_REGISTRY_DEPLOYMENT.md)
- [API Exposure Best Practices](./INFERENCE_API_BEST_PRACTICES.md)
- [Training Pipeline Mind Map](./TRAINING_PIPELINE_MINDMAP.md)
- [AWS SageMaker Documentation](https://docs.aws.amazon.com/sagemaker/)

---

## ✅ Success Criteria

You've successfully implemented production-grade deployment when:

1. ✅ Dev endpoint deploys automatically
2. ✅ All integration tests pass
3. ✅ CloudWatch alarms are active
4. ✅ GitHub Actions workflow completes
5. ✅ Metrics visible in CloudWatch
6. ✅ Can make predictions via API

---

## 🎉 Congratulations!

You now have:
- ✅ Automated multi-stage deployment
- ✅ Comprehensive integration testing
- ✅ Production-grade monitoring
- ✅ Git-tracked model lineage
- ✅ CloudWatch alerting
- ✅ Safe deployment pipeline

**Time to celebrate!** 🎊 Your MLOps pipeline is now production-ready!

---

**Questions?** Check the troubleshooting section or create a GitHub issue.
