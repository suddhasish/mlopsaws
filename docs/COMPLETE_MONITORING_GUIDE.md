# Complete ML Model Monitoring Guide

**Version:** 1.0  
**Date:** November 15, 2025  
**Project:** Diabetes Classification MLOps System

---

## Table of Contents

1. [Overview](#overview)
2. [Monitoring Architecture](#monitoring-architecture)
3. [Data Capture System](#data-capture-system)
4. [Drift Detection](#drift-detection)
5. [Model Quality Monitoring](#model-quality-monitoring)
6. [CloudWatch Integration](#cloudwatch-integration)
7. [Alerting & Notifications](#alerting--notifications)
8. [Implementation Guide](#implementation-guide)
9. [Troubleshooting](#troubleshooting)
10. [Cost Analysis](#cost-analysis)

---

## Overview

### What is Model Monitoring?

Model monitoring is the continuous observation of deployed ML models to ensure they maintain acceptable performance in production. It detects issues like:

- **Data Drift**: Input data distribution changes over time
- **Model Drift**: Model performance degrades
- **System Issues**: Latency, errors, availability problems
- **Concept Drift**: Relationship between features and target changes

### Why Monitor?

```
WITHOUT MONITORING:
─────────────────────────────────────────────────────────────
Week 1:  Model accuracy: 85% ✅
Week 4:  Model accuracy: 82% ⚠️  (Nobody notices)
Week 8:  Model accuracy: 70% ❌ (Business impact)
Week 12: Model accuracy: 55% 💥 (Worse than random!)

Result: Months of incorrect predictions, lost revenue,
        damaged reputation


WITH MONITORING:
─────────────────────────────────────────────────────────────
Week 1:  Model accuracy: 85% ✅
Week 4:  Alert: Accuracy dropped to 82% 🔔
Week 5:  Investigate → Data drift detected
Week 6:  Retrain model with new data
Week 7:  Deploy updated model → Accuracy: 86% ✅

Result: Issues detected early, model maintained,
        business continuity preserved
```

### Monitoring Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    MONITORING PYRAMID                       │
└─────────────────────────────────────────────────────────────┘

              ┌─────────────────────┐
              │  Business Metrics   │  ← ROI, Conversions
              │  (Manual Analysis)  │     Revenue Impact
              └──────────┬──────────┘
                         │
              ┌──────────┴──────────┐
              │   Model Quality     │  ← Accuracy, F1-Score
              │  (Ground Truth)     │     Precision, Recall
              └──────────┬──────────┘
                         │
              ┌──────────┴──────────┐
              │    Data Drift       │  ← Feature distributions
              │   (Statistical)     │     Schema changes
              └──────────┬──────────┘
                         │
              ┌──────────┴──────────┐
              │  System Health      │  ← Latency, Errors
              │   (Real-time)       │     Availability, CPU
              └─────────────────────┘

Priority:   High →→→→→→→→→→→→→→→→ Low
Frequency:  Seconds → Hours → Daily → Weekly
```

---

## Monitoring Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    COMPLETE MONITORING SYSTEM                            │
└─────────────────────────────────────────────────────────────────────────┘

                        ┌─────────────────────┐
                        │  Production Traffic │
                        │  (Predictions)      │
                        └──────────┬──────────┘
                                   │
                                   ▼
                   ┌────────────────────────────────┐
                   │   SageMaker Endpoint           │
                   │   (diabetes-classifier-prod)   │
                   └────────────────────────────────┘
                            │           │
            ┌───────────────┴───┐   ┌──┴───────────────┐
            │                   │   │                  │
            ▼                   ▼   ▼                  ▼
    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
    │ CloudWatch   │    │ Data Capture │    │ Model Metrics│
    │ Metrics      │    │ (S3)         │    │ (S3)         │
    └──────┬───────┘    └──────┬───────┘    └──────┬───────┘
           │                   │                   │
           ▼                   ▼                   ▼
    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
    │ Real-Time    │    │ Drift        │    │ Quality      │
    │ Alarms       │    │ Detection    │    │ Monitoring   │
    │              │    │              │    │              │
    │ • Latency    │    │ • KS Test    │    │ • Accuracy   │
    │ • Errors     │    │ • PSI        │    │ • Precision  │
    │ • Invocations│    │ • Chi-Square │    │ • Recall     │
    └──────┬───────┘    └──────┬───────┘    └──────┬───────┘
           │                   │                   │
           └───────────────────┴───────────────────┘
                               │
                               ▼
                   ┌────────────────────────────────┐
                   │   SNS Topic / Email / Slack    │
                   │   Alert: Model drift detected! │
                   └────────────────────────────────┘
                               │
                               ▼
                   ┌────────────────────────────────┐
                   │   MLOps Team Actions:          │
                   │   1. Investigate root cause    │
                   │   2. Retrain model if needed   │
                   │   3. Deploy updated version    │
                   └────────────────────────────────┘
```

### Component Relationships

```
DATA FLOW THROUGH MONITORING SYSTEM:
─────────────────────────────────────────────────────────────

T=0s     Client sends prediction request
           ↓
T=0.1s   Endpoint receives request
           ├─ Request logged to CloudWatch Logs
           └─ Request captured to S3 (if data capture enabled)
           ↓
T=0.2s   Model generates prediction
           ├─ Invocation metrics → CloudWatch Metrics
           └─ Response captured to S3
           ↓
T=0.3s   Response sent to client
           ↓
T=1m     CloudWatch alarm evaluates metrics
           └─ Triggers SNS if threshold exceeded
           ↓
T=1h     SageMaker Model Monitor job runs
           ├─ Reads captured data from S3
           ├─ Compares with baseline
           ├─ Detects drift/violations
           └─ Publishes results to S3 + CloudWatch
           ↓
T=1d     Daily drift detection job runs
           ├─ Analyzes 24h of data
           ├─ Statistical tests (KS, PSI, Chi-Square)
           └─ Generates drift report
           ↓
T=1w     Model quality evaluation (with ground truth)
           ├─ Compare predictions vs actual outcomes
           ├─ Calculate accuracy, precision, recall
           └─ Detect performance degradation
```

---

## Data Capture System

### What is Data Capture?

Data capture logs all inference requests and responses to S3 for analysis.

### Enabling Data Capture

```python
# File: src/monitoring/model_monitor.py

def enable_data_capture(self, endpoint_name, sampling_percentage=100):
    """
    Enable data capture for an endpoint
    
    Args:
        endpoint_name: SageMaker endpoint name
        sampling_percentage: % of requests to capture (1-100)
                            100 = capture all requests
                            10 = capture 10% (reduces costs)
    """
    data_capture_uri = f"s3://{self.bucket}/monitoring/data-capture"
    
    # Update endpoint config with data capture
    self.sagemaker_client.create_endpoint_config(
        EndpointConfigName=f"{endpoint_name}-with-capture",
        ProductionVariants=[...],  # Existing config
        DataCaptureConfig={
            "EnableCapture": True,
            "InitialSamplingPercentage": sampling_percentage,
            "DestinationS3Uri": data_capture_uri,
            "CaptureOptions": [
                {"CaptureMode": "Input"},   # Capture requests
                {"CaptureMode": "Output"},  # Capture responses
            ],
        },
    )
```

### Data Capture File Format

Captured data is stored in JSON Lines format:

```jsonl
# s3://bucket/monitoring/data-capture/2025/11/15/10/AllTraffic/2025-11-15T10-30-45.jsonl

{"captureData":{"endpointInput":{"observedContentType":"text/csv","mode":"INPUT","data":"6,148,72,35,0,33.6,0.627,50","encoding":"CSV"},"endpointOutput":{"observedContentType":"application/json","mode":"OUTPUT","data":"{\"predictions\":[1],\"probabilities\":[0.85]}","encoding":"JSON"}},"eventMetadata":{"eventId":"a1b2c3d4-e5f6-7890-abcd-ef1234567890","inferenceTime":"2025-11-15T10:30:45.123Z"},"eventVersion":"0"}
{"captureData":{"endpointInput":{...},"endpointOutput":{...}},"eventMetadata":{...},"eventVersion":"0"}
```

### S3 Directory Structure

```
s3://mlops-diabetes-dev-891807086260/
└── monitoring/
    ├── data-capture/                    # Raw captured data
    │   ├── 2025/
    │   │   └── 11/
    │   │       └── 15/
    │   │           └── 10/
    │   │               └── AllTraffic/
    │   │                   ├── 2025-11-15T10-00-00.jsonl  (15 MB)
    │   │                   ├── 2025-11-15T10-15-00.jsonl  (12 MB)
    │   │                   └── 2025-11-15T10-30-00.jsonl  (18 MB)
    │   
    ├── baseline/                        # Training data baseline
    │   ├── statistics.json              # Feature statistics
    │   ├── constraints.json             # Data quality constraints
    │   └── baseline_data.csv
    │
    ├── reports/                         # Monitoring results
    │   ├── 2025-11-15T11-00-00/
    │   │   ├── constraint_violations.json
    │   │   ├── statistics.json
    │   │   └── analysis.json
    │   └── 2025-11-15T12-00-00/
    │       └── ...
    │
    └── drift-detection/                 # Custom drift analysis
        └── 2025-11-15/
            ├── drift_report.json
            ├── feature_distributions.png
            └── psi_scores.csv
```

### Accessing Captured Data

```python
import boto3
import json

s3 = boto3.client('s3')
bucket = 'mlops-diabetes-dev-891807086260'
prefix = 'monitoring/data-capture/2025/11/15/'

# List all captured files
response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)

for obj in response.get('Contents', []):
    key = obj['Key']
    
    # Download file
    obj_data = s3.get_object(Bucket=bucket, Key=key)
    lines = obj_data['Body'].read().decode('utf-8').split('\n')
    
    # Parse JSON Lines
    for line in lines:
        if line:
            record = json.loads(line)
            
            # Extract input
            input_data = record['captureData']['endpointInput']['data']
            
            # Extract output
            output_data = record['captureData']['endpointOutput']['data']
            
            print(f"Input: {input_data}")
            print(f"Output: {output_data}")
```

### Cost Implications

| Requests/Day | Data Captured/Day | S3 Storage/Month | Cost/Month |
|--------------|-------------------|------------------|------------|
| 1,000 | 5 MB | 150 MB | $0.003 |
| 10,000 | 50 MB | 1.5 GB | $0.035 |
| 100,000 | 500 MB | 15 GB | $0.35 |
| 1,000,000 | 5 GB | 150 GB | $3.45 |

**Optimization tips:**
- Set `sampling_percentage` < 100 for high-traffic endpoints
- Use S3 Lifecycle policies to move old data to Glacier
- Delete data after analysis window (e.g., 30 days)

---

## Drift Detection

### What is Drift?

**Data Drift** (Covariate Shift): Input feature distributions change

```
TRAINING DATA (2024):              PRODUCTION DATA (2025):
────────────────────────────────   ────────────────────────────────
Age: Mean=45, Std=12               Age: Mean=55, Std=10  ⚠️ DRIFT!
BMI: Mean=28, Std=5                BMI: Mean=28, Std=5   ✅ No drift
Glucose: Mean=120, Std=30          Glucose: Mean=140, Std=35 ⚠️ DRIFT!

Why? Patient demographics changed (older population)
Action: Retrain model with recent data
```

**Concept Drift**: Relationship between features and target changes

```
TRAINING (2024):                   PRODUCTION (2025):
────────────────────────────────   ────────────────────────────────
BMI > 30 → 80% diabetes risk       BMI > 30 → 60% diabetes risk

Why? New treatment available, lifestyle changes
Action: Retrain model with new outcomes
```

### Statistical Tests for Drift

#### 1. Kolmogorov-Smirnov (KS) Test

**Purpose:** Compare two continuous distributions

**How it works:**
```
Baseline Distribution:    Current Distribution:
    │                         │
 40 │    ●●●●                40│       ●●●●
 30 │  ●●●●●●●●             30│     ●●●●●●●●
 20 │●●●●●●●●●●●●           20│   ●●●●●●●●●●●●
 10 │●●●●●●●●●●●●●●         10│ ●●●●●●●●●●●●●●●●
  0 └────────────────        0 └────────────────────
    50  70  90  110  130        60  80  100  120  140
         Glucose                      Glucose

KS Statistic = Maximum vertical distance between CDFs
P-value < 0.05 → Distributions are different (DRIFT!)
```

**Implementation:**
```python
# File: src/monitoring/drift_detection.py

def kolmogorov_smirnov_test(self, baseline_data, current_data, feature):
    """Perform KS test for distribution drift"""
    from scipy import stats
    
    statistic, p_value = stats.ks_2samp(
        baseline_data[feature],
        current_data[feature]
    )
    
    drift_detected = p_value < self.threshold  # Default: 0.05
    
    return {
        "feature": feature,
        "test": "Kolmogorov-Smirnov",
        "statistic": float(statistic),
        "p_value": float(p_value),
        "drift_detected": drift_detected,
        "threshold": self.threshold,
    }
```

**Interpretation:**
- **p_value >= 0.05**: No significant difference (no drift)
- **p_value < 0.05**: Significant difference (drift detected!)
- **statistic**: Magnitude of drift (0=identical, 1=completely different)

#### 2. Population Stability Index (PSI)

**Purpose:** Quantify distribution shift

**Formula:**
```
PSI = Σ (Actual% - Expected%) × ln(Actual% / Expected%)

Where:
- Expected% = % of training data in each bin
- Actual% = % of production data in each bin
```

**Interpretation:**
- **PSI < 0.1**: No significant change ✅
- **0.1 ≤ PSI < 0.2**: Small change ⚠️
- **PSI ≥ 0.2**: Significant change (DRIFT!) 🔴

**Example:**
```
Feature: Age
Bins: [0-30, 30-40, 40-50, 50-60, 60+]

Training Distribution:    Production Distribution:
Bin      Expected%        Bin      Actual%       Δ         Contribution
0-30     10%              0-30     5%           -5%        PSI += (0.05-0.10) × ln(0.05/0.10) = 0.035
30-40    20%              30-40    15%          -5%        PSI += ...
40-50    40%              40-50    30%          -10%       PSI += ...
50-60    20%              50-60    35%          +15%       PSI += ...
60+      10%              60+      15%          +5%        PSI += ...

Total PSI = 0.25 → SIGNIFICANT DRIFT! (PSI ≥ 0.2)
```

**Implementation:**
```python
def population_stability_index(self, baseline_data, current_data, feature, bins=10):
    """Calculate PSI for drift detection"""
    
    # Bin the data
    baseline_binned = pd.cut(baseline_data[feature], bins=bins)
    current_binned = pd.cut(current_data[feature], bins=bins)
    
    # Calculate proportions
    baseline_props = baseline_binned.value_counts(normalize=True)
    current_props = current_binned.value_counts(normalize=True)
    
    # Calculate PSI
    psi = np.sum(
        (current_props - baseline_props) * 
        np.log(current_props / baseline_props)
    )
    
    # Interpret
    if psi < 0.1:
        interpretation = "No significant change"
        drift_detected = False
    elif psi < 0.2:
        interpretation = "Small change"
        drift_detected = False
    else:
        interpretation = "Significant change (drift detected)"
        drift_detected = True
    
    return {
        "feature": feature,
        "test": "PSI",
        "psi_score": float(psi),
        "interpretation": interpretation,
        "drift_detected": drift_detected,
    }
```

#### 3. Chi-Square Test

**Purpose:** Compare categorical distributions or binned continuous data

**When to use:**
- Categorical features (e.g., blood type, gender)
- Binned continuous features (age groups, BMI categories)

**How it works:**
```
Observed (Production):    Expected (Training):
Category  Count           Category  Count       (O-E)²/E
─────────────────────────────────────────────────────────
Type A    150             Type A    100         25.0
Type B    100             Type B    120         3.33
Type O    200             Type O    250         10.0
Type AB   50              Type AB   30          13.33
                                    ──────────────────
                                    χ² = 51.66
                                    p-value = 0.0001

Result: p < 0.05 → Distributions differ (DRIFT!)
```

### Drift Detection Workflow

```
┌─────────────────────────────────────────────────────────────┐
│           AUTOMATED DRIFT DETECTION WORKFLOW                │
└─────────────────────────────────────────────────────────────┘

STEP 1: Baseline Creation (One-Time)
──────────────────────────────────────────────────────────────
Input: Training data (diabetes.csv)
Action: Calculate baseline statistics
Output: s3://.../monitoring/baseline/statistics.json

{
  "features": {
    "Glucose": {
      "mean": 120.5,
      "std": 30.2,
      "min": 44.0,
      "max": 199.0,
      "quantiles": {"25": 99.0, "50": 117.0, "75": 140.0}
    },
    "BMI": {...},
    ...
  }
}


STEP 2: Continuous Monitoring (Hourly/Daily)
──────────────────────────────────────────────────────────────
Trigger: EventBridge scheduled rule (cron: 0 */1 * * ? *)

T=0m    EventBridge triggers drift detection job
         ↓
T=1m    Read captured data from last hour
         s3://.../monitoring/data-capture/2025/11/15/10/
         ↓
T=2m    Extract input features from captured requests
         Parse JSON Lines → DataFrame (1000 samples)
         ↓
T=3m    Run statistical tests for each feature:
         ├─ KS Test (Glucose): p_value=0.001 → DRIFT! 🔴
         ├─ PSI (BMI): score=0.08 → No drift ✅
         ├─ KS Test (Age): p_value=0.12 → No drift ✅
         └─ PSI (BloodPressure): score=0.15 → Small change ⚠️
         ↓
T=5m    Generate drift report
         {
           "summary": {
             "total_features": 8,
             "features_with_drift": 1,
             "drift_percentage": 12.5
           },
           "features": [...]
         }
         ↓
T=6m    Save report to S3
         s3://.../monitoring/drift-detection/2025-11-15-10-00.json
         ↓
T=7m    Publish CloudWatch metrics
         MetricName: FeatureDrift
         Value: 12.5 (drift percentage)
         ↓
T=8m    Evaluate alerting rules
         IF drift_percentage > 20% THEN
            Publish to SNS topic
            Send email: "Drift detected in Glucose feature"
         END IF


STEP 3: MLOps Team Response
──────────────────────────────────────────────────────────────
Action 1: Investigate drift cause
          - Review feature distributions
          - Check data collection changes
          - Analyze business context changes

Action 2: Decide on response
          Option A: Data issue → Fix data pipeline
          Option B: Real distribution shift → Retrain model
          Option C: Temporary anomaly → Monitor further

Action 3: Implement fix
          IF retrain needed THEN
            1. Collect recent data
            2. Trigger training pipeline
            3. Evaluate new model
            4. Deploy if performance improves
          END IF
```

### Running Drift Detection

```bash
# Manual drift detection
python src/monitoring/run_drift_detection.py \
  --baseline-data s3://bucket/monitoring/baseline/baseline_data.csv \
  --current-data s3://bucket/monitoring/data-capture/2025/11/15/ \
  --output s3://bucket/monitoring/drift-detection/

# Output:
# Analyzing 8 features...
# ✅ Pregnancies: No drift (p=0.234)
# 🔴 Glucose: DRIFT DETECTED (p=0.001, PSI=0.32)
# ✅ BloodPressure: No drift (p=0.156)
# ⚠️  BMI: Small change (PSI=0.15)
# ✅ Insulin: No drift (p=0.445)
# ✅ DiabetesPedigreeFunction: No drift (p=0.089)
# ✅ Age: No drift (p=0.234)
# 
# Summary: 1/8 features with drift (12.5%)
# Recommendation: RETRAIN MODEL
```

---

## Model Quality Monitoring

### What is Model Quality?

Tracks how well the model performs on real production data (requires ground truth labels).

### The Ground Truth Challenge

```
PREDICTION TIME (T=0):          GROUND TRUTH TIME (T=days/weeks):
─────────────────────────────   ─────────────────────────────────
Patient visits clinic           Patient returns for follow-up
Model predicts: 85% diabetes    Doctor diagnoses: Diabetes confirmed
Probability                     
                                Weeks later, we know:
Record:                         Prediction was CORRECT! ✅
- patient_id: 12345
- prediction: 1 (diabetes)      Update metrics:
- probability: 0.85             - True Positive + 1
- timestamp: 2025-11-15         - Accuracy recalculated

⏳ DELAY: Days to months between prediction and truth
```

### Metrics Tracked

| Metric | Formula | Interpretation | Alert Threshold |
|--------|---------|----------------|-----------------|
| **Accuracy** | (TP + TN) / Total | Overall correctness | < 75% |
| **Precision** | TP / (TP + FP) | When predicts diabetes, how often correct? | < 70% |
| **Recall** | TP / (TP + FN) | Of all diabetes cases, how many caught? | < 70% |
| **F1-Score** | 2 × (Precision × Recall) / (Precision + Recall) | Balance of precision/recall | < 70% |
| **ROC-AUC** | Area under ROC curve | Model discrimination ability | < 0.80 |

### Model Quality Monitoring Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│              MODEL QUALITY MONITORING WORKFLOW                           │
└─────────────────────────────────────────────────────────────────────────┘

DAY 1: Predictions Made
─────────────────────────────────────────────────────────────────────────
10:00 AM  Patient 12345 → Prediction: Diabetes (prob=0.85)
10:05 AM  Patient 12346 → Prediction: No Diabetes (prob=0.15)
10:10 AM  Patient 12347 → Prediction: Diabetes (prob=0.92)
...

Predictions logged to:
s3://.../monitoring/predictions/2025-11-15/predictions.csv
patient_id,prediction,probability,timestamp
12345,1,0.85,2025-11-15T10:00:00Z
12346,0,0.15,2025-11-15T10:05:00Z
12347,1,0.92,2025-11-15T10:10:00Z


DAY 30: Ground Truth Arrives
─────────────────────────────────────────────────────────────────────────
Ground truth system updates:
s3://.../monitoring/ground-truth/2025-12-15/actuals.csv
patient_id,actual_diagnosis,diagnosis_date
12345,1,2025-12-15  # Diabetes confirmed ✅ (TP)
12346,0,2025-12-15  # No diabetes confirmed ✅ (TN)
12347,1,2025-12-15  # Diabetes confirmed ✅ (TP)


WEEKLY: Quality Evaluation Job
─────────────────────────────────────────────────────────────────────────
Trigger: Every Sunday at midnight

T=0m    Read predictions from past week
         s3://.../monitoring/predictions/2025-11-*/
         Total: 5,000 predictions
         ↓
T=1m    Read corresponding ground truth
         s3://.../monitoring/ground-truth/2025-12-*/
         Matched: 4,200 predictions (840 still pending)
         ↓
T=2m    Calculate confusion matrix
         
                  Predicted
                  0      1
         Actual 0 [2100] [300]  ← TN=2100, FP=300
                1 [400]  [1400] ← FN=400,  TP=1400
         
         ↓
T=3m    Calculate metrics
         
         Accuracy  = (2100 + 1400) / 4200 = 0.833 (83.3%)
         Precision = 1400 / (1400 + 300) = 0.824 (82.4%)
         Recall    = 1400 / (1400 + 400) = 0.778 (77.8%)
         F1-Score  = 2 × (0.824 × 0.778) / (0.824 + 0.778) = 0.800
         
         ↓
T=4m    Compare with baseline (from training)
         
         Metric      Training  Production  Change
         ──────────────────────────────────────────
         Accuracy    85.0%     83.3%       -1.7% ⚠️
         Precision   82.0%     82.4%       +0.4% ✅
         Recall      80.0%     77.8%       -2.2% ⚠️
         F1-Score    81.0%     80.0%       -1.0% ✅
         
         ↓
T=5m    Detect degradation
         
         IF (Accuracy < 75%) OR (F1-Score < 70%) THEN
            Status: CRITICAL DEGRADATION 🔴
            Action: Trigger retraining
         ELSE IF (Accuracy < 80%) OR (F1-Score < 75%) THEN
            Status: WARNING 🟡
            Action: Monitor closely
         ELSE
            Status: HEALTHY ✅
         END IF
         
         Current: WARNING 🟡 (Accuracy = 83.3%)
         ↓
T=6m    Publish results
         
         CloudWatch Metric:
         - ModelAccuracy: 83.3
         - ModelPrecision: 82.4
         - ModelRecall: 77.8
         
         S3 Report:
         s3://.../monitoring/model-quality/2025-11-15/report.json
         
         SNS Notification:
         "Model quality warning: Accuracy dropped to 83.3%"
```

### Implementation

```python
# File: src/monitoring/model_monitor.py (conceptual - needs ground truth integration)

def evaluate_model_quality(predictions_path, ground_truth_path):
    """
    Evaluate model quality with ground truth
    
    Args:
        predictions_path: S3 path to predictions
        ground_truth_path: S3 path to actual outcomes
    """
    # Load data
    predictions = pd.read_csv(predictions_path)
    ground_truth = pd.read_csv(ground_truth_path)
    
    # Join on patient_id
    joined = predictions.merge(ground_truth, on='patient_id')
    
    # Calculate metrics
    from sklearn.metrics import (
        accuracy_score, precision_score, recall_score, 
        f1_score, roc_auc_score, confusion_matrix
    )
    
    y_true = joined['actual_diagnosis']
    y_pred = joined['prediction']
    y_prob = joined['probability']
    
    metrics = {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred),
        'recall': recall_score(y_true, y_pred),
        'f1_score': f1_score(y_true, y_pred),
        'roc_auc': roc_auc_score(y_true, y_prob),
        'confusion_matrix': confusion_matrix(y_true, y_pred).tolist()
    }
    
    # Compare with baseline
    baseline_metrics = load_baseline_metrics()  # From training
    
    degradation_report = {
        'current': metrics,
        'baseline': baseline_metrics,
        'changes': {
            metric: metrics[metric] - baseline_metrics[metric]
            for metric in metrics if metric != 'confusion_matrix'
        }
    }
    
    # Determine status
    if metrics['accuracy'] < 0.75 or metrics['f1_score'] < 0.70:
        status = 'CRITICAL'
        action = 'RETRAIN_IMMEDIATELY'
    elif metrics['accuracy'] < 0.80 or metrics['f1_score'] < 0.75:
        status = 'WARNING'
        action = 'MONITOR_CLOSELY'
    else:
        status = 'HEALTHY'
        action = 'NONE'
    
    degradation_report['status'] = status
    degradation_report['action'] = action
    
    return degradation_report
```

---

## CloudWatch Integration

### Metrics Published

SageMaker automatically publishes these metrics to CloudWatch:

| Metric Name | Description | Unit | Typical Value |
|-------------|-------------|------|---------------|
| `Invocations` | Number of inference requests | Count | Varies by traffic |
| `InvocationsPerInstance` | Requests per endpoint instance | Count | < 1000 (for scaling) |
| `ModelLatency` | Time model takes to respond | Milliseconds | 50-200ms |
| `OverheadLatency` | SageMaker overhead time | Milliseconds | 10-50ms |
| `Invocation4XXErrors` | Client errors (bad requests) | Count | 0 (ideally) |
| `Invocation5XXErrors` | Server errors (model failures) | Count | 0 (ideally) |
| `ModelSetupTime` | Time to load model on startup | Milliseconds | 30-60 seconds |
| `CPUUtilization` | CPU usage % | Percent | < 70% |
| `MemoryUtilization` | Memory usage % | Percent | < 80% |
| `DiskUtilization` | Disk usage % | Percent | < 80% |

### Custom Metrics

You can publish custom metrics from your inference code:

```python
# In inference.py

import boto3

cloudwatch = boto3.client('cloudwatch')

def output_fn(predictions, response_content_type):
    """Serialize predictions and publish custom metrics"""
    
    # Extract prediction statistics
    avg_confidence = np.mean([p['confidence'] for p in predictions['predictions']])
    
    # Publish to CloudWatch
    cloudwatch.put_metric_data(
        Namespace='MLOps/Diabetes',
        MetricData=[
            {
                'MetricName': 'AveragePredictionConfidence',
                'Value': avg_confidence,
                'Unit': 'None',
                'Timestamp': datetime.utcnow()
            },
            {
                'MetricName': 'HighRiskPredictions',
                'Value': sum(1 for p in predictions['predictions'] if p['prediction'] == 1),
                'Unit': 'Count'
            }
        ]
    )
    
    return json.dumps(predictions)
```

### CloudWatch Alarms

Alarms trigger notifications when metrics exceed thresholds.

#### Creating Alarms

```python
# File: scripts/setup_cloudwatch_alarms.py

import boto3

cloudwatch = boto3.client('cloudwatch')

def create_latency_alarm(endpoint_name, threshold_ms=500):
    """Create alarm for high latency"""
    
    alarm_name = f"{endpoint_name}-high-latency"
    
    cloudwatch.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=2,  # Alert if threshold exceeded for 2 periods
        MetricName='ModelLatency',
        Namespace='AWS/SageMaker',
        Period=300,  # 5 minutes
        Statistic='Average',
        Threshold=threshold_ms,
        ActionsEnabled=True,
        AlarmActions=[
            'arn:aws:sns:us-east-1:891807086260:mlops-alerts'
        ],
        AlarmDescription=f'Alert when endpoint latency > {threshold_ms}ms',
        Dimensions=[
            {'Name': 'EndpointName', 'Value': endpoint_name},
            {'Name': 'VariantName', 'Value': 'AllTraffic'}
        ],
        TreatMissingData='notBreaching'
    )
    
    print(f"✅ Created alarm: {alarm_name}")

def create_error_rate_alarm(endpoint_name, threshold_percent=5):
    """Create alarm for high error rate"""
    
    alarm_name = f"{endpoint_name}-high-error-rate"
    
    # Use metric math to calculate error rate
    cloudwatch.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=1,
        Threshold=threshold_percent,
        ActionsEnabled=True,
        AlarmActions=[
            'arn:aws:sns:us-east-1:891807086260:mlops-alerts'
        ],
        Metrics=[
            {
                'Id': 'errors',
                'ReturnData': False,
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/SageMaker',
                        'MetricName': 'Invocation5XXErrors',
                        'Dimensions': [
                            {'Name': 'EndpointName', 'Value': endpoint_name}
                        ]
                    },
                    'Period': 300,
                    'Stat': 'Sum'
                }
            },
            {
                'Id': 'requests',
                'ReturnData': False,
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/SageMaker',
                        'MetricName': 'Invocations',
                        'Dimensions': [
                            {'Name': 'EndpointName', 'Value': endpoint_name}
                        ]
                    },
                    'Period': 300,
                    'Stat': 'Sum'
                }
            },
            {
                'Id': 'error_rate',
                'Expression': '(errors / requests) * 100',
                'ReturnData': True
            }
        ]
    )
    
    print(f"✅ Created alarm: {alarm_name}")

# Create all alarms
create_latency_alarm('diabetes-classifier-prod', threshold_ms=500)
create_error_rate_alarm('diabetes-classifier-prod', threshold_percent=5)
```

#### Alarm States

```
ALARM LIFECYCLE:
────────────────────────────────────────────────────────────

State: OK (Green)
├─ Metric: ModelLatency = 200ms (threshold: 500ms)
├─ Status: Normal operation ✅
└─ Action: None

        ↓ (Latency increases)

State: ALARM (Red)
├─ Metric: ModelLatency = 650ms (threshold: 500ms)
├─ Status: Threshold breached for 2 evaluation periods 🔴
├─ Action: Send SNS notification
└─ Team notified: "Endpoint latency alarm triggered"

        ↓ (Team investigates & scales endpoint)

State: OK (Green)
├─ Metric: ModelLatency = 180ms (threshold: 500ms)
├─ Status: Returned to normal ✅
└─ Action: Send recovery notification
```

### CloudWatch Dashboards

Create custom dashboards for real-time monitoring:

```python
import boto3
import json

cloudwatch = boto3.client('cloudwatch')

dashboard_body = {
    "widgets": [
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    ["AWS/SageMaker", "Invocations", {"stat": "Sum"}],
                    [".", "ModelLatency", {"stat": "Average"}],
                    [".", "Invocation5XXErrors", {"stat": "Sum"}]
                ],
                "period": 300,
                "stat": "Average",
                "region": "us-east-1",
                "title": "Endpoint Health"
            }
        },
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    ["MLOps/Diabetes", "AveragePredictionConfidence"],
                    [".", "HighRiskPredictions", {"stat": "Sum"}]
                ],
                "period": 300,
                "stat": "Average",
                "region": "us-east-1",
                "title": "Prediction Metrics"
            }
        }
    ]
}

