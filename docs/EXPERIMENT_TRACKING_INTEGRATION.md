# 🧪 Experiment Tracking Integration Guide

This guide explains how experiment tracking is integrated into the MLOps pipeline.

---

## 📊 Overview

Experiment tracking is now **fully integrated** into the training pipeline using **SageMaker Experiments API** (FREE - only S3 storage costs ~$0.05/month).

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   TRAINING PIPELINE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. PreprocessData                                              │
│     └─ Split data (train/val/test)                             │
│                                                                 │
│  2. TrainModel ✅ TRACKS EXPERIMENTS                           │
│     ├─ Train XGBoost model                                     │
│     ├─ Log hyperparameters to SageMaker Experiments           │
│     ├─ Log training metrics (train_auc, validation_auc)       │
│     └─ Log model artifact reference                            │
│                                                                 │
│  3. EvaluateModel                                               │
│     ├─ Test model on held-out data                            │
│     └─ Generate evaluation metrics                             │
│                                                                 │
│  4. TrackExperiment ✅ LOGS FINAL METRICS                      │
│     ├─ Read evaluation results                                 │
│     ├─ Log final metrics (accuracy, F1, ROC-AUC)              │
│     ├─ Link model artifact S3 URI                             │
│     └─ Create experiment summary                               │
│                                                                 │
│  5. CheckModelQualityThresholds                                │
│     └─ If metrics pass → Register model                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Integration Points

### **1. Training Script (`src/training/train.py`)**

**What was added:**
- Import `ExperimentTracker` from monitoring module
- After model training completes, automatically log:
  - **Hyperparameters**: max_depth, eta, gamma, subsample, num_round, etc.
  - **Training metrics**: Final train/validation metrics from XGBoost
  - **Model artifact**: Reference to model location

**Code:**
```python
# After training completes
from src.monitoring.experiment_tracker import ExperimentTracker

experiment_name = os.environ.get('EXPERIMENT_NAME', 'diabetes-classification-experiments')
training_job_name = os.environ.get('TRAINING_JOB_NAME', run_name)

tracker = ExperimentTracker(experiment_name=experiment_name, run_name=training_job_name)
tracker.start_run()

# Log hyperparameters
tracker.log_parameters({
    'max_depth': args.max_depth,
    'eta': args.eta,
    'gamma': args.gamma,
    # ... more hyperparameters
})

# Log training metrics
tracker.log_metrics(final_metrics)

# Log model artifact
tracker.log_artifact(model_uri, 'model')
```

---

### **2. Pipeline Step (`src/monitoring/track_experiment.py`)**

**What was added:**
- New processing step script that runs after evaluation
- Reads evaluation results (accuracy, F1, ROC-AUC, etc.)
- Logs final test metrics to the same experiment run
- Creates complete experiment record

**Why separate step?**
- Training logs training-time metrics (train_auc, val_auc)
- Tracking step logs test metrics (accuracy, precision, recall, F1, ROC-AUC)
- Together they provide complete experiment picture

---

### **3. Training Pipeline (`pipelines/training_pipeline.py`)**

**What was added:**
- New method: `create_experiment_tracking_step()`
- Runs after evaluation, before model registration
- Passes evaluation results to tracking script
- Creates experiment log artifact

**Pipeline flow:**
```
PreprocessData → TrainModel → EvaluateModel → TrackExperiment → RegisterModel
                       ↓                            ↓
                 Logs training            Logs evaluation metrics
                 hyperparameters          (accuracy, F1, etc.)
```

---

## 📈 What Gets Tracked

### **During Training** (TrainModel step):
```json
{
  "hyperparameters": {
    "max_depth": 5,
    "eta": 0.2,
    "gamma": 4,
    "min_child_weight": 6,
    "subsample": 0.7,
    "num_round": 100,
    "early_stopping_rounds": 10
  },
  "training_metrics": {
    "train_auc": 0.8234,
    "validation_auc": 0.7891
  },
  "model_artifact": "/opt/ml/model"
}
```

### **During Experiment Tracking** (TrackExperiment step):
```json
{
  "evaluation_metrics": {
    "accuracy": 0.7532,
    "precision": 0.7234,
    "recall": 0.7112,
    "f1_score": 0.7172,
    "roc_auc": 0.8156
  },
  "model_artifact_uri": "s3://bucket/models/model.tar.gz"
}
```

---

## 🚀 How to Use

### **1. Run Training Pipeline (Automatic Tracking)**

```powershell
# Experiments are automatically tracked when pipeline runs
python pipelines/training_pipeline.py --environment dev --execute
```

**What happens:**
1. Pipeline starts
2. Data preprocessing
3. Model training → **Logs hyperparameters + training metrics**
4. Model evaluation
5. Experiment tracking → **Logs evaluation metrics**
6. Model registration (if quality gates pass)

---

### **2. View Experiments in AWS Console**

