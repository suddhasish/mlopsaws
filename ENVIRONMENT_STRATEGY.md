# 🌍 Multi-Environment MLOps Strategy

## Overview

This project implements a **3-tier environment strategy** for enterprise-grade MLOps:

```
DEV → STAGING → PRODUCTION
```

Each environment has distinct configurations, approval processes, and deployment strategies to ensure reliability and compliance.

---

## 📋 Environment Characteristics

### 🔧 Development (DEV)
**Purpose**: Experimentation, rapid iteration, feature development

| Aspect | Configuration |
|--------|---------------|
| **Approval** | Auto-approved (models deploy immediately) |
| **Quality Gates** | Lower thresholds (Accuracy ≥ 0.70, F1 ≥ 0.65, ROC-AUC ≥ 0.75) |
| **Infrastructure** | Small instances (ml.t3.medium, ml.t2.medium) |
| **Cost Optimization** | Spot instances enabled, no autoscaling |
| **Monitoring** | Optional, every 12 hours |
| **Model Registry** | `diabetes-classification-models-dev` |

**Use Cases**:
- Testing new features
- Algorithm experimentation
- Data pipeline development
- Quick prototyping

**Deployment Command**:
```bash
python pipelines/training_pipeline.py --environment dev
```

---

### 🎯 Staging (STG)
**Purpose**: Pre-production validation, integration testing

| Aspect | Configuration |
|--------|---------------|
| **Approval** | Manual approval required (PendingManualApproval) |
| **Quality Gates** | Production-like (Accuracy ≥ 0.75, F1 ≥ 0.70, ROC-AUC ≥ 0.80) |
| **Infrastructure** | Production-like instances (ml.m5.xlarge, ml.m5.large) |
| **Cost Optimization** | Spot instances, limited autoscaling (1-3 instances) |
| **Monitoring** | Full monitoring, every 6 hours |
| **Model Registry** | `diabetes-classification-models-staging` |

**Use Cases**:
- Final validation before production
- Performance benchmarking
- Integration testing
- Stakeholder demos

**Deployment Command**:
```bash
python pipelines/training_pipeline.py --environment staging
```

---

### 🚀 Production (PROD)
**Purpose**: Serving live traffic, business-critical operations

| Aspect | Configuration |
|--------|---------------|
| **Approval** | **STRICT manual approval** (2-stage gate) |
| **Quality Gates** | Highest standards (Accuracy ≥ 0.78, F1 ≥ 0.73, ROC-AUC ≥ 0.82) |
| **Infrastructure** | High-performance (ml.m5.2xlarge, ml.m5.xlarge) |
| **High Availability** | 2 instances minimum, autoscaling (2-10) |
| **Monitoring** | Real-time, hourly schedules, alerting |
| **Model Registry** | `diabetes-classification-models-prod` |
| **Deployment Strategy** | Blue/green with canary (10% traffic rollout) |
| **Rollback** | Automatic on failure |

**Use Cases**:
- Live predictions for end users
- Business-critical decisions
- Compliance and audit requirements

**Deployment Command**:
```bash
python pipelines/training_pipeline.py --environment production
```

---

## 🔐 Model Approval Workflow

### DEV Environment
```
Train → Automated Quality Check → ✅ Auto-Approve → Deploy
```
- **Gate**: Accuracy ≥ 0.70, F1 ≥ 0.65, ROC-AUC ≥ 0.75
- **Action**: Immediate deployment if metrics pass
- **Rejection**: Model NOT registered if ANY metric fails

### STAGING Environment
```
Train → Automated Quality Check → Manual Review → ✅ Approve → Deploy
```
- **Gate 1 (Automated)**: Accuracy ≥ 0.75 AND F1 ≥ 0.70 AND ROC-AUC ≥ 0.80
- **Gate 2 (Manual)**: Data scientist reviews metrics, feature importance, confusion matrix
- **Action**: Deploy to staging endpoint after approval
- **Rejection**: Model NOT registered if ANY automated check fails

### PRODUCTION Environment
```
Train → Automated Quality Check → Manual Review → Baseline Comparison → ✅ Approve → Canary Deploy
```
- **Gate 1 (Automated)**: Accuracy ≥ 0.78 AND F1 ≥ 0.73 AND ROC-AUC ≥ 0.82
- **Gate 2 (Baseline Comparison)**: New model must outperform current production model
- **Gate 3 (Manual)**: Senior data scientist + ML engineer review
- **Gate 4 (Canary)**: 10% traffic for 5 minutes → 50% → 100%
- **Action**: Blue/green deployment with automatic rollback on errors
- **Rejection**: Model NOT registered if ANY check fails