cloudwatch.put_dashboard(
    DashboardName='MLOps-Diabetes-Dashboard',
    DashboardBody=json.dumps(dashboard_body)
)

print("✅ Dashboard created: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=MLOps-Diabetes-Dashboard")
```

---

## Alerting & Notifications

### SNS Topic Setup

```bash
# Create SNS topic
aws sns create-topic --name mlops-alerts

# Subscribe email
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:891807086260:mlops-alerts \
  --protocol email \
  --notification-endpoint your-email@example.com

# Confirm subscription (check your email)
```

### Alert Types

| Alert Type | Trigger | Severity | Response Time |
|------------|---------|----------|---------------|
| **Endpoint Down** | Endpoint status ≠ InService | 🔴 Critical | Immediate |
| **High Latency** | p95 latency > 500ms | 🟡 Warning | 1 hour |
| **High Error Rate** | 5XX errors > 5% | 🔴 Critical | 30 minutes |
| **Drift Detected** | PSI > 0.2 on key features | 🟡 Warning | 1 day |
| **Quality Degradation** | Accuracy < 75% | 🔴 Critical | 1 day |
| **Low Traffic** | Invocations = 0 for 1 hour | 🟡 Warning | 2 hours |

### Slack Integration

```python
import requests
import json

def send_slack_alert(webhook_url, alert_data):
    """Send alert to Slack"""
    
    # Format message
    message = {
        "text": f"🚨 MLOps Alert: {alert_data['title']}",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🚨 {alert_data['title']}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Endpoint:*\n{alert_data['endpoint']}"},
                    {"type": "mrkdwn", "text": f"*Severity:*\n{alert_data['severity']}"},
                    {"type": "mrkdwn", "text": f"*Metric:*\n{alert_data['metric']}"},
                    {"type": "mrkdwn", "text": f"*Value:*\n{alert_data['value']}"}
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Details:*\n{alert_data['description']}"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View Dashboard"},
                        "url": alert_data['dashboard_url']
                    }
                ]
            }
        ]
    }
    
    # Send to Slack
    response = requests.post(webhook_url, json=message)
    
    if response.status_code == 200:
        print("✅ Slack alert sent")
    else:
        print(f"❌ Failed to send Slack alert: {response.text}")

