# 📊 SageMaker Monitoring & Experiment Tracking

This module provides **cost-effective** monitoring and experiment tracking for ML models.

---

## 🎯 Features

### 1. **Experiment Tracking** (FREE - S3 storage only)
- Track hyperparameters, metrics, and artifacts
- Compare multiple training runs
- Find best performing model
- **Cost:** ~$0.023/GB/month (S3 storage)

### 2. **On-Demand Drift Detection** (~$0.27/run)
- Data quality monitoring
- Model performance tracking
- Run when needed (not continuously)
- **Cost:** $0.269/hour × ~1 hour = $0.27 per check

### 3. **CloudWatch Alarms** (~$0.30/month)
- Model invocation errors
- Latency degradation
- High traffic alerts
- **Cost:** $0.10/alarm × 3 alarms = $0.30/month

---

## 💰 Cost Comparison

| Monitoring Type | Continuous (Monthly) | On-Demand (Per Run) |
|----------------|---------------------|---------------------|
| **Continuous Schedule** | ~$194 (hourly checks) | N/A |
| **On-Demand** | $0 | $0.27 per check |
| **CloudWatch Alarms** | $0.30 | $0.30 |
| **Experiment Tracking** | ~$0.05 | ~$0.05 |
| **TOTAL** | **$194.35/month** | **$0.62 per demo** |

**💡 Recommendation for Demo:** Use **On-Demand** approach - saves **$193/month**!

---

## 🚀 Quick Start

### Enable Monitoring in Terraform

**For Demos (Enable temporarily):**
```hcl
# infrastructure/terraform/environments/dev/terraform.tfvars
enable_sagemaker_monitoring = true
sagemaker_endpoint_name     = "mlops-diabetes-endpoint-dev"
```

**After Demo (Disable to save costs):**
```hcl
enable_sagemaker_monitoring = false
```

Apply changes:
```powershell
terraform apply
```

---

## 📖 Usage Examples

### 1. Track Experiment (FREE)

```python
from src.monitoring.experiment_tracker import track_training_run

# Track a training run
track_training_run(
    experiment_name="diabetes-classification-experiments",
    hyperparameters={
        'max_depth': 5,
        'eta': 0.2,
        'num_round': 100
    },
    metrics={
        'accuracy': 0.85,
        'f1_score': 0.81,
        'roc_auc': 0.88
    },
    model_artifact_uri='s3://bucket/models/model.tar.gz'
)
```

### 2. Compare Experiments

```python
from src.monitoring.experiment_tracker import ExperimentTracker

tracker = ExperimentTracker("diabetes-classification-experiments")

# Get best run
best_run = tracker.get_best_run(metric_name='accuracy', maximize=True)
print(f"Best accuracy: {best_run['accuracy']}")

# Compare all runs
tracker.compare_runs()
```

### 3. Check for Data Drift (On-Demand)

```powershell
# Get current endpoint metrics
python src/monitoring/run_drift_detection.py \
  --endpoint-name mlops-diabetes-endpoint-dev \
  --get-metrics \
  --hours 24

# Run data drift detection (costs $0.27)
python src/monitoring/run_drift_detection.py \
  --endpoint-name mlops-diabetes-endpoint-dev \
  --check-data-drift

# Run model quality check (costs $0.27)
python src/monitoring/run_drift_detection.py \
  --endpoint-name mlops-diabetes-endpoint-dev \
  --check-model-quality
```

---

## 📊 CloudWatch Alarms

When `enable_sagemaker_monitoring = true`, these alarms are created:

1. **Model Invocation Errors**
   - Threshold: > 10 errors in 5 minutes
   - Action: Send SNS notification

2. **Model Latency**
   - Threshold: > 1000ms average
   - Action: Send SNS notification

3. **High Traffic**
   - Threshold: > 1000 invocations per instance in 5 minutes
   - Action: Send SNS notification

**View alarms:**
```powershell
aws cloudwatch describe-alarms \
  --alarm-name-prefix "mlops-diabetes" \
  --profile mlops-dev
```

---

## 🎭 Demo Workflow

**Before Demo:**
```powershell
# 1. Enable monitoring
# Edit: infrastructure/terraform/environments/dev/terraform.tfvars
enable_sagemaker_monitoring = true
sagemaker_endpoint_name     = "mlops-diabetes-endpoint-dev"

# 2. Apply changes
terraform apply

# 3. Deploy model (if not already deployed)
python src/deployment/deploy.py --environment dev
```

**During Demo:**
```powershell
# Show experiment tracking
python src/monitoring/experiment_tracker.py

# Show current metrics
python src/monitoring/run_drift_detection.py \
  --endpoint-name mlops-diabetes-endpoint-dev \
  --get-metrics

# Demonstrate drift detection (optional - costs $0.27)
python src/monitoring/run_drift_detection.py \
  --endpoint-name mlops-diabetes-endpoint-dev \
  --check-data-drift
```

**After Demo:**
```powershell
# Disable monitoring to save costs
# Edit: infrastructure/terraform/environments/dev/terraform.tfvars
enable_sagemaker_monitoring = false

# Apply changes
terraform apply
```

**💰 Demo Cost:** $0.30 (alarms) + $0.27 (optional drift check) = **~$0.60 total**

---

## 🔍 Monitoring Dashboard

**SageMaker Console:**
```
https://console.aws.amazon.com/sagemaker/

→ Experiments and trials
→ Model monitor
→ Endpoints → [Your endpoint] → Monitor
```

**CloudWatch Console:**
```
https://console.aws.amazon.com/cloudwatch/

→ Alarms
→ Metrics → SageMaker
```

---

## 📈 Metrics Collected

### Endpoint Metrics (CloudWatch)
- Invocations (total requests)
- ModelLatency (response time)
- ModelInvocationErrors (failures)
- CPUUtilization
- MemoryUtilization

### Data Quality Metrics
- Missing values
- Data type mismatches
- Outliers
- Distribution drift

### Model Quality Metrics
- Accuracy degradation
- Precision/Recall changes
- ROC-AUC drift
- Confusion matrix changes

---

## 🛠️ Terraform Resources Created

When `enable_sagemaker_monitoring = true`:

1. `aws_sagemaker_data_quality_job_definition` - Data drift detection
2. `aws_sagemaker_model_quality_job_definition` - Model performance tracking
3. `aws_cloudwatch_metric_alarm` × 3 - Error, latency, and traffic alarms

**View resources:**
```powershell
terraform state list | Select-String "sagemaker"
terraform state list | Select-String "cloudwatch_metric_alarm"
```

---

## ⚠️ Important Notes

1. **Monitoring Jobs are NOT scheduled by default**
   - Job definitions are created
   - Run them on-demand using Python script
   - Avoids $194/month continuous monitoring cost

2. **CloudWatch Alarms are active**
   - Cost: $0.10/alarm/month ($0.30 total)
   - Send SNS notifications when thresholds exceeded
   - Automatically enabled when monitoring enabled

3. **Experiment Tracking is always free**
   - Uses SageMaker Experiments API
   - Only pays for S3 storage (~$0.05/month)
   - No need to enable/disable

---

## 📚 References

- [SageMaker Model Monitor](https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor.html)
- [SageMaker Experiments](https://docs.aws.amazon.com/sagemaker/latest/dg/experiments.html)
- [CloudWatch Alarms](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html)
