# Quick Start: Production-Grade Dev Environment

**🚀 Deploy in 15 minutes!**

This guide shows you how to deploy the automated multi-stage MLOps pipeline to your **dev environment** today.

---

## ✅ What You Get

- ✅ **Automated Dev Deployment** - Deploy on every model approval
- ✅ **Integration Tests** - 8 automated tests run after each deployment
- ✅ **Model Metadata Tracking** - Git SHA, data version, semantic versioning
- ✅ **CloudWatch Alarms** - Auto-alert on errors/latency issues
- ✅ **Multi-Stage Pipeline** - Dev → Staging → Production path ready

---

## 📋 Prerequisites

1. Approved model in SageMaker Model Registry
2. AWS credentials configured in GitHub Secrets
3. Python 3.8+ installed locally (for testing)

---

## 🚀 Deployment Steps

### Step 1: Configure GitHub Environment (2 minutes)

Add a GitHub Environment for production approval:

1. Go to your repo: **Settings → Environments → New environment**
2. Name: `production-approval`
3. Add required reviewers (yourself or your team)
4. Save

### Step 2: Deploy to Dev (5 minutes)

#### Option A: Using GitHub Actions (Recommended)

1. Go to **Actions → Multi-Stage Model Deployment**
2. Click **Run workflow**
3. Select:
   - Target environment: **dev**
   - Model package ARN: (leave empty to use latest)
4. Click **Run workflow**

The workflow will:
- ✅ Get latest approved model
- ✅ Deploy to dev endpoint
- ✅ Run 8 integration tests
- ✅ Tag model as "dev-tested"

#### Option B: Manual Deployment

```bash
# Deploy to dev
python src/deployment/deploy.py \
  --environment dev \
  --endpoint-name diabetes-classifier-dev \
  --wait-for-completion

# Run tests
pytest tests/integration/test_endpoint.py \
  --endpoint-name diabetes-classifier-dev \
  -v
```

### Step 3: Setup CloudWatch Alarms (3 minutes)

```bash
# Setup alarms for dev endpoint
python scripts/setup_cloudwatch_alarms.py \
  --endpoint-name diabetes-classifier-dev \
  --environment dev \
  --email your-email@example.com \
  --region us-east-1

# Confirm the email subscription (check your inbox)
```

### Step 4: Verify Everything Works (5 minutes)

```bash
# Run full test suite
pytest tests/integration/test_endpoint.py \
  --endpoint-name diabetes-classifier-dev \
  -v

# Test manual prediction
python -c "
import boto3
runtime = boto3.client('sagemaker-runtime', region_name='us-east-1')
response = runtime.invoke_endpoint(
    EndpointName='diabetes-classifier-dev',
    ContentType='text/csv',
    Body='6,148,72,35,0,33.6,0.627,50'
)
import json
result = json.loads(response['Body'].read())
print(f'Prediction probability: {result:.4f}')
print(f'Prediction class: {1 if result >= 0.5 else 0}')
"
```

---

## 🎯 What Happens Next?

### Automatic Dev Deployments

Every time a model passes quality gates in training:
1. **Auto-registers** to dev model registry
2. **Auto-deploys** to `diabetes-classifier-dev` endpoint
3. **Auto-tests** with 8 integration tests
4. **Auto-tags** model as "dev-tested"

### Promotion to Staging (When Ready)

```bash
# Deploy to staging (auto after dev tests pass)
# Go to GitHub Actions → Run workflow → Select "staging"
```

### Promotion to Production (Requires Approval)

```bash
# Deploy to production (requires manual approval)
# Go to GitHub Actions → Run workflow → Select "production"
# Approve the deployment in GitHub Environments
```

---

## 📊 Monitoring Your Dev Environment

### View Endpoint Status

```bash
# Check endpoint status
aws sagemaker describe-endpoint \
  --endpoint-name diabetes-classifier-dev \
  --region us-east-1

# Get current model version
aws sagemaker describe-endpoint \
  --endpoint-name diabetes-classifier-dev \
  --query 'EndpointConfigName' \
  --output text
```

### View CloudWatch Alarms

Visit: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#alarmsV2:

Your alarms:
- `diabetes-classifier-dev-high-error-rate`
- `diabetes-classifier-dev-high-latency`
- `diabetes-classifier-dev-low-invocations`

### View Metrics Dashboard

```bash
# Get recent invocations
aws cloudwatch get-metric-statistics \
  --namespace AWS/SageMaker \
  --metric-name Invocations \
  --dimensions Name=EndpointName,Value=diabetes-classifier-dev \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum \
  --region us-east-1
```