# Example usage
send_slack_alert(
    webhook_url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    alert_data={
        "title": "High Endpoint Latency",
        "endpoint": "diabetes-classifier-prod",
        "severity": "WARNING",
        "metric": "ModelLatency",
        "value": "650ms (threshold: 500ms)",
        "description": "Endpoint latency has exceeded threshold for 2 consecutive periods",
        "dashboard_url": "https://console.aws.amazon.com/cloudwatch/..."
    }
)
```

---

## Implementation Guide

### Step-by-Step Setup

#### Phase 1: Enable Data Capture

```bash
# 1. Enable data capture on existing endpoint
python src/monitoring/model_monitor.py \
  --endpoint-name diabetes-classifier-dev \
  --enable-capture

# Output:
# Enabling data capture for endpoint: diabetes-classifier-dev
# Data capture enabled. Data will be saved to s3://bucket/monitoring/data-capture
# Endpoint is being updated. This may take a few minutes...

# 2. Verify data capture is working
aws s3 ls s3://mlops-diabetes-dev-891807086260/monitoring/data-capture/ --recursive

# Should see files appear after a few inference requests
```

#### Phase 2: Create Baseline

```bash
# 3. Create monitoring baseline from training data
python src/monitoring/model_monitor.py \
  --endpoint-name diabetes-classifier-dev \
  --baseline-data s3://bucket/data/train/train.csv \
  --create-baseline