```
1. Go to: https://console.aws.amazon.com/sagemaker/
2. Navigate to: Experiments and trials
3. Find experiment: "diabetes-classification-experiments"
4. View all runs with metrics and artifacts
```

---

### **3. Compare Experiments Programmatically**

```python
from src.monitoring.experiment_tracker import ExperimentTracker

tracker = ExperimentTracker("diabetes-classification-experiments")

# Get best run
best_run = tracker.get_best_run('accuracy', maximize=True)
print(f"Best accuracy: {best_run['accuracy']:.4f}")

# Compare all runs
tracker.compare_runs()
```

---

### **4. Compare Experiments via GitHub Actions**

```
GitHub → Actions → MLOps Monitoring Pipeline → Run workflow
  monitoring_type: experiment-comparison
  environment: dev
```

This will:
- Compare all training runs
- Find best performing model
- Generate comparison report
- Upload as artifact

---

## 🔍 Viewing Experiment Data

### **SageMaker Console**

```
SageMaker → Experiments → diabetes-classification-experiments
```

**What you see:**
- List of all training runs
- Hyperparameters for each run
- Metrics (training and evaluation)
- Model artifacts (S3 URIs)
- Timestamp and duration
- Instance types used

### **Programmatic Access**

```python
from sagemaker.analytics import ExperimentAnalytics
import boto3

analytics = ExperimentAnalytics(
    experiment_name='diabetes-classification-experiments',
    sagemaker_session=boto3.Session(region_name='us-east-1')
)

# Get DataFrame of all experiments
df = analytics.dataframe()
print(df)

# Filter best runs
best_runs = df[df['accuracy'] > 0.75].sort_values('accuracy', ascending=False)
```

### **GitHub Actions Monitoring**

```yaml
# In .github/workflows/monitoring_pipeline.yml
experiment-tracking:
  steps:
    - name: Compare experiments
      run: |
        python -c "
        from src.monitoring.experiment_tracker import ExperimentTracker
        tracker = ExperimentTracker('diabetes-classification-experiments')
        best_run = tracker.get_best_run('accuracy', maximize=True)
        print(f'Best Model: {best_run}')
        "
```

---

## 💰 Cost

| Component | Cost |
|-----------|------|
| SageMaker Experiments API | **FREE** |
| S3 Storage (metadata) | ~$0.023/GB/month |
| Typical usage (100 runs) | ~10 MB = **$0.0002/month** |
| **TOTAL** | **~$0.05/month** |

---

## 🎯 Benefits

### **1. Model Lineage**
- Track which hyperparameters produced which results
- Understand model evolution over time
- Reproduce successful experiments

### **2. A/B Testing**
- Compare multiple models side-by-side
- Select best performer automatically
- Deploy with confidence

### **3. Debugging**
- Identify why model performance degraded
- Compare current vs previous runs
- Track changes across environments (dev/staging/prod)

### **4. Compliance**
- Complete audit trail of all models
- Track who trained what, when
- Model versioning and governance

### **5. Automated Model Selection**
```python
# Automatically deploy best model
tracker = ExperimentTracker('diabetes-classification-experiments')
best = tracker.get_best_run('f1_score', maximize=True)

if best['f1_score'] > current_production_f1:
    deploy_model(best['model_artifact_uri'])
```

---

## 🔧 Troubleshooting

### **Issue: Experiments not showing in SageMaker Console**

**Solution:**
1. Check IAM permissions (role needs `sagemaker:CreateExperiment`, `sagemaker:CreateTrial`)
2. Verify experiment name matches
3. Check CloudWatch logs for errors

### **Issue: Import error for ExperimentTracker**

**Solution:**
```python
# Make sure sys.path includes src directory
import sys
sys.path.append('/opt/ml/code')  # For SageMaker
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
```

### **Issue: Metrics not logging**

**Solution:**
- Ensure metrics are numeric (float/int)
- Check evaluation_results.json has correct format
- Verify TrackExperiment step is included in pipeline

---

## 📚 Related Documentation

- [SageMaker Experiments Docs](https://docs.aws.amazon.com/sagemaker/latest/dg/experiments.html)
- [Experiment Tracker Code](../src/monitoring/experiment_tracker.py)
- [Monitoring Pipeline Guide](./MONITORING_PIPELINE_GUIDE.md)
- [Training Pipeline](../pipelines/training_pipeline.py)

---

## 🎉 Summary

Experiment tracking is now **fully automated**:
- ✅ Runs automatically with every training pipeline execution
- ✅ Tracks hyperparameters, metrics, and artifacts
- ✅ Viewable in SageMaker Console
- ✅ Queryable programmatically
- ✅ Integrated with monitoring pipeline
- ✅ FREE (only S3 storage costs ~$0.05/month)

**No manual work needed** - just run your training pipeline and experiments are tracked automatically! 🚀
