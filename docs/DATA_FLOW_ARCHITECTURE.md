# 📊 Complete Data Flow Architecture

## Current Implementation (Learning/Demo)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    COMPLETE DATA PIPELINE FLOW                          │
└─────────────────────────────────────────────────────────────────────────┘

PHASE 1: DATA ACQUISITION
┌──────────────────────────────────────────┐
│ External Data Source                     │
│ https://raw.githubusercontent.com/       │
│ jbrownlee/Datasets/master/               │
│ pima-indians-diabetes.data.csv           │
│                                          │
│ Type: Public dataset                     │
│ Format: CSV (768 rows, 9 columns)       │
│ Size: ~24 KB                             │
└──────────────┬───────────────────────────┘
               │ (urllib.request.urlretrieve)
               ▼
┌──────────────────────────────────────────┐
│ GitHub Actions Runner                    │
│ (Ubuntu VM in GitHub Cloud)              │
│                                          │
│ Step 1: Checkout code                   │
│ Step 2: Run download_data.py            │
│         ├─ Downloads CSV                 │
│         ├─ Validates shape               │
│         └─ Saves: data/raw/diabetes.csv  │
└──────────────┬───────────────────────────┘
               │ (Temporary local storage)
               ▼
PHASE 2: DATA UPLOAD TO AWS
┌──────────────────────────────────────────┐
│ AWS CLI Upload                           │
│ Command: aws s3 cp                       │
│                                          │
│ From: data/raw/diabetes.csv              │
│ To: s3://mlops-diabetes-ACCOUNT-dev/     │
│     diabetes-project/data/raw/           │
│     diabetes.csv                         │
│                                          │
│ Encryption: AES-256 (Server-side)        │
│ Versioning: Enabled                      │
└──────────────┬───────────────────────────┘
               │
               ▼
PHASE 3: S3 STORAGE
┌──────────────────────────────────────────┐
│ AWS S3 Bucket                            │
│ mlops-diabetes-123456789012-dev          │
│                                          │
│ Structure:                               │
│ diabetes-project/                        │
│ └── data/                                │
│     ├── raw/                             │
│     │   └── diabetes.csv       ✅ HERE  │
│     ├── processed/               (empty) │
│     │   ├── train.csv                    │
│     │   ├── validation.csv               │
│     │   └── test.csv                     │
│     └── baseline/                (empty) │
│                                          │
│ Security:                                │
│ ├─ Encryption: aws:kms                   │
│ ├─ Versioning: Enabled                   │
│ ├─ Public access: Blocked                │
│ └─ CloudTrail: Logged                    │
└──────────────┬───────────────────────────┘
               │
               ▼
PHASE 4: SAGEMAKER PROCESSING
┌──────────────────────────────────────────┐
│ SageMaker Processing Job                 │
│ (Scikit-learn container)                 │
│                                          │
│ Input:                                   │
│ └─ s3://.../data/raw/diabetes.csv        │
│                                          │
│ Processing Steps:                        │
│ 1. Read CSV from S3                      │
│ 2. Add column names                      │
│ 3. Handle missing values (if any)        │
│ 4. Feature scaling (StandardScaler)      │
│ 5. Train/Val/Test split (70/15/15)       │
│ 6. Save processed files                  │
│                                          │
│ Output:                                  │
│ ├─ s3://.../data/processed/train.csv     │
│ ├─ s3://.../data/processed/validation.csv│
│ └─ s3://.../data/processed/test.csv      │
│                                          │
│ Instance: ml.m5.xlarge                   │
│ Duration: ~5-7 minutes                   │
│ Cost: ~$0.05 per run                     │
└──────────────┬───────────────────────────┘
               │
               ▼
PHASE 5: MODEL TRAINING
┌──────────────────────────────────────────┐
│ SageMaker Training Job                   │
│ (XGBoost container)                      │
│                                          │
│ Input:                                   │
│ ├─ Train: s3://.../processed/train.csv   │
│ └─ Val: s3://.../processed/validation.csv│
│                                          │
│ Training Parameters:                     │
│ ├─ objective: binary:logistic            │
│ ├─ num_round: 100                        │
│ ├─ max_depth: 5                          │
│ ├─ eta: 0.2                              │
│ └─ subsample: 0.8                        │
│                                          │
│ Output:                                  │
│ └─ s3://.../models/model.tar.gz          │
│                                          │
│ Metrics:                                 │
│ ├─ Training accuracy: ~77%               │
│ ├─ Validation accuracy: ~75%             │
│ ├─ F1 Score: ~0.65                       │
│ └─ ROC-AUC: ~0.82                        │
│                                          │
│ Instance: ml.m5.xlarge                   │
│ Duration: ~8-10 minutes                  │
│ Cost: ~$0.10 per run                     │
└──────────────┬───────────────────────────┘
               │
               ▼