# Output:
# Creating monitoring baseline...
# Analyzing baseline dataset: s3://bucket/data/train/train.csv
# Baseline job started: diabetes-baseline-job-2025-11-15-10-30
# Waiting for baseline job to complete... (this may take 10-15 minutes)
# Baseline created successfully at s3://bucket/monitoring/baseline
```

#### Phase 3: Create Monitoring Schedule

```bash
# 4. Create hourly monitoring schedule
python src/monitoring/model_monitor.py \
  --endpoint-name diabetes-classifier-dev \
  --create-schedule

# Output:
# Creating monitoring schedule: diabetes-classifier-dev-mon
# Monitoring schedule created: diabetes-classifier-dev-mon
# Monitoring reports will be saved to s3://bucket/monitoring/reports
# Schedule: Hourly (cron: 0 * * * ? *)
```

#### Phase 4: Setup CloudWatch Alarms

```bash
# 5. Create CloudWatch alarms
python scripts/setup_cloudwatch_alarms.py \
  --endpoint-name diabetes-classifier-dev \
  --sns-topic-arn arn:aws:sns:us-east-1:891807086260:mlops-alerts

# Output:
# ✅ Created alarm: diabetes-classifier-dev-high-latency
# ✅ Created alarm: diabetes-classifier-dev-high-error-rate
# ✅ Created alarm: diabetes-classifier-dev-low-invocations
# ✅ Created alarm: diabetes-classifier-dev-model-errors
```

#### Phase 5: Setup Drift Detection

```bash
# 6. Run drift detection (manual test)
python src/monitoring/run_drift_detection.py \
  --baseline-data s3://bucket/data/train/train.csv \
  --current-data s3://bucket/monitoring/data-capture/2025/11/15/ \
  --output s3://bucket/monitoring/drift-detection/

