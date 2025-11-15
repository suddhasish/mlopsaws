# Inference.py Integration Plan

**Date:** November 15, 2025  
**Branch:** feature/production-grade-deployment  
**Goal:** Integrate custom `inference.py` handlers without breaking existing functionality

---

## Current vs Proposed Implementation

### **Current Implementation (train.py)**

```python
def model_fn(model_dir):
    """Load model for inference"""
    model_file = os.path.join(model_dir, "xgboost-model")
    booster = xgb.Booster()
    booster.load_model(model_file)
    return booster  # ← Returns just the model

# Uses XGBoost default handlers:
# - input_fn: CSV only (text/csv)
# - predict_fn: Basic XGBoost prediction
# - output_fn: JSON array of predictions
```

**Limitations:**
- ❌ No JSON input support
- ❌ No preprocessing (scaler not loaded)
- ❌ No rich response format
- ❌ No error handling
- ❌ No feature metadata validation

---

### **Proposed Implementation (inference.py)**

```python
def model_fn(model_dir):
    """Load model with all artifacts"""
    # Extracts model.tar.gz if needed
    # Tries multiple model filenames
    # Loads scaler.pkl (for preprocessing)
    # Loads feature_metadata.json
    return {
        "model": booster,
        "scaler": scaler,      # ← NEW: For feature scaling
        "metadata": metadata   # ← NEW: For validation
    }

def input_fn(request_body, content_type):
    """Deserialize input"""
    # Supports: application/json, text/csv
    # Handles multiple JSON formats:
    #   - {"instances": [[...], [...]]}
    #   - {"features": [...]}
    #   - Raw arrays
    return np.array(data)

def predict_fn(input_data, model_dict):
    """Make predictions with preprocessing"""
    if scaler:
        input_data = scaler.transform(input_data)  # ← NEW: Apply scaling
    predictions = model.predict(dmatrix)
    return {
        "predictions": class_predictions,
        "probabilities": probabilities
    }

def output_fn(predictions, response_type):
    """Serialize predictions"""
    # Rich response format:
    # {
    #   "predictions": [{
    #     "prediction": 1,
    #     "label": "Diabetes",
    #     "probability": 0.85,
    #     "confidence": 0.85
    #   }],
    #   "model_version": "1.0",
    #   "timestamp": "2025-11-15T10:30:00"
    # }
```

**Benefits:**
- ✅ JSON input support (REST API friendly)
- ✅ Automatic feature scaling (if scaler exists)
- ✅ Rich response with labels + confidence
- ✅ Robust error handling
- ✅ Better logging for debugging

---

## Key Differences

| Feature | train.py (Current) | inference.py (Proposed) | Breaking Change? |
|---------|-------------------|------------------------|------------------|
| **Return Type** | XGBoost Booster | Dict with model+scaler+metadata | ⚠️ YES - predict_fn signature changes |
| **Input Formats** | CSV only | CSV + JSON | ✅ NO - Backward compatible |
| **Preprocessing** | None | Scaler applied if available | ✅ NO - Optional |
| **Output Format** | Simple array | Rich JSON with labels | ⚠️ MAYBE - Depends on client expectations |
| **Error Handling** | Minimal | Extensive with logging | ✅ NO - Improvement |
| **Model Loading** | Single filename | Tries multiple filenames | ✅ NO - More robust |

---

## Risk Assessment

### 🔴 **HIGH RISK: Breaking Changes**

1. **model_fn Return Type Change**
   - **Current:** Returns `XGBoost Booster` object
   - **Proposed:** Returns `dict` with `{"model": ..., "scaler": ..., "metadata": ...}`
   - **Impact:** `predict_fn` must change to access `model_dict["model"]`
   - **Mitigation:** Update both functions together atomically

2. **Output Format Change**
   - **Current:** `[0, 1, 0]` (simple array)
   - **Proposed:** `{"predictions": [{"prediction": 0, "label": "No Diabetes", ...}]}`
   - **Impact:** API clients expecting old format will break
   - **Mitigation:** Version the endpoint or provide backward compatibility flag

### 🟡 **MEDIUM RISK: Optional Features**