PHASE 6: MODEL EVALUATION
┌──────────────────────────────────────────┐
│ Model Evaluation                         │
│                                          │
│ Test Data: s3://.../processed/test.csv   │
│ Model: s3://.../models/model.tar.gz      │
│                                          │
│ Metrics Calculated:                      │
│ ├─ Accuracy: 0.753                       │
│ ├─ Precision: 0.721                      │
│ ├─ Recall: 0.689                         │
│ ├─ F1 Score: 0.653                       │
│ ├─ ROC-AUC: 0.818                        │
│ └─ Confusion Matrix: [[TP, FP], [FN, TN]]│
│                                          │
│ Output:                                  │
│ └─ s3://.../evaluation/evaluation.json   │
└──────────────┬───────────────────────────┘
               │
               ▼
PHASE 7: MODEL REGISTRATION
┌──────────────────────────────────────────┐
│ SageMaker Model Registry                 │
│                                          │
│ Model Package Group:                     │
│ └─ diabetes-classifier-model-group       │
│                                          │
│ Registered Model:                        │
│ ├─ Model artifact: s3://.../model.tar.gz │
│ ├─ Inference image: XGBoost container    │
│ ├─ Metrics: evaluation.json              │
│ ├─ Status: Approved (dev)                │
│ └─ Version: 1                            │
└──────────────┬───────────────────────────┘
               │
               ▼
PHASE 8: MODEL DEPLOYMENT
┌──────────────────────────────────────────┐
│ SageMaker Real-Time Endpoint             │
│                                          │
│ Endpoint Configuration:                  │
│ ├─ Name: mlops-diabetes-endpoint-dev     │
│ ├─ Model: Latest approved version        │
│ ├─ Instance: ml.t2.medium                │
│ ├─ Instance count: 1                     │
│ └─ Auto-scaling: Enabled (1-3 instances) │
│                                          │
│ Features:                                │
│ ├─ Data capture: Enabled (10% sampling)  │
│ ├─ Model monitoring: Enabled (hourly)    │
│ └─ CloudWatch metrics: Enabled           │
│                                          │
│ Endpoint URL:                            │
│ https://runtime.sagemaker.us-east-1.     │
│ amazonaws.com/endpoints/                 │
│ mlops-diabetes-endpoint-dev/invocations  │
│                                          │
│ Status: InService ✅                     │
│ Deployment time: ~8-10 minutes           │
│ Cost: ~$0.065/hour                       │
└──────────────┬───────────────────────────┘
               │
               ▼
PHASE 9: PREDICTION (INFERENCE)
┌──────────────────────────────────────────┐
│ Client Application                       │
│                                          │
│ Input JSON:                              │
│ {                                        │
│   "instances": [                         │
│     [6, 148, 72, 35, 0, 33.6, 0.627, 50] │
│   ]                                      │
│ }                                        │
│                                          │
│ API Call:                                │
│ POST /endpoints/.../invocations          │
│                                          │
│ Response:                                │
│ {                                        │
│   "predictions": [                       │
│     {"score": 0.73, "class": 1}          │
│   ]                                      │
│ }                                        │
│                                          │
│ Interpretation:                          │
│ └─ 73% probability of diabetes ⚠️        │
└──────────────────────────────────────────┘


MONITORING & FEEDBACK LOOP
┌──────────────────────────────────────────┐
│ Continuous Monitoring                    │
│                                          │
│ Data Capture:                            │
│ └─ s3://.../monitoring/data-capture/     │
│    ├─ Inputs (features)                  │
│    └─ Outputs (predictions)              │
│                                          │
│ Model Monitor (Hourly):                  │
│ ├─ Data quality violations               │
│ ├─ Model quality violations              │
│ ├─ Bias drift detection                  │
│ └─ Feature attribution drift             │
│                                          │
│ Violations → SNS Alert → Email           │
│                                          │
│ CloudWatch Metrics:                      │
│ ├─ ModelInvocations                      │
│ ├─ ModelLatency                          │
│ ├─ Overhead Latency                      │
│ └─ MemoryUtilization                     │
│                                          │
│ If drift detected → Retrain pipeline     │
└──────────────────────────────────────────┘
```

---

## Data States Throughout Pipeline

```
┌────────────────────────────────────────────────────────────┐
│                    DATA TRANSFORMATIONS                    │
└────────────────────────────────────────────────────────────┘

STATE 1: RAW DATA (From GitHub)
├─ Format: CSV (no header)
├─ Rows: 768
├─ Columns: 9 (8 features + 1 target)
├─ Features: [pregnancies, glucose, blood_pressure, 
│             skin_thickness, insulin, bmi, 
│             diabetes_pedigree, age]
├─ Target: [0=No diabetes, 1=Has diabetes]
├─ Missing values: Some zeros as placeholders
└─ Size: ~24 KB

      ↓ (download_data.py)