# 7. Schedule drift detection (daily)
# Add to EventBridge:
# Rule: drift-detection-daily
# Schedule: cron(0 0 * * ? *)  # Daily at midnight
# Target: Lambda function that runs drift_detection.py
```

### Verification Checklist

```
✅ MONITORING SETUP CHECKLIST:
────────────────────────────────────────────────────────────

Phase 1: Data Capture
├─ [ ] Data capture enabled on endpoint
├─ [ ] Captured files appearing in S3
├─ [ ] Sampling percentage configured (100% for dev, lower for prod)
└─ [ ] S3 lifecycle policy configured (delete after 30 days)

Phase 2: Baseline
├─ [ ] Baseline job completed successfully
├─ [ ] statistics.json exists in S3
├─ [ ] constraints.json exists in S3
└─ [ ] Baseline covers all features

Phase 3: Monitoring Schedule
├─ [ ] Monitoring schedule created
├─ [ ] First monitoring execution completed
├─ [ ] Monitoring reports appearing in S3
└─ [ ] No violations in initial reports

Phase 4: Alarms
├─ [ ] Latency alarm created
├─ [ ] Error rate alarm created
├─ [ ] Low invocations alarm created
├─ [ ] Model errors alarm created
└─ [ ] SNS topic subscribed with email