---

## 📊 Quality Gate Matrix

| Environment | Accuracy | F1-Score | ROC-AUC | Approval | Baseline Check |
|-------------|----------|----------|---------|----------|----------------|
| **DEV**     | ≥ 0.70   | ≥ 0.65   | ≥ 0.75  | Auto     | No             |
| **STAGING** | ≥ 0.75   | ≥ 0.70   | ≥ 0.80  | Manual   | No             |
| **PROD**    | ≥ 0.78   | ≥ 0.73   | ≥ 0.82  | Manual   | **Yes**        |

### ❌ What Happens if Quality Gates Fail?

```python
# In pipelines/training_pipeline.py (create_condition_step method)

if not (accuracy >= threshold AND f1 >= threshold AND roc_auc >= threshold):
    # Model is NOT registered to Model Registry
    # Pipeline stops before registration step
    # CloudWatch logs capture failure reason
    # SNS notification sent to ML team (if configured)
    logger.error(f"Model failed quality gates: accuracy={accuracy}, f1={f1}, roc_auc={roc_auc}")
    return None  # No model registration
```

**Result**: The conditional step (`ConditionStep`) has `if_steps=[step_register]` and `else_steps=[]`, meaning:
- ✅ If ALL conditions pass → Model registered to registry
- ❌ If ANY condition fails → Pipeline stops, NO registration happens

---

## 🚀 Deployment Strategy per Environment

### DEV: Direct Deployment
```
Train → Register → Deploy → Monitor (optional)
```
- Single endpoint: `diabetes-classifier-dev-endpoint`
- No traffic splitting
- Overwrite existing endpoint

### STAGING: Blue/Green Deployment
```
Train → Register → Create Green Endpoint → Test → Switch Traffic → Delete Blue
```
- Blue endpoint: `diabetes-classifier-staging-blue`
- Green endpoint: `diabetes-classifier-staging-green`
- 100% traffic switch after validation

### PRODUCTION: Canary Deployment
```
Train → Register → Create Canary → 10% Traffic → Monitor → 50% → 100% → Delete Old
```
- Main endpoint: `diabetes-classifier-prod`
- Canary variant: `diabetes-classifier-prod-canary`
- Gradual rollout: 10% → 30% → 50% → 100% (5-minute intervals)
- **Automatic rollback** if error rate > 1% or latency > 500ms

---

## 🔄 Promotion Workflow

### DEV → STAGING
```bash
# 1. Train in DEV
python pipelines/training_pipeline.py --environment dev

# 2. If model performs well, retrain in STAGING with same code
python pipelines/training_pipeline.py --environment staging

# 3. Manually approve in SageMaker Console:
# Model Registry → diabetes-classification-models-staging → Pending → Approve
```

### STAGING → PRODUCTION
```bash
# 1. Train in STAGING
python pipelines/training_pipeline.py --environment staging

# 2. Validate thoroughly (integration tests, load tests)
pytest tests/integration/ --env staging

# 3. If all tests pass, retrain in PRODUCTION
python pipelines/training_pipeline.py --environment production

# 4. Manually approve with senior review:
# Model Registry → diabetes-classification-models-prod → Pending → Approve
```

---

## 🛠️ CI/CD Integration

### GitHub Actions Environment Strategy

```yaml
# .github/workflows/mlops_pipeline.yaml

jobs:
  dev-deployment:
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    environment: dev  # No approval required
    steps:
      - name: Deploy to DEV
        run: python pipelines/training_pipeline.py --environment dev

  staging-deployment:
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: staging  # GitHub environment approval
    steps:
      - name: Deploy to STAGING
        run: python pipelines/training_pipeline.py --environment staging

  production-deployment:
    if: github.event_name == 'release'
    runs-on: ubuntu-latest
    environment: production  # Strict GitHub approval + SageMaker approval
    steps:
      - name: Deploy to PRODUCTION
        run: python pipelines/training_pipeline.py --environment production
```

### Branch Strategy
- `develop` → Auto-deploy to DEV
- `main` → Deploy to STAGING with approval
- `release/*` → Deploy to PRODUCTION with double approval

---

## 📁 Configuration Files

