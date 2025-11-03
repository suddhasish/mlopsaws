# 🔐 Model Approval & Quality Gates

## ❓ Your Questions Answered

### Q1: "Is it going to register all models irrespective of model score improved or not?"

**Answer: NO ❌**

Models are **NOT** automatically registered. They go through a **2-stage approval process**:

---

## 🎯 Two-Stage Approval Process

### Stage 1: Automated Quality Gates ✅ (Happens ALWAYS)

Every trained model must pass **ALL THREE** metrics thresholds simultaneously:

```python
# In pipelines/training_pipeline.py - create_condition_step()

# CONDITION 1: Accuracy Check
if accuracy < 0.75:  # DEV: 0.70, STAGING: 0.75, PROD: 0.78
    ❌ REJECT - Model NOT registered
    
# CONDITION 2: F1-Score Check  
if f1_score < 0.70:  # DEV: 0.65, STAGING: 0.70, PROD: 0.73
    ❌ REJECT - Model NOT registered
    
# CONDITION 3: ROC-AUC Check
if roc_auc < 0.80:  # DEV: 0.75, STAGING: 0.80, PROD: 0.82
    ❌ REJECT - Model NOT registered

# ALL conditions must pass
if accuracy >= 0.75 AND f1_score >= 0.70 AND roc_auc >= 0.80:
    ✅ PASS - Proceed to Stage 2
```

**Implementation in Code:**

```python
# File: pipelines/training_pipeline.py (Lines 290-340)

def create_condition_step(self, step_eval, step_register, evaluation_report):
    """Create conditional step for model approval"""
    
    # Get thresholds from config
    min_accuracy = self.config['evaluation']['approval_thresholds']['min_accuracy']
    min_f1 = self.config['evaluation']['approval_thresholds']['min_f1_score']
    min_roc_auc = self.config['evaluation']['approval_thresholds']['min_roc_auc']
    
    logger.info(f"Quality Gates: Accuracy >= {min_accuracy}, F1 >= {min_f1}, ROC-AUC >= {min_roc_auc}")
    
    # THREE CONDITIONS (ALL must pass)
    cond_accuracy = ConditionGreaterThanOrEqualTo(
        left=JsonGet(step=step_eval, property_file=evaluation_report, json_path='metrics.accuracy'),
        right=min_accuracy
    )
    
    cond_f1 = ConditionGreaterThanOrEqualTo(
        left=JsonGet(step=step_eval, property_file=evaluation_report, json_path='metrics.f1_score'),
        right=min_f1
    )
    
    cond_roc_auc = ConditionGreaterThanOrEqualTo(
        left=JsonGet(step=step_eval, property_file=evaluation_report, json_path='metrics.roc_auc'),
        right=min_roc_auc
    )
    
    # ConditionStep with AND logic (all conditions must be True)
    step_cond = ConditionStep(
        name="CheckModelQuality",
        conditions=[cond_accuracy, cond_f1, cond_roc_auc],  # ALL required
        if_steps=[step_register],  # Only register if ALL pass
        else_steps=[]  # NO registration if ANY fails
    )
    
    return step_cond
```

**What Happens When Quality Gates Fail:**

```
Pipeline Execution Flow:

Training Step → Evaluation Step → Conditional Step
                                        │
                        ┌───────────────┴───────────────┐
                        │                               │
                  ALL 3 pass?                      ANY fail?
                        │                               │
                       YES                             NO
                        │                               │
                        ▼                               ▼
              Register Model Step                  STOP HERE
              (goes to Stage 2)                   (Model discarded)
                                                   (CloudWatch log)
                                                   (SNS alert sent)
```

---

### Stage 2: Manual Approval 👨‍💼 (Environment-Dependent)

After passing automated quality gates, approval status varies by environment:

#### DEV Environment: Auto-Approved ✅
```yaml
# config/environment_config.yaml - dev section
model_registry:
  approval_status: Approved
```
- **Behavior**: Model immediately available for deployment
- **Use Case**: Rapid experimentation and testing

#### STAGING Environment: Manual Approval Required 🔍
```yaml
# config/environment_config.yaml - staging section
model_registry:
  approval_status: PendingManualApproval
```
- **Behavior**: Model registered but requires human review
- **Approvers**: Data scientists, ML engineers
- **Review Items**:
  - Confusion matrix analysis
  - Feature importance verification
  - Comparison with previous model
  - Business metric validation