Phase 5: Drift Detection
├─ [ ] Drift detection script tested
├─ [ ] EventBridge rule created
├─ [ ] Drift reports generated
└─ [ ] Alerts configured for drift > 20%

Phase 6: Dashboards
├─ [ ] CloudWatch dashboard created
├─ [ ] All key metrics displayed
├─ [ ] Dashboard shared with team
└─ [ ] Mobile alerts configured
```

---

## Troubleshooting

### Common Issues

#### 1. No Data in S3 Data Capture

**Symptom:** S3 bucket empty after enabling data capture

**Causes:**
- Data capture not actually enabled
- No inference requests made
- Sampling percentage too low
- S3 permissions issue

**Solutions:**
```bash
# Check endpoint config
aws sagemaker describe-endpoint \
  --endpoint-name diabetes-classifier-dev \
  --query 'DataCaptureConfig'

# Should show:
# {
#     "EnableCapture": true,
#     "CurrentSamplingPercentage": 100,
#     "DestinationS3Uri": "s3://bucket/monitoring/data-capture"
# }

# Test inference
python scripts/test_inference.py --endpoint-name diabetes-classifier-dev

# Check S3 (may take up to 5 minutes to appear)
aws s3 ls s3://bucket/monitoring/data-capture/ --recursive
```

#### 2. Monitoring Schedule Failing

**Symptom:** MonitoringExecutionStatus = "Failed"

**Causes:**
- Baseline missing or invalid
- No captured data to analyze
- Insufficient IAM permissions
- Instance type too small

**Solutions:**
```bash
# Check monitoring execution logs
aws sagemaker list-monitoring-executions \
  --monitoring-schedule-name diabetes-classifier-dev-mon \
  --max-results 1