3. **Scaler Dependency**
   - **Issue:** If scaler.pkl doesn't exist, scaling is skipped
   - **Impact:** Predictions might be wrong if training used scaling
   - **Current:** Training DOES save scaler (preprocessing.py line ~50)
   - **Mitigation:** Already handled - scaler is optional in inference.py

4. **Metadata Files**
   - **Issue:** feature_metadata.json may not exist in older models
   - **Impact:** Validation skipped, but inference still works
   - **Mitigation:** Already handled - metadata is optional

### 🟢 **LOW RISK: Improvements**

5. **Extended Input Support**
   - **Issue:** None - only adds JSON support, doesn't remove CSV
   - **Impact:** Positive - more flexibility
   - **Mitigation:** None needed

---

## Integration Strategy

### **Phase 1: Preparation (No Breaking Changes)**

#### Step 1.1: Verify Current Model Artifacts

```bash
# Check what's in your current model.tar.gz
aws s3 cp s3://mlops-diabetes-dev-891807086260/models/diabetes-training-*/output/model.tar.gz .
tar -tzf model.tar.gz

# Expected contents:
# xgboost-model          ✅ Required
# scaler.pkl             ✅ Should exist (from preprocessing)
# feature_metadata.json  ❓ May not exist
# feature_importance.json ✅ Optional
```

**Action:** Document what files exist

#### Step 1.2: Add Missing Artifacts to Training

Update `src/training/train.py` to save feature metadata:

```python
def train(args):
    # ... existing training code ...
    
    # AFTER model is saved (around line 150)
    
    # Save feature metadata
    feature_metadata = {
        "feature_count": dtrain.num_col(),
        "feature_names": ["Pregnancies", "Glucose", "BloodPressure", 
                         "SkinThickness", "Insulin", "BMI", 
                         "DiabetesPedigreeFunction", "Age"],
        "model_type": "xgboost",
        "version": "1.0"
    }
    
    metadata_path = os.path.join(args.model_dir, "feature_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(feature_metadata, f, indent=2)
    
    logger.info(f"Saved feature metadata to {metadata_path}")
```