---

## 🧪 Testing Your Setup

### Run Integration Tests Locally

```bash
# Install test dependencies
pip install pytest boto3

# Run tests
pytest tests/integration/test_endpoint.py \
  --endpoint-name diabetes-classifier-dev \
  -v \
  --tb=short

# Expected output:
# ✓ test_endpoint_exists
# ✓ test_endpoint_responds
# ✓ test_response_format
# ✓ test_prediction_consistency
# ✓ test_known_cases
# ✓ test_response_time
# ✓ test_error_handling
# ✓ test_endpoint_config
```

### Test Alarm Triggers

```bash
# Trigger a test alarm (will clear automatically)
aws cloudwatch set-alarm-state \
  --alarm-name diabetes-classifier-dev-high-error-rate \
  --state-value ALARM \
  --state-reason "Testing alarm notification" \
  --region us-east-1

# Check your email for the alarm notification
```

---

## 📈 Cost Estimate

**Dev Environment Monthly Cost:**

| Resource | Specification | Monthly Cost |
|----------|--------------|--------------|
| Dev Endpoint | ml.t2.medium × 1 | ~$35 |
| CloudWatch Alarms | 3 alarms | $0.30 |
| CloudWatch Logs | 1 GB | $0.50 |
| S3 Storage | 5 GB | $0.12 |
| **Total** | | **~$36/month** |

**To save costs:**
- Delete dev endpoint when not in use
- Re-deploy when needed (takes 5-7 minutes)

```bash
# Delete dev endpoint
aws sagemaker delete-endpoint \
  --endpoint-name diabetes-classifier-dev \
  --region us-east-1

# Re-deploy anytime
python src/deployment/deploy.py --environment dev
```

---

## 🔧 Configuration Files

All configuration is in these files:

### Environment Config
**File:** `config/environment_config.yaml`

```yaml
dev:
  sagemaker:
    endpoint:
      endpoint_name: diabetes-classifier-dev
      instance_type: ml.t2.medium  # Smallest for dev
      auto_deploy: true  # Auto-deploy on approval
  
  model_registry:
    approval_status: Approved  # Auto-approve in dev
    auto_register: true  # Auto-register models
```

### Workflow Config
**File:** `.github/workflows/multi_stage_deployment.yml`

- Dev: Auto-deploys + auto-tests
- Staging: Auto-deploys after dev tests pass
- Production: Requires manual approval

---

## 🎓 Next Steps

### Phase 1: Use Dev Environment (This Week)
- ✅ Deploy models to dev automatically
- ✅ Test with real traffic
- ✅ Iterate quickly

### Phase 2: Add Staging (Next Week)
- Setup staging endpoint
- Run load tests
- Enable shadow mode testing

### Phase 3: Production Deployment (Week 3)
- Configure production approval workflow
- Setup canary deployment
- Enable auto-rollback

---

## 🆘 Troubleshooting

### Deployment Fails

```bash
# Check endpoint status
aws sagemaker describe-endpoint \
  --endpoint-name diabetes-classifier-dev

# Check CloudWatch logs
aws logs tail /aws/sagemaker/Endpoints/diabetes-classifier-dev \
  --follow \
  --region us-east-1
```

### Tests Fail

```bash
# Run tests with more verbose output
pytest tests/integration/test_endpoint.py \
  --endpoint-name diabetes-classifier-dev \
  -vv \
  --tb=long

# Test single test
pytest tests/integration/test_endpoint.py::TestEndpointAvailability::test_endpoint_exists \
  --endpoint-name diabetes-classifier-dev \
  -v
```

### No Alarms Received

```bash
# Check SNS subscription status
aws sns list-subscriptions-by-topic \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:sagemaker-dev-alerts

# Resend confirmation email
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:sagemaker-dev-alerts \
  --protocol email \
  --notification-endpoint your-email@example.com
```

---

## 📞 Support

- **Documentation:** Check `docs/` folder
- **Issues:** Create GitHub issue
- **Architecture:** See `docs/TRAINING_PIPELINE_MINDMAP.md`

---

## ✅ Success Checklist

- [ ] GitHub environment `production-approval` created
- [ ] Dev endpoint deployed successfully
- [ ] Integration tests passing (8/8)
- [ ] CloudWatch alarms configured
- [ ] Email notifications working
- [ ] Manual prediction test successful
- [ ] Model metadata visible in registry

**Congratulations! You now have a production-grade dev environment! 🎉**