# Get processing job name from output
aws sagemaker describe-processing-job \
  --processing-job-name <job-name>

# Check CloudWatch logs
aws logs tail /aws/sagemaker/ProcessingJobs --follow

# Common fix: Increase instance size
# Edit monitoring schedule, change instance_type to ml.m5.xlarge
```

#### 3. False Positive Drift Alerts

**Symptom:** Drift detected but data looks normal

**Causes:**
- Threshold too sensitive (p_value = 0.05)
- Small sample size
- Temporary spike in data
- Seasonality not accounted for

**Solutions:**
```python
# Adjust drift detector threshold
detector = DriftDetector(threshold=0.01)  # More conservative

# Increase minimum sample size
if len(current_data) < 1000:
    logger.warning("Sample size too small for reliable drift detection")
    return None

# Use rolling window instead of single point
rolling_drift = []
for week in last_4_weeks:
    drift = detector.detect_feature_drift(baseline, week_data)
    rolling_drift.append(drift['summary']['drift_percentage'])

# Alert only if consistent drift
if np.mean(rolling_drift) > 20:
    send_alert("Persistent drift detected")
```

#### 4. High Monitoring Costs

**Symptom:** Monitoring costs unexpectedly high

**Solutions:**
```python
# 1. Reduce data capture sampling
update_data_capture_config(sampling_percentage=10)  # Capture 10%