#### PRODUCTION Environment: Strict Manual Approval 🚨
```yaml
# config/environment_config.yaml - production section
model_registry:
  approval_status: PendingManualApproval
```
- **Behavior**: Model registered but requires senior review + baseline comparison
- **Approvers**: Senior data scientist + ML lead
- **Review Items**:
  - All staging checks PLUS:
  - Performance vs current production baseline
  - Business impact assessment
  - Compliance verification
  - Stakeholder sign-off

---

## 📊 Complete Approval Matrix

| Environment | Quality Gates | Manual Approval | Baseline Check | Result |
|-------------|---------------|-----------------|----------------|--------|
| **DEV**     | ✅ (70/65/75) | ❌ (Auto)       | ❌             | Fast iteration |
| **STAGING** | ✅ (75/70/80) | ✅ (Manual)     | ❌             | Pre-prod validation |
| **PROD**    | ✅ (78/73/82) | ✅ (Manual)     | ✅ (Required)  | Maximum safety |

---

## 🔍 How to Check Model Approval Status

### 1. Via AWS Console

```
1. Go to: AWS Console → SageMaker → Model Registry
2. Select: diabetes-classification-models-[environment]
3. View: Model packages with status:
   - ✅ Approved: Ready for deployment
   - ⏳ PendingManualApproval: Awaiting review
   - ❌ Rejected: Failed quality gates or manual review
```

### 2. Via AWS CLI

```bash
# List all model packages
aws sagemaker list-model-packages \
  --model-package-group-name diabetes-classification-models-prod \
  --query 'ModelPackageSummaryList[*].[ModelPackageArn,ModelApprovalStatus]' \
  --output table

# Get specific model details
aws sagemaker describe-model-package \
  --model-package-name <MODEL_PACKAGE_ARN>
```

### 3. Via Python Script

```python
import boto3

sagemaker_client = boto3.client('sagemaker')

# List pending approvals
response = sagemaker_client.list_model_packages(
    ModelPackageGroupName='diabetes-classification-models-prod',
    ModelApprovalStatus='PendingManualApproval'
)

for model in response['ModelPackageSummaryList']:
    print(f"Model: {model['ModelPackageArn']}")
    print(f"Status: {model['ModelApprovalStatus']}")
    print(f"Created: {model['CreationTime']}")
```

---

## ✅ How to Manually Approve Models

### Option 1: AWS Console (Recommended)

```
1. Navigate: SageMaker → Model Registry → [model-group]
2. Click: Model package with "PendingManualApproval" status
3. Review: Metrics tab
   - Accuracy: 0.XX
   - F1-Score: 0.XX
   - ROC-AUC: 0.XX
   - Confusion Matrix
4. Review: Model Details tab
   - Training job ARN
   - Dataset location
   - Hyperparameters
5. Click: "Update status" button
6. Select: "Approve" or "Reject"
7. Add: Comment (required for rejection)
8. Confirm: Submit
```

### Option 2: AWS CLI

```bash
# Approve model
aws sagemaker update-model-package \
  --model-package-arn <MODEL_PACKAGE_ARN> \
  --model-approval-status Approved \
  --approval-description "Approved after manual review - meets all criteria"

# Reject model
aws sagemaker update-model-package \
  --model-package-arn <MODEL_PACKAGE_ARN> \
  --model-approval-status Rejected \
  --approval-description "Rejected - F1 score too low for business requirements"
```

### Option 3: Python Script

```python
# File: scripts/approve_model.py (create this)

import boto3
import argparse

def approve_model(model_package_arn, status, comment):
    """Approve or reject a model in Model Registry"""
    client = boto3.client('sagemaker')
    
    response = client.update_model_package(
        ModelPackageArn=model_package_arn,
        ModelApprovalStatus=status,
        ApprovalDescription=comment
    )
    
    print(f"Model {status.lower()}: {model_package_arn}")
    return response

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--arn', required=True, help='Model package ARN')
    parser.add_argument('--status', choices=['Approved', 'Rejected'], required=True)
    parser.add_argument('--comment', required=True, help='Approval/rejection reason')
    
    args = parser.parse_args()
    approve_model(args.arn, args.status, args.comment)
```

**Usage:**
```bash
python scripts/approve_model.py \
  --arn arn:aws:sagemaker:us-east-1:123456789012:model-package/diabetes-classification/1 \
  --status Approved \
  --comment "Excellent performance, ready for production"
```

---

## 🚫 What Gets Rejected and Why