**Action:** Add metadata saving (backward compatible - doesn't break existing deployments)

---

### **Phase 2: Package inference.py with Model**

#### Step 2.1: Update Training Pipeline

**File:** `pipelines/training_pipeline.py`

**Current code (around line 220-240):**
```python
xgb_estimator = XGBoost(
    entry_point="src/training/train.py",
    framework_version="1.5-1",
    # ... other params ...
)
```

**Updated code:**
```python
xgb_estimator = XGBoost(
    entry_point="train.py",                    # ← Relative to source_dir
    source_dir="src/training",                 # ← NEW: Package directory
    dependencies=["../deployment/inference.py"], # ← NEW: Include inference.py
    framework_version="1.5-1",
    # ... other params ...
)
```

**What this does:**
- Packages `src/training/train.py` → `/opt/ml/code/train.py`
- Packages `src/deployment/inference.py` → `/opt/ml/code/inference.py`
- Both files included in `model.tar.gz`

**Alternative (Manual Copy in train.py):**
```python
# At end of train() function in train.py
import shutil

# Copy inference.py to model directory
inference_src = os.path.join(os.path.dirname(__file__), "../deployment/inference.py")
inference_dst = os.path.join(args.model_dir, "code", "inference.py")
os.makedirs(os.path.dirname(inference_dst), exist_ok=True)
shutil.copy(inference_src, inference_dst)
logger.info(f"Packaged inference.py to {inference_dst}")
```

---

### **Phase 3: Backward Compatible Inference.py**

#### Step 3.1: Add Compatibility Mode

Update `src/deployment/inference.py` to support both old and new clients:

```python
# Add at top of file
COMPATIBILITY_MODE = os.environ.get("INFERENCE_COMPATIBILITY_MODE", "v2")

def output_fn(predictions, response_content_type):
    """Serialize predictions with backward compatibility"""
    
    if COMPATIBILITY_MODE == "v1":
        # OLD FORMAT (for existing clients)
        return json.dumps(predictions["predictions"])
    
    # NEW FORMAT (rich response)
    predictions_with_labels = []
    for pred, prob in zip(predictions["predictions"], predictions["probabilities"]):
        predictions_with_labels.append({
            "prediction": int(pred),
            "label": "Diabetes" if pred == 1 else "No Diabetes",
            "probability": float(prob),
            "confidence": float(prob) if pred == 1 else float(1 - prob),
        })
    
    response = {
        "predictions": predictions_with_labels,
        "model_version": "1.0",
        "timestamp": str(pd.Timestamp.now()),
    }
    
    return json.dumps(response)
```

**Usage:**
- New endpoints: Default to v2 (rich format)
- Old endpoints: Set environment variable `INFERENCE_COMPATIBILITY_MODE=v1`

---

### **Phase 4: Testing Strategy**

#### Step 4.1: Local Testing (Before Deployment)

```bash
# Test inference.py locally
cd src/deployment
python inference.py

# Expected output:
# INFO:__main__:Testing inference handler...
# INFO:__main__:Processed input shape: (2, 8)
# INFO:__main__:Inference handler test completed
```

#### Step 4.2: Test Endpoint with Both Formats

**CSV Input (Existing):**
```bash
aws sagemaker-runtime invoke-endpoint \
  --endpoint-name diabetes-classifier-dev \
  --content-type text/csv \
  --body '6,148,72,35,0,33.6,0.627,50' \
  output.json

cat output.json
# Should work with both old and new inference.py
```

**JSON Input (New Feature):**
```bash
aws sagemaker-runtime invoke-endpoint \
  --endpoint-name diabetes-classifier-dev \
  --content-type application/json \
  --body '{"instances": [[6,148,72,35,0,33.6,0.627,50]]}' \
  output.json

cat output.json
# Expected (v2 format):
# {
#   "predictions": [{
#     "prediction": 1,
#     "label": "Diabetes",
#     "probability": 0.85,
#     "confidence": 0.85
#   }],
#   "model_version": "1.0",
#   "timestamp": "2025-11-15T10:30:00.123456"
# }
```

#### Step 4.3: Compare Predictions

```python
# Test script to verify predictions match
import boto3
import json

runtime = boto3.client('sagemaker-runtime')

# Test data
test_input = [[6, 148, 72, 35, 0, 33.6, 0.627, 50]]

# Test CSV (old format)
csv_body = ','.join(map(str, test_input[0]))
csv_response = runtime.invoke_endpoint(
    EndpointName='diabetes-classifier-dev',
    ContentType='text/csv',
    Body=csv_body
)
csv_result = json.loads(csv_response['Body'].read())

# Test JSON (new format)
json_body = json.dumps({"instances": test_input})
json_response = runtime.invoke_endpoint(
    EndpointName='diabetes-classifier-dev',
    ContentType='application/json',
    Body=json_body
)
json_result = json.loads(json_response['Body'].read())

# Compare predictions
print("CSV prediction:", csv_result)
print("JSON prediction:", json_result)

# Extract prediction values
csv_pred = csv_result[0] if isinstance(csv_result, list) else csv_result['predictions'][0]['prediction']
json_pred = json_result['predictions'][0]['prediction']

assert csv_pred == json_pred, f"Predictions don't match! CSV={csv_pred}, JSON={json_pred}"
print("✅ Predictions match!")
```

---

## Step-by-Step Execution Plan

### ✅ **Step 1: Verify Current State (Safe)**

```bash
# 1. Check current endpoint works
python scripts/test_inference.py --endpoint-name diabetes-classifier-dev

# 2. Check model artifacts
aws s3 ls s3://mlops-diabetes-dev-891807086260/models/ --recursive | grep model.tar.gz | tail -1
```

### ✅ **Step 2: Add Feature Metadata (Safe - Backward Compatible)**

1. Edit `src/training/train.py`
2. Add feature metadata saving (code provided above)
3. Commit: `git add src/training/train.py`
4. Commit: `git commit -m "feat: add feature metadata to model artifacts"`

### ✅ **Step 3: Update Training Pipeline to Package inference.py**

1. Edit `pipelines/training_pipeline.py`
2. Add `source_dir` and `dependencies` (code provided above)
3. Commit: `git add pipelines/training_pipeline.py`
4. Commit: `git commit -m "feat: package inference.py with model"`

### ⚠️ **Step 4: Retrain Model (Creates New Model Package)**

```bash
# Execute training pipeline with new packaging
python pipelines/training_pipeline.py --execute

# This creates a NEW model version with inference.py included
# Old models still work (they just won't use custom inference.py)
```

### ⚠️ **Step 5: Deploy to Test Endpoint**

```bash
# Deploy new model to TEST endpoint first
python src/deployment/deploy.py --endpoint-name diabetes-classifier-test

# Wait for endpoint to be InService
aws sagemaker describe-endpoint --endpoint-name diabetes-classifier-test
```

### ✅ **Step 6: Validate Test Endpoint**

```bash
# Test CSV (should still work)
python scripts/test_inference.py --endpoint-name diabetes-classifier-test

# Test JSON (new feature)
curl -X POST https://runtime.sagemaker.us-east-1.amazonaws.com/endpoints/diabetes-classifier-test/invocations \
  -H "Content-Type: application/json" \
  -d '{"instances": [[6,148,72,35,0,33.6,0.627,50]]}'
```

### ⚠️ **Step 7: Deploy to Production (After Validation)**

```bash
# Only after test endpoint validation passes
python src/deployment/deploy.py --endpoint-name diabetes-classifier-prod
```

---

## Rollback Plan

If anything breaks:

### **Rollback Option 1: Revert Code**
```bash
git revert HEAD~2  # Undo last 2 commits
python pipelines/training_pipeline.py --execute  # Retrain with old code
```

### **Rollback Option 2: Deploy Previous Model Version**
```bash
# List model versions
aws sagemaker list-model-packages \
  --model-package-group-name mlops-diabetes-model-group-dev

# Deploy previous version
export OLD_MODEL_ARN="arn:aws:sagemaker:us-east-1:891807086260:model-package/mlops-diabetes-model-group-dev/1"
python src/deployment/deploy.py --model-package-arn $OLD_MODEL_ARN
```

### **Rollback Option 3: Blue/Green Deployment**
```bash
# Keep old endpoint running
# Deploy new version to separate endpoint
# Test extensively
# Switch traffic only when confident
```

---

## Success Criteria

✅ **Must Have:**
- [ ] CSV input still works (backward compatibility)
- [ ] Predictions match between old and new model
- [ ] Endpoint latency < 500ms (p95)
- [ ] No errors in CloudWatch logs

✅ **Should Have:**
- [ ] JSON input works
- [ ] Rich response format available
- [ ] Scaler correctly applied (if exists)
- [ ] Feature metadata loaded (if exists)

✅ **Nice to Have:**
- [ ] Better error messages in responses
- [ ] Request/response logging improved
- [ ] Confidence scores in output

---

## Timeline

| Phase | Duration | Risk | Can Rollback? |
|-------|----------|------|---------------|
| 1. Verify Current State | 30 min | None | N/A |
| 2. Add Feature Metadata | 1 hour | Low | Yes - Just commit |
| 3. Update Pipeline | 1 hour | Low | Yes - Just commit |
| 4. Retrain Model | 20 min | Low | Yes - Use old model |
| 5. Deploy to Test | 10 min | Medium | Yes - Delete endpoint |
| 6. Validate | 2 hours | Low | Yes - Deploy old model |
| 7. Deploy to Prod | 10 min | High | Yes - Deploy old model |
| **Total** | **~5-6 hours** | **Manageable** | **Yes at every step** |

---

## Decision Matrix

| Scenario | Recommendation |
|----------|----------------|
| **You need JSON API support urgently** | Proceed with integration |
| **You have active production traffic** | Use blue/green deployment |
| **You're in early development** | Proceed with direct replacement |
| **You want zero risk** | Deploy to new endpoint first, test for 1 week, then switch traffic |
| **You need backward compatibility** | Add COMPATIBILITY_MODE environment variable |

---

## Final Recommendation

**Proceed with integration using this sequence:**

1. ✅ **LOW RISK:** Add feature metadata (doesn't affect inference)
2. ✅ **LOW RISK:** Update pipeline to package inference.py
3. ⚠️ **MEDIUM RISK:** Deploy to TEST endpoint first
4. ✅ **VALIDATE:** Extensive testing on test endpoint
5. ⚠️ **HIGH RISK:** Deploy to production only after validation passes

**Expected outcome:** More robust inference with JSON support, better error handling, and backward compatibility maintained! 🚀
