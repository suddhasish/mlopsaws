# GitHub Actions Setup Guide

## ✅ Configuration Updated

Your `config/config.yaml` has been updated with:
- **AWS Account ID:** `891807086260`
- **SageMaker Role:** `arn:aws:iam::891807086260:role/service-role/AmazonSageMaker-ExecutionRole-20251026T145759`
- **S3 Bucket:** `mlops-diabetes-dev-891807086260`

---

## 🔐 Step 1: Add GitHub Secrets

Go to: https://github.com/suddhasish/mlopsaws/settings/secrets/actions

Click **"New repository secret"** and add these 5 secrets:

### Required Secrets

| Secret Name | Value |
|-------------|-------|
| `AWS_ACCESS_KEY_ID` | Get from AWS Console → IAM → Security credentials |
| `AWS_SECRET_ACCESS_KEY` | Get from AWS Console → IAM → Security credentials |
| `S3_BUCKET_NAME` | `mlops-diabetes-dev-891807086260` |
| `SAGEMAKER_EXECUTION_ROLE` | `arn:aws:iam::891807086260:role/service-role/AmazonSageMaker-ExecutionRole-20251026T145759` |
| `AWS_ACCOUNT_ID` | `891807086260` |

### How to Get AWS Access Keys

```powershell
# Check your current AWS credentials
aws configure list

# If you need to create new access keys:
# 1. Go to AWS Console → IAM → Users → Your User
# 2. Click "Security credentials" tab
# 3. Click "Create access key"
# 4. Choose "Command Line Interface (CLI)"
# 5. Copy both Access Key ID and Secret Access Key
```

---

## 🚀 Step 2: Trigger the Pipeline

### Option A: Push to Main (Recommended)

```powershell
cd "d:\MLOPS\MLOPS-AWS\mlops AWS sagemaker"

# Commit the config changes
git add config/config.yaml
git commit -m "config: update AWS account and SageMaker role for pipeline execution"
git push origin main
```

This will automatically trigger the GitHub Actions workflow!

### Option B: Manual Workflow Trigger

1. Go to: https://github.com/suddhasish/mlopsaws/actions
2. Click on **"MLOps Pipeline - Diabetes Classification"**
3. Click **"Run workflow"** button (top right)
4. Select branch: **main**
5. Click **"Run workflow"**

---

## 📊 Step 3: Monitor Execution

### GitHub Actions Dashboard
- URL: https://github.com/suddhasish/mlopsaws/actions
- Watch real-time logs for each job
- Total time: ~25-30 minutes

### SageMaker Console
- Pipelines: https://console.aws.amazon.com/sagemaker/home?region=us-east-1#/pipelines
- Training Jobs: https://console.aws.amazon.com/sagemaker/home?region=us-east-1#/jobs
- Model Registry: https://console.aws.amazon.com/sagemaker/home?region=us-east-1#/model-packages/groups

---

## 🔄 What GitHub Actions Will Do

```
Job 1: Code Quality & Tests (2 min)
├─ Run pytest
├─ Check code formatting (Black)
└─ Lint with flake8

Job 2: Data Validation (1 min)
├─ Download diabetes.csv
└─ Validate data structure

Job 3: Upload Data to S3 (1 min)
└─ Upload diabetes.csv → s3://mlops-diabetes-dev-891807086260/

Job 4: Execute SageMaker Pipeline (20-25 min)
├─ Create/update pipeline definition
├─ Start pipeline execution
│  ├─ PreprocessData (5 min)
│  ├─ TrainModel with Spot Instances (10 min)
│  ├─ EvaluateModel (5 min)
│  ├─ TrackExperiment (2 min)
│  └─ RegisterModel (if metrics pass)
└─ Pipeline complete! ✅

Job 5: Deploy Model (Manual Approval Required)
└─ Requires manual approval in GitHub

Job 6: Setup Monitoring
└─ Configure Model Monitor
```

---

## 💰 Cost Estimate

| Component | Cost |
|-----------|------|
| GitHub Actions (2,000 min/month free) | $0 |
| SageMaker Pipeline Execution | ~$0.08 |
| S3 Storage | ~$0.01/GB/month |
| **Total per run** | **~$0.08** |

With spot instances, you save ~70% on training costs!

---

## ✅ Verification Checklist

- [ ] GitHub secrets added (all 5 secrets)
- [ ] Config updated and pushed to main
- [ ] GitHub Actions workflow triggered
- [ ] Pipeline execution started in SageMaker
- [ ] Monitor logs in GitHub Actions
- [ ] Check SageMaker Console for pipeline status

---

## 🐛 Troubleshooting

### Issue: "AWS credentials not found"
**Solution:** Verify GitHub secrets are set correctly
```powershell
# Test your local AWS credentials work
aws sts get-caller-identity
```

### Issue: "Access Denied" in S3
**Solution:** Check SageMaker role has S3 permissions
```powershell
# Verify role exists
aws iam get-role --role-name AmazonSageMaker-ExecutionRole-20251026T145759
```

### Issue: "Pipeline already exists"
**Solution:** This is normal - pipeline will be updated, not recreated

### Issue: GitHub Actions workflow doesn't trigger
**Solution:** Check the workflow file exists
```powershell
ls .github/workflows/mlops_pipeline.yaml
```

---

## 📞 Quick Commands

```powershell
# Check GitHub Actions status
gh run list --workflow=mlops_pipeline.yaml

# View latest run logs
gh run view --log

# Check SageMaker pipeline executions
aws sagemaker list-pipeline-executions --pipeline-name diabetes-classification-pipeline

# Check latest training job
aws sagemaker list-training-jobs --max-results 1 --query "TrainingJobSummaries[0]"
```

---

## 🎯 Next Steps After Pipeline Completes

1. **Check Model Registry**
   ```powershell
   aws sagemaker list-model-packages --model-package-group-name mlops-diabetes-model-group-dev
   ```

2. **Deploy to Endpoint** (if model approved)
   ```powershell
   python src/deployment/deploy.py --model-package-arn <ARN> --endpoint-name diabetes-dev
   ```

3. **Test Inference**
   ```powershell
   python scripts/test_inference.py --endpoint-name diabetes-dev
   ```

---

## 📧 Notifications

GitHub Actions will:
- ✅ Send email on success
- ❌ Send email on failure
- 📊 Show status badge in README

Add this to your README.md:
```markdown
[![MLOps Pipeline](https://github.com/suddhasish/mlopsaws/actions/workflows/mlops_pipeline.yaml/badge.svg)](https://github.com/suddhasish/mlopsaws/actions/workflows/mlops_pipeline.yaml)
```