### Automatic Rejection Scenarios

```python
# Scenario 1: Low Accuracy
Trained Model: accuracy=0.72, f1=0.75, roc_auc=0.85
Quality Gate:  accuracy≥0.75, f1≥0.70, roc_auc≥0.80
Result: ❌ REJECTED (accuracy too low)
Reason: Model does not meet minimum accuracy threshold

# Scenario 2: Low F1-Score (bad for class imbalance)
Trained Model: accuracy=0.80, f1=0.65, roc_auc=0.85
Quality Gate:  accuracy≥0.75, f1≥0.70, roc_auc≥0.80
Result: ❌ REJECTED (F1 too low)
Reason: Poor performance on minority class

# Scenario 3: Low ROC-AUC (bad discrimination)
Trained Model: accuracy=0.80, f1=0.75, roc_auc=0.72
Quality Gate:  accuracy≥0.75, f1≥0.70, roc_auc≥0.80
Result: ❌ REJECTED (ROC-AUC too low)
Reason: Model cannot properly distinguish classes

# Scenario 4: Multiple failures
Trained Model: accuracy=0.68, f1=0.62, roc_auc=0.70
Quality Gate:  accuracy≥0.75, f1≥0.70, roc_auc≥0.80
Result: ❌ REJECTED (all metrics fail)
Reason: Model quality far below acceptable standards
```

### Manual Rejection Scenarios

Even if a model passes automated gates, humans can reject for:

1. **Business Reasons**:
   - Cost per false positive too high
   - Regulatory compliance issues
   - Stakeholder concerns

2. **Technical Reasons**:
   - Model complexity not justified by performance gain
   - Training data quality issues discovered
   - Feature drift detected

3. **Operational Reasons**:
   - Inference latency too high
   - Model size too large for deployment
   - Resource requirements exceed budget

---

## 📈 Baseline Comparison (Production Only)

For production deployments, models are compared against current baseline:

```python
# File: src/evaluation/evaluate.py (add this function)

def compare_with_baseline(new_metrics, environment='production'):
    """Compare new model with current production model"""
    
    if environment != 'production':
        return True  # Skip baseline check for dev/staging
    
    # Get current production model metrics
    client = boto3.client('sagemaker')
    
    # Fetch current approved model
    response = client.list_model_packages(
        ModelPackageGroupName='diabetes-classification-models-prod',
        ModelApprovalStatus='Approved',
        SortBy='CreationTime',
        SortOrder='Descending',
        MaxResults=1
    )
    
    if not response['ModelPackageSummaryList']:
        return True  # No baseline, approve new model
    
    current_model_arn = response['ModelPackageSummaryList'][0]['ModelPackageArn']
    
    # Get baseline metrics (from model metadata)
    baseline_metrics = get_model_metrics(current_model_arn)
    
    # Compare metrics
    improvements = {
        'accuracy': new_metrics['accuracy'] - baseline_metrics['accuracy'],
        'f1_score': new_metrics['f1_score'] - baseline_metrics['f1_score'],
        'roc_auc': new_metrics['roc_auc'] - baseline_metrics['roc_auc']
    }
    
    # Require improvement in at least 2 out of 3 metrics
    improved_count = sum(1 for v in improvements.values() if v > 0)
    
    if improved_count >= 2:
        logger.info(f"✅ New model improves {improved_count}/3 metrics over baseline")
        return True
    else:
        logger.warning(f"❌ New model only improves {improved_count}/3 metrics")
        return False
```

---

## 🔔 Notifications & Alerts

Configure SNS topics to notify team members:

```yaml
# config/environment_config.yaml - production

alerts:
  enabled: true
  sns_topic_arn: "arn:aws:sns:us-east-1:ACCOUNT_ID:mlops-prod-alerts"
  
  notifications:
    - event: model_registered
      message: "New model pending approval: {model_arn}"
      recipients: ["ml-team@company.com"]
    
    - event: quality_gate_failed
      message: "Model training failed quality gates: {metrics}"
      recipients: ["ml-ops@company.com"]
    
    - event: model_approved
      message: "Model approved for production: {model_arn}"
      recipients: ["stakeholders@company.com"]
```

---

## 🎓 Best Practices

### 1. Always Review Before Production
- Never blindly approve models in staging/production
- Check confusion matrix for class-specific performance
- Validate feature importance aligns with domain knowledge