# 2. Reduce monitoring frequency
monitor.create_monitoring_schedule(
    schedule_cron_expression=CronExpressionGenerator.daily()  # Daily instead of hourly
)

# 3. Use smaller monitoring instances
instance_type='ml.t3.medium'  # Instead of ml.m5.xlarge

# 4. Setup S3 lifecycle policy
aws s3api put-bucket-lifecycle-configuration \
  --bucket mlops-diabetes-dev-891807086260 \
  --lifecycle-configuration file://lifecycle.json

# lifecycle.json:
{
  "Rules": [
    {
      "Id": "DeleteOldCapturedData",
      "Status": "Enabled",
      "Filter": {"Prefix": "monitoring/data-capture/"},
      "Expiration": {"Days": 30}
    }
  ]
}
```

---

## Cost Analysis

### Monitoring Cost Breakdown

```
MONTHLY COST ESTIMATE (1M predictions/month):
────────────────────────────────────────────────────────────

Data Capture:
├─ S3 Storage: 150 GB × $0.023/GB = $3.45
├─ S3 PUT requests: 1M × $0.005/1000 = $5.00
└─ Data Transfer: Minimal (same region) = $0.50

SageMaker Model Monitor:
├─ Processing job: ml.m5.xlarge
│  ├─ 24 executions/day × 0.25 hours × $0.23/hour = $1.38/day
│  └─ Monthly: $1.38 × 30 = $41.40
├─ Baseline creation: One-time $0.25
└─ Storage: Monitoring reports ~5 GB × $0.023 = $0.12

CloudWatch:
├─ Custom metrics: 10 metrics × $0.30 = $3.00
├─ Alarms: 5 alarms × $0.10 = $0.50
├─ Logs: 10 GB × $0.50/GB = $5.00
└─ Dashboard: Free

Drift Detection:
├─ Lambda executions: 30/month × $0.20 = $0.02
├─ Processing: Included in monitor cost
└─ S3 storage: Included above

SNS Notifications:
└─ Email notifications: Free (< 1000/month)

────────────────────────────────────────────────────────────
TOTAL MONTHLY COST: ~$59/month

Optimization for lower traffic (10K predictions/day):
- Reduce sampling to 10%: Save $4/month
- Monitor every 6 hours instead of hourly: Save $30/month
- Use ml.t3.medium: Save $20/month
OPTIMIZED TOTAL: ~$10/month
```

### Cost Optimization Strategies

| Strategy | Savings | Trade-off |
|----------|---------|-----------|
| Reduce data capture sampling from 100% to 10% | 10% | Smaller analysis sample |
| Monitor every 6 hours instead of hourly | 75% | Slower drift detection |
| Use ml.t3.medium instead of ml.m5.xlarge | 50% | Longer processing time |
| Delete captured data after 7 days | 75% | Shorter history |
| Disable monitoring in dev environment | 100% | No dev monitoring |

---

## Summary

**Monitoring is essential for production ML systems.** This guide covered:

✅ **Data Capture**: Log all requests/responses to S3  
✅ **Drift Detection**: Statistical tests (KS, PSI, Chi-Square)  
✅ **Model Quality**: Track accuracy, precision, recall with ground truth  
✅ **CloudWatch**: Real-time metrics, alarms, dashboards  
✅ **Alerting**: SNS, Slack, email notifications  
✅ **Implementation**: Step-by-step setup with verification  
✅ **Troubleshooting**: Common issues and solutions  
✅ **Cost Analysis**: Breakdown and optimization strategies

**Next Steps:**
1. Enable data capture on your endpoints
2. Create baseline from training data
3. Setup monitoring schedules
4. Configure CloudWatch alarms
5. Test end-to-end with sample predictions
6. Document runbooks for common alerts

**Remember:** Monitoring is not "set and forget" - regularly review drift reports, adjust thresholds, and update baselines as your data evolves! 🚀