```
config/
├── config.yaml                    # Base configuration (backward compatible)
├── environment_config.yaml        # Environment-specific overrides
├── dev_config.yaml                # DEV-only settings (optional)
├── staging_config.yaml            # STAGING-only settings (optional)
└── production_config.yaml         # PROD-only settings (optional)
```

### Usage in Code
```python
import yaml

# Load environment-specific config
env = os.getenv('MLOPS_ENV', 'dev')
with open(f'config/environment_config.yaml') as f:
    config = yaml.safe_load(f)[env]

# Example: Get approval status
approval_status = config['sagemaker']['model_registry']['approval_status']
# DEV: "Approved"
# STAGING: "PendingManualApproval"
# PROD: "PendingManualApproval"
```

---

## 💰 Cost Comparison

| Environment | Monthly Cost (Estimate) | Use Case |
|-------------|-------------------------|----------|
| **DEV**     | $50-100                | 8 hours/day, 5 days/week |
| **STAGING** | $150-300               | 24/7 uptime, low traffic |
| **PROD**    | $500-1500              | 24/7 HA, high traffic, monitoring |

**Cost Optimization Tips**:
- DEV: Use spot instances, shut down endpoints when not in use
- STAGING: Use spot instances, scale down autoscaling limits
- PROD: Reserved instances for base capacity, spot for autoscaling

---

## 🔍 Monitoring & Alerting per Environment

### DEV
- CloudWatch logs only
- No alerts
- Manual drift checks

### STAGING
- CloudWatch logs + metrics
- Email alerts for failures
- Automated drift detection (every 6 hours)

### PRODUCTION
- Full observability stack:
  - CloudWatch metrics (latency, error rate, invocations)
  - Model Monitor (data quality, drift, bias)
  - SNS alerts (email, Slack, PagerDuty)
  - Hourly drift detection
  - Automatic retraining triggers

---

## ✅ Manual Approval Process

### How to Approve Models in SageMaker Console

1. **Navigate to Model Registry**:
   ```
   AWS Console → SageMaker → Model Registry → [environment]-model-package-group
   ```

2. **Review Pending Model**:
   - Click on model with status "PendingManualApproval"
   - Review metrics: Accuracy, F1, ROC-AUC, Confusion Matrix
   - Check training job details and hyperparameters
   - Validate data lineage (S3 paths, dataset version)

3. **Approve or Reject**:
   - ✅ **Approve**: Model becomes eligible for deployment
   - ❌ **Reject**: Model blocked from deployment, add rejection comments

4. **Deployment** (after approval):
   ```bash
   python src/deployment/deploy.py --environment [dev|staging|production]
   ```

---

## 🚨 Emergency Rollback

### Production Rollback Procedure
```bash
# Option 1: Automatic rollback (if canary deployment fails)
# CloudWatch alarms trigger automatic rollback to previous model

# Option 2: Manual rollback via CLI
aws sagemaker update-endpoint \
  --endpoint-name diabetes-classifier-prod \
  --endpoint-config-name diabetes-classifier-prod-previous

# Option 3: Rollback via Python script
python src/deployment/rollback.py --environment production --to-version v1.2.3
```

---

## 📚 Best Practices

1. **Never Skip Environments**: Always promote DEV → STAGING → PROD
2. **Automated Testing**: Run integration tests in STAGING before PROD
3. **Feature Flags**: Use feature flags for gradual feature rollout
4. **Audit Logs**: Maintain approval logs for compliance (SageMaker tracks this)
5. **Disaster Recovery**: Keep 3 approved models in PROD registry for quick rollback
6. **Documentation**: Update this file when changing thresholds or processes

---

## 🎯 Quick Reference Commands

```bash
# Set environment variable (choose one)
export MLOPS_ENV=dev
export MLOPS_ENV=staging
export MLOPS_ENV=production

# Train and deploy to environment
python pipelines/training_pipeline.py --environment $MLOPS_ENV

# Deploy approved model
python src/deployment/deploy.py --environment $MLOPS_ENV

# Check model registry status
aws sagemaker list-model-packages \
  --model-package-group-name diabetes-classification-models-$MLOPS_ENV

# Approve pending model
aws sagemaker update-model-package \
  --model-package-arn <ARN> \
  --model-approval-status Approved
```

---

## 📞 Support

- **DEV Issues**: Self-service, check CloudWatch logs
- **STAGING Issues**: Contact ML team via Slack #ml-staging
- **PROD Issues**: Page on-call ML engineer via PagerDuty

---

**Last Updated**: December 2024  
**Owner**: MLOps Team  
**Review Cycle**: Quarterly