STATE 2: LOCAL GITHUB RUNNER
├─ Location: /tmp/data/raw/diabetes.csv
├─ Same format as STATE 1
├─ Validated: Shape check, no corruption
└─ Temporary (deleted after upload)

      ↓ (aws s3 cp)

STATE 3: S3 RAW DATA
├─ Location: s3://BUCKET/data/raw/diabetes.csv
├─ Encryption: AWS KMS
├─ Versioning: Enabled
├─ Same content as STATE 2
└─ Persistent storage

      ↓ (SageMaker Processing)

STATE 4: PROCESSED DATA
├─ Format: CSV (with header)
├─ Columns: Named (Pregnancies, Glucose, ...)
├─ Features: Scaled (StandardScaler)
│   - Mean: 0
│   - Std: 1
├─ Missing values: Replaced with median
├─ Split into 3 files:
│   ├─ train.csv (537 rows, 70%)
│   ├─ validation.csv (115 rows, 15%)
│   └─ test.csv (116 rows, 15%)
└─ Location: s3://BUCKET/data/processed/

      ↓ (SageMaker Training)

STATE 5: MODEL ARTIFACT
├─ Format: model.tar.gz (compressed)
├─ Contains:
│   ├─ xgboost-model (binary)
│   └─ metadata.json
├─ Size: ~100 KB
├─ Location: s3://BUCKET/models/
└─ Registered in Model Registry

      ↓ (SageMaker Deployment)

STATE 6: DEPLOYED MODEL
├─ Loaded in memory (SageMaker endpoint)
├─ Ready for inference
├─ Input: Raw features (8 values)
├─ Output: Prediction (0 or 1) + probability
└─ Latency: ~50-100ms per prediction
```

---

## Cost Breakdown by Phase

```
┌────────────────────────────────────────────────────────────┐
│                    COST PER PIPELINE RUN                   │
└────────────────────────────────────────────────────────────┘

PHASE 1: Data Acquisition
├─ GitHub download: FREE
└─ GitHub Actions runner: FREE (included)

PHASE 2: S3 Upload
├─ Data transfer: FREE (to AWS from internet)
├─ PUT requests: $0.000005 per request ≈ $0.00
└─ Storage: $0.023/GB/month ≈ $0.0006/month (24 KB)

PHASE 3: SageMaker Processing
├─ Instance: ml.m5.xlarge
├─ Duration: 7 minutes
├─ Rate: $0.269/hour
└─ Cost: ~$0.03

PHASE 4: Model Training
├─ Instance: ml.m5.xlarge
├─ Duration: 10 minutes
├─ Rate: $0.269/hour
└─ Cost: ~$0.045

PHASE 5: Model Deployment
├─ Instance: ml.t2.medium
├─ Duration: Continuous (24/7)
├─ Rate: $0.065/hour
└─ Cost: ~$46.80/month

PHASE 6: Model Monitoring
├─ Processing: ml.m5.xlarge
├─ Schedule: Hourly
├─ Duration: 5 min/job
└─ Cost: ~$5.00/month

────────────────────────────────────────────────────────────
TOTAL COST:
├─ One-time pipeline run: ~$0.08
├─ Monthly (with endpoint): ~$52/month
└─ Development tips:
    ├─ Delete endpoint when not testing
    ├─ Use auto-shutdown Lambda
    └─ Enable cost alerts ($10 threshold)
```

---

## Performance Metrics

```
┌────────────────────────────────────────────────────────────┐
│                    PIPELINE PERFORMANCE                    │
└────────────────────────────────────────────────────────────┘

Total Pipeline Duration: ~30 minutes

Phase Breakdown:
├─ Code quality checks: 3-5 min      (10-17%)
├─ Data validation: 2 min            (6-7%)
├─ Data upload: 1 min                (3-4%)
├─ Processing job: 5-7 min           (17-23%)
├─ Training job: 8-10 min            (27-33%)
├─ Model evaluation: 2-3 min         (7-10%)
├─ Model registration: 1 min         (3-4%)
├─ Model deployment: 8-10 min        (27-33%)
└─ Monitoring setup: 2-3 min         (7-10%)

Optimization Opportunities:
├─ ✅ Already optimized: Parallel jobs where possible
├─ ⚠️ Bottleneck: Training (can't parallelize)
└─ 💡 Improvement: Use ml.c5.2xlarge for faster training
    (Cost: +50%, Time: -30% ≈ 21 minutes total)
```

---

**Complete guide:** [DATA_INGESTION_GUIDE.md](./DATA_INGESTION_GUIDE.md)

**Last Updated:** November 4, 2025
