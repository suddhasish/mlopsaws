# 🚀 Automated Monitoring Pipeline - Best Practices Guide

This guide explains how to set up and configure automated monitoring for your MLOps project with both **on-demand** and **scheduled** execution.

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Pipeline Components](#pipeline-components)
3. [Setup Instructions](#setup-instructions)
4. [Execution Modes](#execution-modes)
5. [Cost Optimization](#cost-optimization)
6. [Monitoring Dashboards](#monitoring-dashboards)
7. [Best Practices](#best-practices)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                   MONITORING PIPELINE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  TRIGGERS:                                                      │
│  ├─ Manual (On-Demand)      ────────┐                         │
│  ├─ Scheduled (Weekly)      ────────┤                         │
│  └─ Post-Deployment         ────────┤                         │
│                                      ▼                         │
│  ┌───────────────────────────────────────────────────────┐    │
│  │  Job 1: Endpoint Metrics (FREE - Always Runs)        │    │
│  │  - CloudWatch metrics                                 │    │
│  │  - Health check                                       │    │
│  │  - Error counts & latency                            │    │
│  └───────────────────────────────────────────────────────┘    │
│                          │                                     │
│          ┌───────────────┼───────────────┐                   │
│          ▼               ▼               ▼                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Job 2:      │  │ Job 3:      │  │ Job 4:      │        │
│  │ Data Drift  │  │ Model       │  │ Statistical │        │
│  │ ($0.27)     │  │ Quality     │  │ Drift (FREE)│        │
│  │             │  │ ($0.27)     │  │             │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│          │               │               │                   │
│          └───────────────┼───────────────┘                   │
│                          ▼                                     │
│  ┌───────────────────────────────────────────────────────┐    │
│  │  Job 5: Experiment Tracking (FREE)                    │    │
│  │  - Compare training runs                              │    │
│  │  - Find best model                                    │    │
│  └───────────────────────────────────────────────────────┘    │
│                          │                                     │
│                          ▼                                     │
│  ┌───────────────────────────────────────────────────────┐    │
│  │  Job 6: Generate Report & Notify                      │    │
│  │  - Consolidate results                                │    │
│  │  - Send alerts (Slack/Email)                         │    │
│  │  - Create GitHub issues if drift detected            │    │
│  └───────────────────────────────────────────────────────┘    │
│                          │                                     │
│                          ▼                                     │
│  ┌───────────────────────────────────────────────────────┐    │
│  │  Job 7: Auto-Retrain Decision (Conditional)          │    │
│  │  - Evaluate drift severity                           │    │
│  │  - Trigger retraining if needed                      │    │
│  └───────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧩 Pipeline Components

### **1. Endpoint Metrics (FREE - Always Runs)**
- **What:** CloudWatch metrics from SageMaker endpoint
- **Cost:** $0 (CloudWatch metrics are free for SageMaker)
- **Duration:** ~30 seconds
- **Output:** Health status, error counts, latency metrics

### **2. Data Drift Detection ($0.27/run - Conditional)**
- **What:** SageMaker Model Monitor data quality check
- **Cost:** $0.269/hour × ~1 hour = $0.27
- **Duration:** ~30-60 minutes
- **Output:** Drift report with violations, statistics

### **3. Model Quality Check ($0.27/run - Conditional)**
- **What:** SageMaker Model Monitor model quality check
- **Cost:** $0.269/hour × ~1 hour = $0.27
- **Duration:** ~30-60 minutes
- **Output:** Model performance metrics, degradation alerts

### **4. Statistical Drift (FREE - Always Runs)**
- **What:** Custom statistical tests (KS, PSI, Chi-Square)
- **Cost:** $0 (runs on GitHub Actions runner)
- **Duration:** ~2-5 minutes
- **Output:** Feature-level drift analysis

### **5. Experiment Tracking (FREE - Always Runs)**
- **What:** Compare all training experiment runs
- **Cost:** $0 (SageMaker Experiments API is free)
- **Duration:** ~30 seconds
- **Output:** Best model comparison, run summaries

### **6. Report Generation (FREE - Always Runs)**
- **What:** Consolidate all monitoring results
- **Cost:** $0
- **Duration:** ~30 seconds
- **Output:** Markdown report, Slack/email notifications

### **7. Auto-Retrain Decision (Conditional)**
- **What:** Evaluate if model retraining needed
- **Cost:** $0
- **Duration:** ~10 seconds
- **Output:** Retraining recommendation, optional trigger

---

## ⚙️ Setup Instructions

### **Step 1: Enable Monitoring in Terraform**

```hcl
# infrastructure/terraform/environments/dev/terraform.tfvars

enable_sagemaker_monitoring = true  # Creates job definitions
sagemaker_endpoint_name     = "mlops-diabetes-endpoint-dev"
```

```powershell
terraform apply
```

**What this creates:**
- SageMaker Data Quality Job Definition
- SageMaker Model Quality Job Definition
- CloudWatch Alarms (3 alarms: errors, latency, traffic)

**Cost:** $0.30/month (CloudWatch alarms only)

---

### **Step 2: Configure GitHub Secrets**

The workflow needs these secrets (already set up for your OIDC):

```
AWS_ROLE_ARN         = arn:aws:iam::891807086260:role/GitHubActions-MLOps-Dev
AWS_REGION           = us-east-1
AWS_ACCOUNT_ID       = 891807086260
SLACK_WEBHOOK_URL    = https://hooks.slack.com/... (optional)
```

**Verify secrets:**
```
GitHub → Settings → Secrets and variables → Actions
```

---

### **Step 3: Enable Data Capture on Endpoint**

This is required for SageMaker Model Monitor to work:

```powershell
# One-time setup
python src/monitoring/model_monitor.py \
  --endpoint-name mlops-diabetes-endpoint-dev \
  --enable-capture \
  --create-baseline \
  --baseline-data s3://mlops-diabetes-dev-891807086260/data/train/diabetes.csv
```

**What this does:**
- Enables data capture (captures 100% of requests/responses)
- Creates baseline statistics for drift detection
- Stores baseline in S3

**Cost:** $0 (data capture is free, S3 storage ~$0.01/month)

---

### **Step 4: Test the Pipeline**

#### **Option A: Manual On-Demand Execution**

```
GitHub → Actions → MLOps Monitoring Pipeline → Run workflow

Monitoring Type: all
Environment: dev
```

#### **Option B: Run Specific Monitoring**

```
Monitoring Type: metrics-only  (FREE)
Monitoring Type: drift-detection  ($0.27)
Monitoring Type: model-quality  ($0.27)
Monitoring Type: experiment-comparison  (FREE)
```

---

## 🎮 Execution Modes

### **Mode 1: On-Demand (Manual)**

**When to use:** Before demos, after deployments, ad-hoc checks

**How to trigger:**
```
GitHub → Actions → MLOps Monitoring Pipeline → Run workflow
```

**Cost per run:**
| Monitoring Type | Cost |
|----------------|------|
| `metrics-only` | $0 |
| `drift-detection` | $0.27 |
| `model-quality` | $0.27 |
| `experiment-comparison` | $0 |
| `all` | $0.54 |

---

### **Mode 2: Scheduled (Automatic)**

**When:** Every Monday at 9 AM UTC (configured in workflow)

**What runs:**
- ✅ Endpoint metrics (FREE)
- ✅ Data drift detection ($0.27)
- ✅ Model quality check ($0.27)
- ✅ Statistical drift (FREE)
- ✅ Report generation & alerts (FREE)

**Cost:** $0.54/week = **$2.16/month**

**Change schedule:**
```yaml
# .github/workflows/monitoring_pipeline.yml

schedule:
  - cron: '0 9 * * 1'  # Every Monday 9 AM
  # - cron: '0 0 * * 0'  # Every Sunday midnight
  # - cron: '0 */6 * * *'  # Every 6 hours
```

---

### **Mode 3: Post-Deployment (Automatic)**

**When:** After "MLOps Pipeline" workflow completes

**What runs:**
- ✅ Endpoint metrics
- ✅ Experiment comparison (to verify new model)

**Cost:** $0 (no drift checks, just metrics)

**Use case:** Verify that newly deployed model is healthy

---

## 💰 Cost Optimization Strategies

### **Strategy 1: Metrics-Only Default (FREE)**

For daily/hourly checks, use metrics only:

```yaml
# Change default monitoring type
monitoring_type:
  default: 'metrics-only'  # Instead of 'all'
```

**Cost:** $0/month
**Good for:** Routine health checks

---

### **Strategy 2: Weekly Drift Detection ($2/month)**

Run full drift detection weekly:

```yaml
schedule:
  - cron: '0 9 * * 1'  # Weekly only
```

**Cost:** $0.54/week × 4 = $2.16/month
**Good for:** Regular production monitoring

---

### **Strategy 3: Conditional Drift Detection ($0-2/month)**

Only run drift detection if metrics look bad:

```yaml
drift-detection:
  needs: check-metrics
  if: |
    needs.check-metrics.outputs.error_count > 10 ||
    needs.check-metrics.outputs.avg_latency > 500
```

**Cost:** $0 (if endpoint healthy), $0.54 (if issues detected)
**Good for:** Cost-conscious monitoring

---

### **Strategy 4: Demo Mode (Enable/Disable)**

For demos only:

```powershell
# Before demo
# Edit .github/workflows/monitoring_pipeline.yml
# Comment out schedule section

# Run manually during demo
# GitHub → Actions → Run workflow

# After demo
# Re-enable schedule if needed
```

**Cost:** $0.54 per demo
**Good for:** Learning/demonstration

---

## 📊 Monitoring Dashboards

### **1. GitHub Actions Dashboard**

```
https://github.com/YOUR_USERNAME/mlopsaws/actions
```

**What to monitor:**
- Workflow run history
- Success/failure trends
- Artifact downloads (reports)

---

### **2. CloudWatch Dashboard**

Create custom dashboard:

```powershell
aws cloudwatch put-dashboard \
  --dashboard-name MLOps-Monitoring \
  --dashboard-body file://cloudwatch-dashboard.json \
  --profile mlops-dev
```

**Metrics to track:**
- `ModelLatency` - Response time
- `ModelInvocationErrors` - Error rate
- `Invocations` - Request volume
- `CPUUtilization` - Resource usage

---

### **3. SageMaker Console**

```
https://console.aws.amazon.com/sagemaker/

→ Model monitor
→ Monitoring schedules
→ Execution history
```

**What to check:**
- Baseline statistics
- Drift violations
- Data capture status

---

### **4. S3 Monitoring Reports**

All reports saved to S3:

```
s3://mlops-diabetes-dev-891807086260/monitoring/
├── data-capture/          # Captured requests/responses
├── baseline/              # Baseline statistics
├── results/               # Drift detection results
└── reports/               # Weekly summaries
```

**Download latest report:**
```powershell
aws s3 ls s3://mlops-diabetes-dev-891807086260/monitoring/results/ \
  --profile mlops-dev \
  --recursive | sort | tail -1
```

---

## ✅ Best Practices

### **1. Start Simple, Scale Gradually**

#### **Week 1: Metrics Only**
```yaml
monitoring_type: metrics-only
schedule: Daily
Cost: $0/month
```

#### **Week 2-4: Add Weekly Drift**
```yaml
monitoring_type: all
schedule: Weekly (Monday)
Cost: $2.16/month
```

#### **Month 2+: Conditional + Alerts**
```yaml
monitoring_type: Conditional based on metrics
alerts: Slack/Email enabled
Cost: $0.50-2/month
```

---

### **2. Set Up Alerts Properly**

#### **CloudWatch Alarms → SNS → Email**
```powershell
# Already created by Terraform
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:891807086260:mlops-diabetes-alerts-dev \
  --protocol email \
  --notification-endpoint your-email@example.com \
  --profile mlops-dev
```

#### **Slack Integration**
```
1. Create Slack Incoming Webhook
2. Add to GitHub Secrets: SLACK_WEBHOOK_URL
3. Pipeline will send notifications automatically
```

#### **GitHub Issues (Auto-Created)**
- Drift detected → Creates issue with label `drift-detection`
- High error rate → Creates issue with label `endpoint-health`

---

### **3. Baseline Maintenance**

**Update baselines** when model is retrained:

```powershell
# After retraining
python src/monitoring/model_monitor.py \
  --endpoint-name mlops-diabetes-endpoint-dev \
  --baseline-data s3://bucket/data/train/diabetes_new.csv \
  --create-baseline
```

**Frequency:** After each model update

---

### **4. Data Capture Best Practices**

#### **Sampling Percentage**
```python
# Development: 100% (catch all issues)
sampling_percentage=100

# Production: 10-20% (reduce storage costs)
sampling_percentage=20
```

#### **Storage Management**
```powershell
# Lifecycle policy for captured data (auto-delete after 90 days)
aws s3api put-bucket-lifecycle-configuration \
  --bucket mlops-diabetes-dev-891807086260 \
  --lifecycle-configuration file://data-capture-lifecycle.json \
  --profile mlops-dev
```

---

### **5. Retraining Triggers**

#### **Manual Approval (Recommended for Learning)**
```yaml
auto-retrain-decision:
  steps:
    - name: Create retraining request
      # Creates GitHub issue for manual review
```

#### **Automatic (For Production)**
```yaml
auto-retrain-decision:
  steps:
    - name: Trigger retraining
      if: drift_percentage > 25
      # Automatically starts training pipeline
```

---

### **6. Cost Controls**

#### **Budget Alert Integration**
```yaml
# Workflow checks budget before expensive operations
- name: Check budget
  run: |
    CURRENT_SPEND=$(aws budgets describe-budget ...)
    if [ $CURRENT_SPEND -gt 50 ]; then
      echo "Budget limit reached, skipping drift detection"
      exit 0
    fi
```

#### **Scheduled Cost Reports**
```yaml
# Monthly summary
schedule:
  - cron: '0 0 1 * *'  # 1st of each month
```

---

## 📅 Recommended Schedule

### **Development Environment**

| Frequency | Monitoring Type | Cost/Month |
|-----------|----------------|------------|
| Daily | Metrics only | $0 |
| Weekly (Mon) | All monitoring | $2.16 |
| Post-deployment | Metrics + Experiments | $0 |
| **TOTAL** | | **$2.16** |

### **Production Environment**

| Frequency | Monitoring Type | Cost/Month |
|-----------|----------------|------------|
| Hourly | Metrics only | $0 |
| Daily | Statistical drift | $0 |
| Weekly (Mon) | Full monitoring | $2.16 |
| Post-deployment | All checks | $0.54 × 4 = $2.16 |
| **TOTAL** | | **$4.32** |

---

## 🚀 Quick Start Commands

```powershell
# 1. Enable monitoring (one-time)
terraform apply

# 2. Set up data capture (one-time)
python src/monitoring/model_monitor.py \
  --endpoint-name mlops-diabetes-endpoint-dev \
  --enable-capture \
  --create-baseline \
  --baseline-data s3://bucket/data/train/diabetes.csv

# 3. Test pipeline (manual)
# GitHub → Actions → MLOps Monitoring Pipeline → Run workflow

# 4. Schedule is automatic (already configured)
# Runs every Monday at 9 AM UTC

# 5. View results
# GitHub → Actions → Latest run → Artifacts

# 6. Check CloudWatch alarms
aws cloudwatch describe-alarms \
  --alarm-name-prefix "mlops-diabetes" \
  --profile mlops-dev
```

---

## 📚 Additional Resources

- [SageMaker Model Monitor Docs](https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor.html)
- [GitHub Actions Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [CloudWatch Metrics for SageMaker](https://docs.aws.amazon.com/sagemaker/latest/dg/monitoring-cloudwatch.html)

---

**🎉 You now have a complete automated monitoring pipeline!**

- ✅ On-demand execution for demos
- ✅ Scheduled weekly checks
- ✅ Post-deployment validation
- ✅ Cost-optimized ($2-4/month instead of $194)
- ✅ Production-ready with alerts
