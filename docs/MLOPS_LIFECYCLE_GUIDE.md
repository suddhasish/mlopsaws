# 🔄 Complete MLOps Lifecycle Guide

**How the entire MLOps workflow operates in this project - from code commit to production monitoring**

Last Updated: November 5, 2025

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [The Complete Lifecycle](#the-complete-lifecycle)
3. [Phase 1: Development & Code Changes](#phase-1-development--code-changes)
4. [Phase 2: Infrastructure Deployment](#phase-2-infrastructure-deployment)
5. [Phase 3: ML Pipeline Execution](#phase-3-ml-pipeline-execution)
6. [Phase 4: Model Deployment](#phase-4-model-deployment)
7. [Phase 5: Monitoring & Drift Detection](#phase-5-monitoring--drift-detection)
8. [Phase 6: Retraining & Continuous Improvement](#phase-6-retraining--continuous-improvement)
9. [Automation & CI/CD](#automation--cicd)
10. [Cost Management](#cost-management)

---

## 🎯 Overview

This project implements a **complete, production-ready MLOps lifecycle** for diabetes classification using AWS SageMaker. The workflow is **largely automated** through GitHub Actions, with manual approval gates for production deployments.

### **Key Principles:**

- ✅ **Infrastructure as Code** (Terraform)
- ✅ **Automated Testing** (GitHub Actions)
- ✅ **Multi-Environment** (dev → staging → production)
- ✅ **Continuous Monitoring** (SageMaker Model Monitor + CloudWatch)
- ✅ **Experiment Tracking** (SageMaker Experiments - FREE)
- ✅ **Cost Optimization** (Auto-shutdown, on-demand monitoring)

---

## 🔄 The Complete Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        MLOPS LIFECYCLE OVERVIEW                         │
└─────────────────────────────────────────────────────────────────────────┘

1. CODE CHANGES (Developer)
   ├─ Modify training code, pipelines, or infrastructure
   ├─ Commit to feature branch
   └─ Create Pull Request
         │
         ▼
2. AUTOMATED TESTING (GitHub Actions)
   ├─ Terraform validation
   ├─ Python linting & unit tests
   ├─ Infrastructure plan preview
   └─ PR checks pass? → Merge to main
         │
         ▼
3. INFRASTRUCTURE DEPLOYMENT (Terraform via GitHub Actions)
   ├─ Dev environment (automatic)
   ├─ Staging environment (automatic)
   └─ Production environment (manual approval required)
         │
         ▼
4. ML PIPELINE EXECUTION (SageMaker Pipelines)
   ├─ Data preprocessing (SKLearn Processing Job)
   ├─ Model training (XGBoost Training Job)
   ├─ Model evaluation (Processing Job)
   ├─ Experiment tracking (SageMaker Experiments)
   └─ Quality gates → Pass? → Continue
         │
         ▼
5. MODEL REGISTRATION (SageMaker Model Registry)
   ├─ Register model with metrics
   ├─ Version automatically (v1, v2, v3...)
   └─ Approval status: PendingManualApproval
         │
         ▼
6. MODEL DEPLOYMENT (SageMaker Endpoints)
   ├─ Deploy to dev endpoint (automatic)
   ├─ Deploy to staging endpoint (automatic)
   ├─ Deploy to production endpoint (manual approval)
   └─ Enable data capture for monitoring
         │
         ▼
7. CONTINUOUS MONITORING (Automated)
   ├─ Endpoint health metrics (CloudWatch - FREE)
   ├─ Data drift detection (on-demand - $0.27/check)
   ├─ Model quality monitoring (on-demand - $0.27/check)
   ├─ Statistical drift analysis (FREE)
   └─ Experiment comparison (FREE)
         │
         ▼
8. DRIFT DETECTED? (Automated Decision)
   ├─ YES → Create GitHub issue + Send alert
   │         └─ Trigger retraining workflow
   └─ NO → Continue monitoring
         │
         ▼
9. RETRAINING (Automatic or Manual)
   ├─ Fetch latest production data
   ├─ Re-run ML pipeline (steps 4-6)
   ├─ Compare new model vs current production
   └─ Better performance? → Deploy new version
         │
         ▼
10. CONTINUOUS IMPROVEMENT (Loop back to monitoring)
    └─ Repeat lifecycle continuously
```

---

## 📝 Phase 1: Development & Code Changes

### **What Happens:**

Developers make changes to code, configurations, or infrastructure.

### **Components Involved:**

- **Local Development:**
  - Python scripts (`src/`, `pipelines/`)
  - Terraform files (`infrastructure/terraform/`)
  - Configuration (`config/config.yaml`)
  - Documentation (`docs/`)

### **Typical Changes:**

```python
# Example: Improving model hyperparameters
# File: config/config.yaml

model:
  hyperparameters:
    max_depth: 7        # Changed from 5
    eta: 0.1            # Changed from 0.2
    num_round: 150      # Changed from 100
```

### **Git Workflow:**

```bash
# 1. Create feature branch
git checkout -b feature/improve-hyperparameters

# 2. Make changes
vim config/config.yaml

# 3. Test locally (optional)
python pipelines/training_pipeline.py --environment dev

# 4. Commit changes
git add .
git commit -m "feat: Optimize XGBoost hyperparameters for better accuracy"

# 5. Push to GitHub
git push origin feature/improve-hyperparameters

# 6. Create Pull Request
# GitHub UI → Compare & pull request
```

---

## 🏗️ Phase 2: Infrastructure Deployment

### **What Happens:**

Terraform provisions AWS resources via GitHub Actions.

### **Trigger:**

- Pull Request merged to `main`
- Manual workflow dispatch

### **GitHub Actions Workflow:**

**File:** `.github/workflows/terraform.yml`

```yaml
Workflow Steps:
1. Validate Job (All branches)
   ├─ Checkout code
   ├─ Setup Terraform
   ├─ Terraform fmt check
   ├─ Terraform validate (without S3 backend)
   └─ Post validation results to PR

2. Plan Job (Main branch only)
   ├─ Configure AWS credentials (OIDC)
   ├─ Terraform init (with S3 backend)
   ├─ Terraform plan
   └─ Save plan artifact

3. Apply Job (Main branch only)
   ├─ Download plan artifact
   ├─ Terraform apply (automatic for dev/staging)
   └─ Manual approval required for production
```

### **Resources Created:**

```
AWS Resources (via Terraform):
├─ S3 Buckets
│  ├─ mlops-diabetes-dev-{account-id}
│  ├─ mlops-diabetes-staging-{account-id}
│  └─ mlops-diabetes-production-{account-id}
│
├─ IAM Roles
│  ├─ SageMaker execution role
│  └─ Lambda execution roles
│
├─ SageMaker Resources
│  ├─ Model Package Groups (optional - quota dependent)
│  └─ Monitoring job definitions (if enabled)
│
├─ CloudWatch
│  ├─ Log groups
│  └─ Alarms (errors, latency, traffic)
│
├─ SNS Topics
│  ├─ mlops-diabetes-alerts-{env}
│  └─ mlops-diabetes-critical-{env}
│
├─ EventBridge Rules
│  └─ Scheduled monitoring triggers
│
└─ Budget Alerts
   └─ Monthly budget tracking ($60 limit)
```

### **Environment Deployment Order:**

```
1. Dev Environment (Automatic)
   ├─ Deploys immediately on merge to main
   └─ Used for testing and experiments

2. Staging Environment (Automatic)
   ├─ Deploys after dev succeeds
   └─ Pre-production validation

3. Production Environment (Manual Approval)
   ├─ Requires approval in GitHub Actions
   └─ Production-grade configuration
```

---

## 🤖 Phase 3: ML Pipeline Execution

### **What Happens:**

SageMaker Pipelines orchestrates the complete ML workflow.

### **Trigger:**

- Manual execution: `python pipelines/training_pipeline.py --execute`
- GitHub Actions: After infrastructure deployment
- Automated retraining: When drift detected

### **Pipeline Steps:**

#### **Step 1: Data Preprocessing**

```
SageMaker Processing Job (SKLearn)
├─ Instance: ml.m5.xlarge
├─ Script: src/processing/preprocessing.py
├─ Input: s3://bucket/data/raw/diabetes.csv
└─ Outputs:
   ├─ s3://bucket/data/train/train.csv
   ├─ s3://bucket/data/validation/validation.csv
   ├─ s3://bucket/data/test/test.csv
   └─ s3://bucket/preprocessing/model/scaler.pkl
```

**What it does:**
- Loads raw diabetes dataset
- Handles missing values
- Splits data (70% train, 15% validation, 15% test)
- Applies StandardScaler
- Saves preprocessed datasets to S3

**Duration:** ~5 minutes  
**Cost:** ~$0.10

---

#### **Step 2: Model Training**

```
SageMaker Training Job (XGBoost)
├─ Instance: ml.m5.xlarge
├─ Script: src/training/train.py
├─ Framework: XGBoost 1.5-1
├─ Inputs:
│  ├─ Train data: s3://bucket/data/train/
│  └─ Validation data: s3://bucket/data/validation/
└─ Outputs:
   └─ Model artifact: s3://bucket/models/model.tar.gz
```

**What it does:**
- Trains XGBoost binary classifier
- Hyperparameters from config.yaml
- Early stopping on validation AUC
- **✅ Logs experiment to SageMaker Experiments:**
  - Hyperparameters (max_depth, eta, gamma, etc.)
  - Training metrics (train_auc, validation_auc)
  - Model artifact location
- Saves model to S3

**Duration:** ~10-15 minutes  
**Cost:** ~$0.20

**Experiment Tracking:**
```python
# Automatically tracked in src/training/train.py
tracker = ExperimentTracker('diabetes-classification-experiments')
tracker.log_parameters({
    'max_depth': 5,
    'eta': 0.2,
    'num_round': 100
})
tracker.log_metrics({
    'train_auc': 0.8234,
    'validation_auc': 0.7891
})
```

---

#### **Step 3: Model Evaluation**

```
SageMaker Processing Job (SKLearn)
├─ Instance: ml.m5.xlarge
├─ Script: src/evaluation/evaluate.py
├─ Inputs:
│  ├─ Model: s3://bucket/models/model.tar.gz
│  └─ Test data: s3://bucket/data/test/
└─ Outputs:
   └─ Metrics: s3://bucket/evaluation/evaluation_results.json
```

**What it does:**
- Loads trained model
- Runs predictions on test set
- Calculates metrics:
  - Accuracy
  - Precision
  - Recall
  - F1 Score
  - ROC-AUC
  - Confusion Matrix
- Saves evaluation report to S3

**Duration:** ~3 minutes  
**Cost:** ~$0.05

**Evaluation Results:**
```json
{
  "metrics": {
    "accuracy": 0.7532,
    "precision": 0.7234,
    "recall": 0.7112,
    "f1_score": 0.7172,
    "roc_auc": 0.8156
  },
  "confusion_matrix": [[45, 12], [15, 38]]
}
```

---

#### **Step 4: Experiment Tracking (NEW)**

```
SageMaker Processing Job (SKLearn)
├─ Instance: ml.t3.medium
├─ Script: src/monitoring/track_experiment.py
├─ Inputs:
│  └─ Evaluation results: s3://bucket/evaluation/
└─ Outputs:
   └─ Experiment log: s3://bucket/experiments/
```

**What it does:**
- Reads evaluation results
- **✅ Logs final metrics to SageMaker Experiments:**
  - Accuracy, F1, ROC-AUC, etc.
  - Links model S3 URI
  - Creates complete experiment record
- Generates experiment summary

**Duration:** ~1 minute  
**Cost:** ~$0.01 (uses small instance)

**View Experiments:**
```
AWS Console → SageMaker → Experiments
→ "diabetes-classification-experiments"
→ See all training runs with metrics
```

---

#### **Step 5: Quality Gate Check**

```
Conditional Step
├─ Condition 1: Accuracy >= 0.70
├─ Condition 2: F1 Score >= 0.65
└─ Condition 3: ROC-AUC >= 0.75
    │
    ├─ ALL PASS → Register Model
    └─ ANY FAIL → Pipeline ends (no registration)
```

**What it does:**
- Evaluates model against thresholds
- Only registers models that meet quality criteria
- Prevents poor models from reaching production

**Thresholds (configurable):**
```yaml
# config/config.yaml
evaluation:
  approval_thresholds:
    min_accuracy: 0.70
    min_f1_score: 0.65
    min_roc_auc: 0.75
```

---

#### **Step 6: Model Registration** (Conditional)

```
SageMaker Model Registry
├─ Model Package Group: diabetes-classifier-package-group
├─ Model Version: Automatically incremented (v1, v2, v3...)
├─ Approval Status: PendingManualApproval (staging/prod)
│                    Approved (dev)
└─ Metadata:
   ├─ Metrics (from evaluation)
   ├─ Training job name
   ├─ Model artifact S3 URI
   └─ Timestamp
```

**What it does:**
- Creates versioned model package
- Attaches evaluation metrics
- Sets approval workflow
- Enables model lineage tracking

---

### **Complete Pipeline Execution:**

```bash
# Manual execution
python pipelines/training_pipeline.py --environment dev --execute

# Output:
Creating SageMaker Pipeline
✅ Preprocess step created
✅ Training step created
✅ Evaluation step created
✅ Experiment tracking step created
✅ Registration step created
Pipeline execution started: arn:aws:sagemaker:...
Monitor at: https://console.aws.amazon.com/sagemaker/pipelines
```

**Total Duration:** ~25-30 minutes  
**Total Cost:** ~$0.40-0.50

---

## 🚀 Phase 4: Model Deployment

### **What Happens:**

Approved models are deployed to SageMaker real-time endpoints.

### **Deployment Flow:**

```
Model Registry
    │
    ├─ Model approved?
    │  └─ YES
    │     │
    │     ▼
    ├─ Create SageMaker Model
    │  ├─ Model artifact from S3
    │  ├─ Inference container (XGBoost)
    │  └─ IAM execution role
    │     │
    │     ▼
    ├─ Create Endpoint Configuration
    │  ├─ Instance type: ml.t2.medium (dev)
    │  ├─ Instance count: 1
    │  ├─ Data capture: Enabled (100% in dev, 20% in prod)
    │  └─ Model name + version
    │     │
    │     ▼
    └─ Create/Update Endpoint
       ├─ Endpoint name: mlops-diabetes-endpoint-{env}
       ├─ Initial instance count: 1
       └─ Auto-scaling (optional)
```

### **Deployment Commands:**

```bash
# Automatic (via GitHub Actions after model approval)
# Or manual:

# 1. Get approved model
aws sagemaker list-model-packages \
  --model-package-group-name diabetes-classifier-package-group \
  --model-approval-status Approved

# 2. Deploy model
python src/deployment/deploy.py \
  --model-package-arn arn:aws:sagemaker:... \
  --endpoint-name mlops-diabetes-endpoint-dev
```

### **Endpoint Configuration:**

| Environment | Instance Type | Instances | Data Capture | Auto-Scaling |
|-------------|---------------|-----------|--------------|--------------|
| **Dev** | ml.t2.medium | 1 | 100% | No |
| **Staging** | ml.t2.medium | 1 | 50% | No |
| **Production** | ml.m5.large | 2 | 20% | Yes (1-5) |

### **Cost:**

- **Dev:** $47/month (24/7) or $5/month (with auto-shutdown)
- **Staging:** $47/month (24/7)
- **Production:** $94-470/month (depending on auto-scaling)

### **Testing Endpoint:**

```python
import boto3
import json

runtime = boto3.client('sagemaker-runtime')

# Prepare input
payload = {
    "instances": [
        [6, 148, 72, 35, 0, 33.6, 0.627, 50]  # Sample features
    ]
}

# Invoke endpoint
response = runtime.invoke_endpoint(
    EndpointName='mlops-diabetes-endpoint-dev',
    ContentType='application/json',
    Body=json.dumps(payload)
)

# Get prediction
result = json.loads(response['Body'].read())
print(f"Prediction: {result}")  # 0 = No diabetes, 1 = Diabetes
```

**Response Time:** <100ms  
**Availability:** 99.9%

---

## 📊 Phase 5: Monitoring & Drift Detection

### **What Happens:**

Continuous monitoring detects data drift, model degradation, and endpoint health issues.

### **Monitoring Components:**

#### **1. Endpoint Health Metrics (FREE)**

```
CloudWatch Metrics (Automatic)
├─ ModelInvocations - Request count
├─ ModelLatency - Response time
├─ ModelInvocationErrors - Error rate
├─ CPUUtilization - Resource usage
└─ MemoryUtilization - Memory usage
```

**CloudWatch Alarms:**
- ✅ Errors > 10 in 5 minutes → Send SNS alert
- ✅ Latency > 1000ms → Send SNS alert
- ✅ Invocations > 1000/instance → Scale up

**View Metrics:**
```bash
# Via AWS Console
CloudWatch → Metrics → SageMaker → Endpoints

# Via CLI
aws cloudwatch get-metric-statistics \
  --namespace AWS/SageMaker \
  --metric-name ModelLatency \
  --dimensions Name=EndpointName,Value=mlops-diabetes-endpoint-dev
```

---

#### **2. Data Drift Detection ($0.27/check)**

```
SageMaker Model Monitor (On-Demand)
├─ Baseline: Created from training data
├─ Production data: From endpoint data capture
├─ Statistical tests:
│  ├─ Kolmogorov-Smirnov test (continuous features)
│  ├─ Chi-Square test (categorical features)
│  └─ Jensen-Shannon divergence (distributions)
└─ Violations: Features outside acceptable range
```

**Run Drift Detection:**
```bash
# Manual
python src/monitoring/run_drift_detection.py \
  --endpoint-name mlops-diabetes-endpoint-dev \
  --check-data-drift

# Automated (GitHub Actions - Weekly Monday 9 AM)
GitHub → Actions → MLOps Monitoring Pipeline
  monitoring_type: drift-detection
  environment: dev
```

**Drift Report:**
```json
{
  "drift_detected": true,
  "violations": [
    {
      "feature": "glucose",
      "baseline_mean": 120.5,
      "current_mean": 145.3,
      "drift_score": 0.23,
      "threshold": 0.15
    }
  ]
}
```

**Cost:** $0.27 per check  
**Frequency:** Weekly (recommended) = $1.38/month

---

#### **3. Model Quality Monitoring ($0.27/check)**

```
SageMaker Model Monitor (On-Demand)
├─ Baseline: Evaluation metrics from training
├─ Production metrics: Calculated from ground truth labels
├─ Checks:
│  ├─ Accuracy degradation
│  ├─ Precision/Recall changes
│  └─ F1 score drift
└─ Alert if metrics drop below threshold
```

**Run Quality Check:**
```bash
python src/monitoring/run_drift_detection.py \
  --endpoint-name mlops-diabetes-endpoint-dev \
  --check-model-quality
```

**Quality Report:**
```json
{
  "quality_degradation": true,
  "metrics": {
    "baseline_accuracy": 0.75,
    "current_accuracy": 0.68,
    "degradation": 0.07
  }
}
```

---

#### **4. Statistical Drift Analysis (FREE)**

```
Custom Drift Detection (Offline)
├─ Script: src/monitoring/drift_detection.py
├─ Methods:
│  ├─ Kolmogorov-Smirnov test
│  ├─ Population Stability Index (PSI)
│  └─ Chi-Square test
└─ Runs on GitHub Actions runner (no SageMaker cost)
```

**Run Statistical Drift:**
```bash
python src/monitoring/drift_detection.py \
  --baseline-data s3://bucket/data/train/diabetes.csv \
  --production-data s3://bucket/monitoring/production_data.csv
```

**Cost:** FREE  
**Frequency:** Daily (recommended)

---

#### **5. Experiment Comparison (FREE)**

```
SageMaker Experiments API
├─ Compare all training runs
├─ Find best performing model
├─ Track metric trends over time
└─ Identify hyperparameter impacts
```

**Compare Experiments:**
```python
from src.monitoring.experiment_tracker import ExperimentTracker

tracker = ExperimentTracker('diabetes-classification-experiments')

# Get best run
best = tracker.get_best_run('accuracy', maximize=True)
print(f"Best accuracy: {best['accuracy']:.4f}")

# Compare all runs
tracker.compare_runs()
```

**Cost:** FREE (SageMaker Experiments API is free)  
**Frequency:** On-demand or after each training run

---

### **Monitoring Pipeline (Automated)**

**GitHub Actions Workflow:** `.github/workflows/monitoring_pipeline.yml`

**Triggers:**
- ✅ **Manual:** GitHub → Actions → Run workflow
- ✅ **Scheduled:** Every Monday 9 AM UTC
- ✅ **Event-driven:** After model deployment

**Jobs:**
1. **Check Metrics** (FREE) - CloudWatch endpoint metrics
2. **Drift Detection** ($0.27) - SageMaker data quality
3. **Model Quality** ($0.27) - SageMaker model quality
4. **Statistical Drift** (FREE) - Custom offline analysis
5. **Experiment Tracking** (FREE) - Compare training runs
6. **Generate Report** (FREE) - Summary + notifications
7. **Auto-Retrain Decision** (FREE) - Evaluate retraining need

**Notifications:**
- ✅ Slack webhook (if configured)
- ✅ GitHub issue creation (if drift detected)
- ✅ Email via SNS topics

---

## 🔄 Phase 6: Retraining & Continuous Improvement

### **What Happens:**

When drift is detected or model degrades, automatic or manual retraining is triggered.

### **Retraining Triggers:**

```
Trigger Conditions:
├─ Data drift > 25%
├─ Model accuracy drops > 10%
├─ Manual trigger (GitHub Actions)
└─ Scheduled (monthly)
```

### **Retraining Workflow:**

```
1. Drift/Degradation Detected
   └─ Create GitHub issue with label: "model-retraining"
      │
      ▼
2. Decision Point
   ├─ Automatic: Trigger retraining workflow
   └─ Manual: Review issue → Approve retraining
      │
      ▼
3. Fetch Latest Data
   ├─ Download recent production data
   ├─ Merge with training dataset
   └─ Validate data quality
      │
      ▼
4. Re-run ML Pipeline
   ├─ Same as Phase 3 (all steps)
   ├─ New experiment run tracked
   └─ New model version registered
      │
      ▼
5. Compare Models
   ├─ New model metrics
   ├─ Current production metrics
   └─ Improvement threshold: +2% accuracy
      │
      ▼
6. Deployment Decision
   ├─ Better? → Approve + Deploy
   └─ Worse? → Keep current model
      │
      ▼
7. Gradual Rollout (Production)
   ├─ Canary deployment (10% traffic)
   ├─ Monitor for 24 hours
   ├─ Gradual increase (50%, 100%)
   └─ Rollback if issues detected
```

### **Manual Retraining:**

```bash
# Trigger via GitHub Actions
GitHub → Actions → MLOps Pipeline → Run workflow
  environment: dev
  trigger_retraining: true

# Or via CLI
python pipelines/training_pipeline.py \
  --environment dev \
  --retrain \
  --use-latest-data
```

### **Automatic Retraining:**

**Configured in:** `.github/workflows/monitoring_pipeline.yml`

```yaml
auto-retrain-decision:
  if: |
    needs.drift-detection.outputs.drift_detected == 'true' ||
    needs.model-quality.outputs.degradation_detected == 'true'
  steps:
    - name: Trigger retraining
      uses: actions/github-script@v7
      with:
        script: |
          // Trigger MLOps pipeline workflow
          await github.rest.actions.createWorkflowDispatch({
            workflow_id: 'mlops_pipeline.yaml',
            ref: 'main',
            inputs: {
              environment: 'dev',
              trigger_retraining: 'true'
            }
          })
```

### **Model Versioning:**

```
SageMaker Model Registry
├─ v1 (Baseline) - Accuracy: 0.75
├─ v2 (Retraining #1) - Accuracy: 0.76
├─ v3 (Retraining #2) - Accuracy: 0.78 ← Production
└─ v4 (Retraining #3) - Accuracy: 0.77 (Rejected, worse than v3)
```

### **A/B Testing (Optional):**

```
Production Endpoint
├─ Variant A (90% traffic) - Current production model v3
└─ Variant B (10% traffic) - New model v4
   │
   ├─ Monitor metrics for 48 hours
   ├─ Compare performance
   └─ Decide: Keep v4 or rollback to v3
```

---

## ⚙️ Automation & CI/CD

### **GitHub Actions Workflows:**

#### **1. Terraform Workflow** (`.github/workflows/terraform.yml`)

**Triggers:**
- Push to main
- Pull request

**Jobs:**
- ✅ Validate Terraform syntax
- ✅ Plan infrastructure changes
- ✅ Apply to dev/staging (automatic)
- ✅ Apply to production (manual approval)

---

#### **2. MLOps Pipeline Workflow** (`.github/workflows/mlops_pipeline.yaml`)

**Triggers:**
- Manual workflow dispatch
- After Terraform deployment
- Scheduled (optional)

**Jobs:**
- ✅ Upload data to S3
- ✅ Execute SageMaker pipeline
- ✅ Monitor pipeline execution
- ✅ Deploy approved models

---

#### **3. Monitoring Pipeline Workflow** (`.github/workflows/monitoring_pipeline.yml`)

**Triggers:**
- Manual (on-demand)
- Scheduled (weekly Monday 9 AM)
- After model deployment

**Jobs:**
- ✅ Check endpoint metrics
- ✅ Run drift detection
- ✅ Run model quality checks
- ✅ Statistical drift analysis
- ✅ Experiment comparison
- ✅ Generate monitoring report
- ✅ Auto-retrain decision

---

### **Manual Steps (Intentional):**

**Why manual approval for production?**
- ✅ Human oversight for critical changes
- ✅ Cost control
- ✅ Compliance requirements
- ✅ Risk mitigation

**Manual approval points:**
1. **Production infrastructure deployment**
   - GitHub Actions → Review plan → Approve
2. **Production model deployment**
   - SageMaker Console → Approve model package
3. **Production retraining**
   - Review retraining GitHub issue → Trigger workflow

---

## 💰 Cost Management

### **Monthly Cost Breakdown:**

| Component | Dev | Staging | Production | Total |
|-----------|-----|---------|------------|-------|
| **S3 Storage** | $1 | $1 | $2 | $4 |
| **SageMaker Endpoint** | $47 | $47 | $188 | $282 |
| **Training (monthly)** | $0.50 | $0 | $0 | $0.50 |
| **Monitoring** | $2 | $0 | $5 | $7 |
| **CloudWatch** | $0.30 | $0 | $1 | $1.30 |
| **Budget Alerts** | FREE | FREE | FREE | FREE |
| **Experiments** | $0.05 | $0 | $0.10 | $0.15 |
| **TOTAL** | **$51** | **$48** | **$196** | **$295** |

### **Cost Optimization:**

#### **1. Enable Auto-Shutdown (Saves $840/month)**

```hcl
# infrastructure/terraform/environments/dev/terraform.tfvars
enable_auto_shutdown = true
```

**What it does:**
- Stops endpoints at 7 PM weekdays
- Starts endpoints at 8 AM weekdays
- Keeps endpoints off weekends

**Savings:** ~60% reduction = $840/month saved

---

#### **2. Use On-Demand Monitoring (Saves $191/month)**

```hcl
# Instead of continuous monitoring ($194/month)
enable_sagemaker_monitoring = false  # Default

# Run on-demand via GitHub Actions
# Cost: $0.60 per demo or $2.16/month weekly
```

**Savings:** $194 - $2 = $192/month saved

---

#### **3. Use Spot Instances for Training (Saves 70%)**

```python
# pipelines/training_pipeline.py
xgb_estimator = XGBoost(
    # ...
    use_spot_instances=True,
    max_wait=3600,  # 1 hour max wait
    # ...
)
```

**Savings:** $0.20 → $0.06 per training job

---

#### **4. Right-Size Instances**

| Workload | Instead of | Use | Savings |
|----------|-----------|-----|---------|
| Dev endpoint | ml.m5.large | ml.t2.medium | 68% |
| Preprocessing | ml.m5.2xlarge | ml.m5.xlarge | 50% |
| Training | ml.p3.2xlarge | ml.m5.xlarge | 90% |

---

#### **5. Budget Alerts**

```
AWS Budgets (Configured via Terraform)
├─ Monthly budget: $60 (dev), $80 (staging), $300 (prod)
├─ Alert at 80% ($48, $64, $240)
├─ Alert at 100% (limit reached)
└─ Alert at 120% (overspending)
```

**Notifications:** Email via SNS

---

### **Optimized Monthly Cost:**

| Optimization | Before | After | Savings |
|--------------|--------|-------|---------|
| Auto-shutdown enabled | $295 | $180 | $115 |
| On-demand monitoring | $180 | $170 | $10 |
| Spot instances | $170 | $168 | $2 |
| Right-sized instances | $168 | $150 | $18 |
| **TOTAL** | **$295** | **$150** | **$145/month** |

**Annual savings:** $1,740

---

## 📈 Success Metrics

### **ML Performance:**
- ✅ Model Accuracy: 75-80%
- ✅ F1 Score: 0.70-0.75
- ✅ ROC-AUC: 0.80-0.85
- ✅ Endpoint Latency: <100ms

### **Operational Metrics:**
- ✅ Pipeline Success Rate: >95%
- ✅ Deployment Frequency: Weekly
- ✅ Endpoint Availability: 99.9%
- ✅ Mean Time to Deploy: <30 minutes

### **Cost Metrics:**
- ✅ Monthly AWS Cost: $150-300 (optimized)
- ✅ Cost per Inference: $0.001
- ✅ Training Cost: <$1 per run

### **Quality Metrics:**
- ✅ Drift Detection: Weekly
- ✅ Retraining Frequency: Monthly or on-demand
- ✅ Model Version Tracking: 100%
- ✅ Experiment Tracking: Automatic

---

## 🎓 Learning Outcomes

By following this lifecycle, you'll learn:

✅ **MLOps Fundamentals:** Complete ML lifecycle from code to production  
✅ **AWS SageMaker:** Pipelines, Training, Deployment, Monitoring  
✅ **Infrastructure as Code:** Terraform for reproducible infrastructure  
✅ **CI/CD:** GitHub Actions for automation  
✅ **Monitoring:** Drift detection, model quality, endpoint health  
✅ **Experiment Tracking:** SageMaker Experiments for model comparison  
✅ **Cost Optimization:** Reduce cloud costs while maintaining quality  
✅ **Production Best Practices:** Approval gates, versioning, rollback  

---

## 📚 Related Documentation

- **[COMPLETE_SETUP_GUIDE.md](./COMPLETE_SETUP_GUIDE.md)** - Initial setup
- **[EXPERIMENT_TRACKING_INTEGRATION.md](./EXPERIMENT_TRACKING_INTEGRATION.md)** - Experiment tracking details
- **[MONITORING_PIPELINE_GUIDE.md](./MONITORING_PIPELINE_GUIDE.md)** - Monitoring best practices
- **[DATA_FLOW_ARCHITECTURE.md](./DATA_FLOW_ARCHITECTURE.md)** - Data pipeline architecture
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Common issues and solutions

---

## 🎯 Quick Reference

### **Check Pipeline Status:**
```bash
aws sagemaker list-pipeline-executions \
  --pipeline-name diabetes-classification-pipeline
```

### **View Experiments:**
```
AWS Console → SageMaker → Experiments
→ diabetes-classification-experiments
```

### **Monitor Endpoint:**
```
AWS Console → SageMaker → Endpoints
→ mlops-diabetes-endpoint-dev
```

### **Trigger Retraining:**
```
GitHub → Actions → MLOps Pipeline → Run workflow
```

### **View Costs:**
```
AWS Console → Billing → Cost Explorer
```

---

**🎉 You now understand the complete MLOps lifecycle in this project!**

From code commit to production monitoring, everything is automated, monitored, and cost-optimized. 🚀