### 2. Document Approval Decisions
```
Good approval comment:
"Approved - Accuracy improved 3% over baseline, F1 score stable, 
validated with holdout test set, stakeholder approval received"

Bad approval comment:
"looks good"
```

### 3. Maintain Approval History
- SageMaker Model Registry tracks all status changes
- Use CloudTrail for audit logs
- Implement approval workflow with ticketing system (JIRA, ServiceNow)

### 4. Set Up Alerts
```python
# When quality gates fail, send alert
if not all_conditions_pass:
    sns_client.publish(
        TopicArn='arn:aws:sns:...:mlops-alerts',
        Subject='Model Quality Gate Failure',
        Message=f'Model failed: accuracy={accuracy}, f1={f1}, roc_auc={roc_auc}'
    )
```

---

## 📊 Example Approval Workflow

### Successful Approval Flow

```
1. Train Model
   ├─ Hyperparameters: max_depth=6, eta=0.1, num_round=100
   └─ Training data: s3://bucket/data/train.csv

2. Evaluate Model
   ├─ Accuracy: 0.82 ✅ (>= 0.78)
   ├─ F1-Score: 0.79 ✅ (>= 0.73)
   └─ ROC-AUC: 0.88 ✅ (>= 0.82)

3. Automated Quality Gates
   └─ PASSED ✅ (all 3 metrics above threshold)

4. Model Registration
   ├─ Registered to: diabetes-classification-models-prod
   └─ Status: PendingManualApproval

5. Manual Review (Human)
   ├─ Reviewed by: jane.doe@company.com
   ├─ Baseline comparison: +2% accuracy improvement
   ├─ Feature importance: Validated
   └─ Decision: APPROVED ✅

6. Model Deployment
   ├─ Deployment: Canary (10% → 50% → 100%)
   └─ Endpoint: diabetes-classifier-prod

7. Monitoring
   └─ Data drift monitoring: Enabled
```

### Failed Approval Flow

```
1. Train Model
   └─ [Same as above]

2. Evaluate Model
   ├─ Accuracy: 0.74 ❌ (< 0.78)
   ├─ F1-Score: 0.71 ❌ (< 0.73)
   └─ ROC-AUC: 0.79 ❌ (< 0.82)

3. Automated Quality Gates
   └─ FAILED ❌ (all 3 metrics below threshold)

4. Pipeline Stops
   ├─ Model NOT registered
   ├─ CloudWatch log: "Quality gates failed"
   └─ SNS alert sent to ml-ops@company.com

5. Action Required
   ├─ Review hyperparameters
   ├─ Check data quality
   ├─ Investigate feature engineering
   └─ Retrain with adjustments
```

---

## 🔒 Security & Compliance

### Audit Trail
Every approval action is logged:
- **Who**: IAM user/role that approved
- **When**: Timestamp of approval
- **Why**: Approval comment
- **What**: Model package ARN and metrics

### Access Control
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sagemaker:DescribeModelPackage",
        "sagemaker:ListModelPackages"
      ],
      "Resource": "*",
      "Principal": {
        "AWS": "arn:aws:iam::ACCOUNT:role/DataScientist"
      }
    },
    {
      "Effect": "Allow",
      "Action": "sagemaker:UpdateModelPackage",
      "Resource": "arn:aws:sagemaker:*:*:model-package/*",
      "Condition": {
        "StringEquals": {
          "aws:PrincipalTag/Team": "MLOps"
        }
      }
    }
  ]
}
```

---

## 📞 FAQ

**Q: Can I lower the quality gate thresholds?**
A: Yes, edit `config/environment_config.yaml` → `evaluation.approval_thresholds`. Restart pipeline.

**Q: What if emergency deployment is needed?**
A: Use emergency override (requires senior approval):
```bash
aws sagemaker update-model-package \
  --model-package-arn <ARN> \
  --model-approval-status Approved \
  --approval-description "EMERGENCY OVERRIDE - Ticket #12345"
```

**Q: How long do approvals typically take?**
- DEV: Instant (auto-approved)
- STAGING: 30 minutes - 2 hours
- PRODUCTION: 4-24 hours (requires stakeholder alignment)

**Q: Can I automate production approvals?**
A: Not recommended. Manual review prevents costly mistakes. If absolutely needed, implement strict baseline comparison + automated tests.

---

**Summary**: Models are **NOT** automatically registered. They must pass ALL quality gates AND receive manual approval (in staging/prod). This 2-stage process ensures only high-quality models reach production.
