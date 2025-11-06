# MLOps Pipeline Complete Mind Maps

Generated: 2025-11-06

**Contents:**
1. Training Pipeline Mind Map
2. Deployment Pipeline Mind Map
3. Monitoring System Mind Map
4. Evaluation Framework Mind Map
5. Data Processing Mind Map
6. Complete End-to-End Flow

---

# 1. TRAINING PIPELINE MIND MAP

```text
🎯 DIABETES CLASSIFICATION TRAINING PIPELINE - END-TO-END FLOW
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│                         ENTRY POINT: main()                                 │
│                         pipelines/training_pipeline.py                      │
└────────────────────────────┬────────────────────────────────────────────────┘
                             │
                             ▼
            ┌────────────────────────────────────────┐
            │  1. Parse Command Line Arguments       │
            │  --environment (dev/staging/prod)      │
            │  --config (path to config.yaml)        │
            │  --execute (run pipeline or just def)  │
            └────────────────┬───────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────────────────┐
│               2. DiabetesPipeline.__init__()                               │
│               Initialize Pipeline Configuration                            │
├────────────────────────────────────────────────────────────────────────────┤
│  LOADS:                                                                    │
│  ├─ config/config.yaml (base configuration)                                │
│  └─ config/environment_config.yaml (env-specific overrides)                │
│                                                                            │
│  INITIALIZES:                                                              │
│  ├─ self.config (merged configuration)                                     │
│  ├─ self.sagemaker_session (AWS SDK session)                               │
│  ├─ self.role (SageMaker execution role ARN)                               │
│  ├─ self.bucket (S3 bucket name)                                           │
│  └─ self.region (AWS region)                                               │
│                                                                            │
│  WHY: Sets up AWS connectivity and loads all hyperparameters               │
└────────────────────────────┬───────────────────────────────────────────────┘
                             │
                             ▼
            ┌────────────────────────────────────────┐
            │  3. create_pipeline()                  │
            │  Orchestrates all pipeline steps       │
            └────────────────┬───────────────────────┘
                             │
                ┌────────────┴────────────┬─────────────────┬──────────────┐
                ▼                         ▼                 ▼              ▼
    ┌─────────────────────┐  ┌──────────────────┐  ┌────────────┐  ┌────────────┐
    │ create_pipeline_    │  │ create_          │  │ create_    │  │ create_    │
    │ parameters()        │  │ preprocessing_   │  │ training_  │  │ evaluation_│
    │                     │  │ step()           │  │ step()     │  │ step()     │
    └─────────────────────┘  └──────────────────┘  └────────────┘  └────────────┘
                                                           │
                            ┌──────────────────────────────┴─────────────────┐
                            ▼                                                ▼
                  ┌──────────────────────┐                      ┌────────────────────┐
                  │ create_experiment_   │                      │ create_model_      │
                  │ tracking_step()      │                      │ registration_step()│
                  └──────────────────────┘                      └────────────────────┘
                                                                         │
                                                            ┌────────────┴────────────┐
                                                            ▼                         ▼
                                                ┌──────────────────────┐   ┌─────────────────┐
                                                │ create_condition_    │   │ Pipeline()      │
                                                │ step()               │   │ Assembly        │
                                                └──────────────────────┘   └─────────────────┘


════════════════════════════════════════════════════════════════════════════════════════════
                              DETAILED STEP-BY-STEP BREAKDOWN
════════════════════════════════════════════════════════════════════════════════════════════


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  STEP 1: create_pipeline_parameters()                                        ┃
┃  Lines: 86-123                                                                ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  PURPOSE: Define configurable pipeline parameters                            ┃
┃                                                                               ┃
┃  CREATES:                                                                     ┃
┃  ├─ processing_instance_type: ParameterString (ml.m5.xlarge)                 ┃
┃  ├─ training_instance_type: ParameterString (ml.m5.xlarge)                   ┃
┃  ├─ model_approval_status: ParameterString (PendingManualApproval)           ┃
┃  ├─ input_data: ParameterString (s3://bucket/data/raw/diabetes.csv)          ┃
┃  ├─ max_depth: ParameterInteger (5)                                          ┃
┃  ├─ eta: ParameterFloat (0.2)                                                ┃
┃  └─ num_round: ParameterInteger (100)                                        ┃
┃                                                                               ┃
┃  WHY NEEDED:                                                                  ┃
┃  ✓ Allows pipeline re-execution with different parameters                    ┃
┃  ✓ No code changes needed to tune hyperparameters                            ┃
┃  ✓ Environment-specific configurations (dev vs prod)                         ┃
┃                                                                               ┃
┃  RETURNS: Dictionary of SageMaker pipeline parameters                        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  STEP 2: create_preprocessing_step()                                         ┃
┃  Lines: 125-175                                                               ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  PURPOSE: Data preparation and feature engineering                           ┃
┃                                                                               ┃
┃  ARCHITECTURE:                                                                ┃
┃  ┌────────────────────────────────────────────────────────────────┐          ┃
┃  │ SKLearnProcessor                                               │          ┃
┃  │ ├─ Framework: sklearn 1.0-1                                   │          ┃
┃  │ ├─ Instance: ml.m5.xlarge (from parameters)                   │          ┃
┃  │ ├─ Script: src/processing/preprocessing.py                    │          ┃
┃  │ └─ Job Name: diabetes-preprocessing-YYYY-MM-DD-HH-MM-SS       │          ┃
┃  └────────────────────────────────────────────────────────────────┘          ┃
┃                                                                               ┃
┃  INPUT:                                                                       ┃
┃  └─ s3://bucket/data/raw/diabetes.csv                                        ┃
┃     → Mounted at: /opt/ml/processing/input                                   ┃
┃                                                                               ┃
┃  OUTPUTS (4 channels):                                                        ┃
┃  ├─ train: /opt/ml/processing/output/train → s3://.../data/train/            ┃
┃  ├─ validation: /opt/ml/processing/output/validation → s3://.../validation/  ┃
┃  ├─ test: /opt/ml/processing/output/test → s3://.../data/test/               ┃
┃  └─ model: /opt/ml/processing/output/model → s3://.../preprocessing/model/   ┃
┃            (Contains: scaler.pkl, metadata.json)                              ┃
┃                                                                               ┃
┃  WHAT HAPPENS INSIDE preprocessing.py:                                       ┃
┃  1. Load diabetes.csv                                                         ┃
┃  2. Handle missing values (median imputation)                                ┃
┃  3. Train/Val/Test split (70/15/15) - STRATIFIED                            ┃
┃  4. Fit StandardScaler on training data ONLY                                 ┃
┃  5. Transform all splits with fitted scaler                                  ┃
┃  6. Save: train.csv, validation.csv, test.csv, scaler.pkl                   ┃
┃                                                                               ┃
┃  WHY NEEDED:                                                                  ┃
┃  ✓ Clean data separation (no data leakage)                                   ┃
┃  ✓ Feature scaling for XGBoost                                               ┃
┃  ✓ Reproducible preprocessing (saved scaler for inference)                   ┃
┃                                                                               ┃
┃  RETURNS: ProcessingStep object (step_process)                               ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  STEP 3: create_training_step()                                              ┃
┃  Lines: 177-217                                                               ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  PURPOSE: Train XGBoost binary classification model                          ┃
┃                                                                               ┃
┃  DEPENDS ON: step_process (preprocessing must complete first)                ┃
┃                                                                               ┃
┃  ARCHITECTURE:                                                                ┃
┃  ┌────────────────────────────────────────────────────────────────┐          ┃
┃  │ XGBoost Estimator                                              │          ┃
┃  │ ├─ Algorithm: AWS SageMaker Built-in XGBoost 1.5-1            │          ┃
┃  │ ├─ Container: 763104351884.dkr.ecr.us-east-1.amazonaws.com/   │          ┃
┃  │ │             xgboost-training:1.5-1                           │          ┃
┃  │ ├─ Entry Point: src/training/train.py (CUSTOM script)         │          ┃
┃  │ ├─ Instance: ml.m5.xlarge (from parameters)                   │          ┃
┃  │ ├─ Job Name: diabetes-training-YYYY-MM-DD-HH-MM-SS            │          ┃
┃  │ └─ Output: s3://.../models/                                   │          ┃
┃  └────────────────────────────────────────────────────────────────┘          ┃
┃                                                                               ┃
┃  HYPERPARAMETERS (passed to container):                                      ┃
┃  ├─ max_depth: 5 (tree depth)                                                ┃
┃  ├─ eta: 0.2 (learning rate)                                                 ┃
┃  ├─ num_round: 100 (number of boosting rounds)                               ┃
┃  ├─ objective: binary:logistic                                               ┃
┃  └─ eval_metric: auc                                                         ┃
┃                                                                               ┃
┃  INPUTS (2 channels - CHAINED from preprocessing):                           ┃
┃  ├─ train: step_process.properties.ProcessingOutputConfig                    ┃
┃  │          .Outputs['train'].S3Output.S3Uri                                 ┃
┃  │          ↓                                                                ┃
┃  │          Dynamically resolves to: s3://.../data/train/train.csv           ┃
┃  │          Mounted at: /opt/ml/input/data/train/                            ┃
┃  │                                                                            ┃
┃  └─ validation: step_process.properties.ProcessingOutputConfig               ┃
┃               .Outputs['validation'].S3Output.S3Uri                          ┃
┃               ↓                                                               ┃
┃               Dynamically resolves to: s3://.../data/validation/validation.csv┃
┃               Mounted at: /opt/ml/input/data/validation/                     ┃
┃                                                                               ┃
┃  WHAT HAPPENS INSIDE train.py:                                               ┃
┃  1. Read train.csv and validation.csv (from mounted paths)                   ┃
┃  2. Create XGBoost DMatrix objects                                           ┃
┃  3. Train with xgb.train():                                                  ┃
┃     - Boosting for num_round iterations                                      ┃
┃     - Early stopping if validation AUC doesn't improve (10 rounds)           ┃
┃  4. Save model: /opt/ml/model/xgboost-model                                  ┃
┃  5. Save metadata: feature_importance.json, model_metadata.json              ┃
┃  6. Log experiment to SageMaker Experiments (hyperparams + metrics)          ┃
┃                                                                               ┃
┃  OUTPUT:                                                                      ┃
┃  └─ model.tar.gz → s3://.../models/diabetes-training-*/output/               ┃
┃     Contains: xgboost-model, feature_importance.json, metadata.json          ┃
┃                                                                               ┃
┃  WHY CHAINING WORKS:                                                          ┃
┃  ✓ SageMaker resolves step_process.properties at RUNTIME                     ┃
┃  ✓ Training waits for preprocessing to complete                              ┃
┃  ✓ No hardcoded S3 paths (dynamic pipeline)                                  ┃
┃                                                                               ┃
┃  RETURNS: TrainingStep object (step_train)                                   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  STEP 4: create_evaluation_step()                                            ┃
┃  Lines: 219-261                                                               ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  PURPOSE: Evaluate trained model on held-out test set                        ┃
┃                                                                               ┃
┃  DEPENDS ON: step_train (training), step_process (test data)                 ┃
┃                                                                               ┃
┃  ARCHITECTURE:                                                                ┃
┃  ┌────────────────────────────────────────────────────────────────┐          ┃
┃  │ SKLearnProcessor                                               │          ┃
┃  │ ├─ Script: src/evaluation/evaluate.py                         │          ┃
┃  │ ├─ Instance: ml.m5.xlarge                                     │          ┃
┃  │ └─ Job Name: diabetes-evaluation-YYYY-MM-DD-HH-MM-SS          │          ┃
┃  └────────────────────────────────────────────────────────────────┘          ┃
┃                                                                               ┃
┃  INPUTS (2 channels - CHAINED from previous steps):                          ┃
┃  ├─ Model: step_train.properties.ModelArtifacts.S3ModelArtifacts             ┃
┃  │         ↓                                                                 ┃
┃  │         s3://.../models/diabetes-training-*/output/model.tar.gz           ┃
┃  │         Mounted at: /opt/ml/processing/model/                             ┃
┃  │                                                                            ┃
┃  └─ Test Data: step_process.properties.ProcessingOutputConfig                ┃
┃               .Outputs['test'].S3Output.S3Uri                                ┃
┃               ↓                                                               ┃
┃               s3://.../data/test/test.csv                                    ┃
┃               Mounted at: /opt/ml/processing/test/                           ┃
┃                                                                               ┃
┃  WHAT HAPPENS INSIDE evaluate.py:                                            ┃
┃  1. Load trained model from /opt/ml/processing/model/xgboost-model           ┃
┃  2. Load test data from /opt/ml/processing/test/test.csv                     ┃
┃  3. Generate predictions                                                     ┃
┃  4. Calculate metrics:                                                       ┃
┃     - Accuracy, Precision, Recall, F1-score                                  ┃
┃     - ROC-AUC, Confusion Matrix                                              ┃
┃  5. Save evaluation_results.json:                                            ┃
┃     {                                                                         ┃
┃       "metrics": {                                                            ┃
┃         "accuracy": 0.85,                                                     ┃
┃         "f1_score": 0.82,                                                     ┃
┃         "roc_auc": 0.88,                                                      ┃
┃         ...                                                                   ┃
┃       }                                                                       ┃
┃     }                                                                         ┃
┃                                                                               ┃
┃  OUTPUT:                                                                      ┃
┃  └─ evaluation_results.json → s3://.../evaluation/                           ┃
┃                                                                               ┃
┃  PropertyFile (CRITICAL for conditional step):                               ┃
┃  ├─ Name: 'EvaluationReport'                                                 ┃
┃  ├─ Output: 'evaluation'                                                     ┃
┃  └─ Path: 'evaluation_results.json'                                          ┃
┃     → Allows pipeline to READ metrics and make decisions                     ┃
┃                                                                               ┃
┃  WHY NEEDED:                                                                  ┃
┃  ✓ Unbiased performance (test set never seen during training)                ┃
┃  ✓ Quality gates (only good models get registered)                           ┃
┃  ✓ Metrics available for conditional logic                                   ┃
┃                                                                               ┃
┃  RETURNS: (step_eval, evaluation_report)                                     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  STEP 5: create_experiment_tracking_step()                                   ┃
┃  Lines: 263-294                                                               ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  PURPOSE: Log experiment metadata to SageMaker Experiments                   ┃
┃                                                                               ┃
┃  DEPENDS ON: step_train (training job metadata), step_eval (metrics)         ┃
┃                                                                               ┃
┃  ARCHITECTURE:                                                                ┃
┃  ┌────────────────────────────────────────────────────────────────┐          ┃
┃  │ SKLearnProcessor                                               │          ┃
┃  │ ├─ Script: src/monitoring/track_experiment.py                 │          ┃
┃  │ ├─ Instance: ml.t3.medium (small, cheap)                      │          ┃
┃  │ └─ Job Name: diabetes-experiment-tracking-*                   │          ┃
┃  └────────────────────────────────────────────────────────────────┘          ┃
┃                                                                               ┃
┃  JOB ARGUMENTS (passed to script):                                           ┃
┃  ├─ --training-job-name: step_train.properties.TrainingJobName               ┃
┃  ├─ --model-artifact-uri: step_train.properties.ModelArtifacts...            ┃
┃  ├─ --evaluation-results: /opt/ml/processing/evaluation/evaluation_results.json┃
┃  └─ --experiment-name: 'diabetes-classification-experiments'                 ┃
┃                                                                               ┃
┃  WHAT HAPPENS INSIDE track_experiment.py:                                    ┃
┃  1. Load evaluation results                                                  ┃
┃  2. Create/update SageMaker Experiment                                       ┃
┃  3. Create Trial Run with training job name                                  ┃
┃  4. Log:                                                                     ┃
┃     - All hyperparameters (max_depth, eta, etc.)                             ┃
┃     - All evaluation metrics (accuracy, F1, ROC-AUC)                         ┃
┃     - Model artifact S3 URI                                                  ┃
┃     - Training job ARN                                                       ┃
┃                                                                               ┃
┃  WHY NEEDED:                                                                  ┃
┃  ✓ Track ALL experiments in one place                                        ┃
┃  ✓ Compare models across runs                                                ┃
┃  ✓ Reproducibility (know which hyperparams → which metrics)                  ┃
┃  ✓ Audit trail for compliance                                                ┃
┃                                                                               ┃
┃  RETURNS: ProcessingStep object (step_experiment)                            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  STEP 6: create_model_registration_step()                                    ┃
┃  Lines: 296-319                                                               ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  PURPOSE: Register model in SageMaker Model Registry                         ┃
┃                                                                               ┃
┃  DEPENDS ON: step_train (model), step_eval (metrics)                         ┃
┃                                                                               ┃
┃  ARCHITECTURE:                                                                ┃
┃  ┌────────────────────────────────────────────────────────────────┐          ┃
┃  │ RegisterModel Step                                             │          ┃
┃  │ ├─ Model Package Group: diabetes-classification-models        │          ┃
┃  │ ├─ Model Data: step_train.properties.ModelArtifacts.*         │          ┃
┃  │ ├─ Approval Status: parameters['model_approval_status']       │          ┃
┃  │ │                    (Approved / PendingManualApproval)        │          ┃
┃  │ └─ Model Metrics: evaluation_results.json                     │          ┃
┃  └────────────────────────────────────────────────────────────────┘          ┃
┃                                                                               ┃
┃  MODEL METADATA:                                                              ┃
┃  ├─ content_types: ['text/csv'] (what input format model accepts)            ┃
┃  ├─ response_types: ['application/json'] (what output format)                ┃
┃  ├─ inference_instances: ['ml.t2.medium', 'ml.m5.large']                     ┃
┃  ├─ transform_instances: ['ml.m5.large'] (for batch transform)               ┃
┃  └─ model_metrics: Links to evaluation_results.json                          ┃
┃                                                                               ┃
┃  WHAT HAPPENS:                                                                ┃
┃  1. Create Model Package in SageMaker Model Registry                         ┃
┃  2. Version is auto-incremented (v1, v2, v3...)                              ┃
┃  3. Attach evaluation metrics to model version                               ┃
┃  4. Set approval status (Approved/Pending/Rejected)                          ┃
┃  5. Enable deployment from registry                                          ┃
┃                                                                               ┃
┃  WHY NEEDED:                                                                  ┃
┃  ✓ Model versioning (track all trained models)                               ┃
┃  ✓ Approval workflow (QA before production)                                  ┃
┃  ✓ Lineage tracking (data → code → model → metrics)                          ┃
┃  ✓ Easy deployment (reference by version, not S3 path)                       ┃
┃                                                                               ┃
┃  RETURNS: RegisterModel object (step_register)                               ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  STEP 7: create_condition_step()                                             ┃
┃  Lines: 321-384                                                               ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  PURPOSE: Quality gates - only register models that meet thresholds          ┃
┃                                                                               ┃
┃  DEPENDS ON: step_eval (evaluation_report), step_register                    ┃
┃                                                                               ┃
┃  QUALITY GATE LOGIC (AND logic - ALL must pass):                             ┃
┃  ┌────────────────────────────────────────────────────────────────┐          ┃
┃  │ Condition 1: Accuracy >= 0.75                                  │          ┃
┃  │ ConditionGreaterThanOrEqualTo(                                 │          ┃
┃  │   JsonGet(step_eval, evaluation_report,                        │          ┃
┃  │           'metrics.accuracy'),                                 │          ┃
┃  │   0.75                                                          │          ┃
┃  │ )                                                               │          ┃
┃  └────────────────────────────────────────────────────────────────┘          ┃
┃                           AND                                                 ┃
┃  ┌────────────────────────────────────────────────────────────────┐          ┃
┃  │ Condition 2: F1-Score >= 0.70                                  │          ┃
┃  │ ConditionGreaterThanOrEqualTo(                                 │          ┃
┃  │   JsonGet(step_eval, evaluation_report,                        │          ┃
┃  │           'metrics.f1_score'),                                 │          ┃
┃  │   0.70                                                          │          ┃
┃  │ )                                                               │          ┃
┃  └────────────────────────────────────────────────────────────────┘          ┃
┃                           AND                                                 ┃
┃  ┌────────────────────────────────────────────────────────────────┐          ┃
┃  │ Condition 3: ROC-AUC >= 0.80                                   │          ┃
┃  │ ConditionGreaterThanOrEqualTo(                                 │          ┃
┃  │   JsonGet(step_eval, evaluation_report,                        │          ┃
┃  │           'metrics.roc_auc'),                                  │          ┃
┃  │   0.80                                                          │          ┃
┃  │ )                                                               │          ┃
┃  └────────────────────────────────────────────────────────────────┘          ┃
┃                                                                               ┃
┃  CONDITIONAL STEP BEHAVIOR:                                                   ┃
┃  ├─ IF all 3 conditions TRUE:                                                ┃
┃  │  └─ Execute: step_register (register model)                               ┃
┃  │                                                                            ┃
┃  └─ ELSE (any condition FALSE):                                              ┃
┃     └─ Execute: [] (do nothing, skip registration)                           ┃
┃                                                                               ┃
┃  HOW JsonGet WORKS:                                                           ┃
┃  ├─ Reads evaluation_results.json from step_eval                             ┃
┃  ├─ Parses JSON path: 'metrics.accuracy' → 0.85                              ┃
┃  └─ Compares with threshold: 0.85 >= 0.75 → TRUE                             ┃
┃                                                                               ┃
┃  WHY NEEDED:                                                                  ┃
┃  ✓ Prevent bad models from reaching production                               ┃
┃  ✓ Automated quality control                                                 ┃
┃  ✓ Consistent standards across all models                                    ┃
┃  ✓ No manual intervention needed for good models                             ┃
┃                                                                               ┃
┃  RETURNS: ConditionStep object (step_cond)                                   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  STEP 8: create_pipeline() - ASSEMBLY                                        ┃
┃  Lines: 386-422                                                               ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  PURPOSE: Assemble all steps into executable pipeline                        ┃
┃                                                                               ┃
┃  EXECUTION ORDER:                                                             ┃
┃  ┌────────────────────────────────────────────────────────────────┐          ┃
┃  │ Pipeline(                                                      │          ┃
┃  │   name='diabetes-classification-pipeline',                    │          ┃
┃  │   parameters=[...],  # 7 parameters defined earlier           │          ┃
┃  │   steps=[                                                      │          ┃
┃  │     step_process,      # 1. Preprocessing (no dependencies)   │          ┃
┃  │     step_train,        # 2. Training (waits for step_process) │          ┃
┃  │     step_eval,         # 3. Evaluation (waits for step_train) │          ┃
┃  │     step_experiment,   # 4. Experiment tracking (after eval)  │          ┃
┃  │     step_cond          # 5. Conditional registration (after eval)│        ┃
┃  │   ]                                                            │          ┃
┃  │ )                                                              │          ┃
┃  └────────────────────────────────────────────────────────────────┘          ┃
┃                                                                               ┃
┃  DEPENDENCY GRAPH (SageMaker auto-detects):                                  ┃
┃  ```                                                                          ┃
┃  step_process                                                                 ┃
┃       │                                                                       ┃
┃       ├─────────────┬─────────────┐                                          ┃
┃       ▼             ▼             ▼                                          ┃
┃  step_train    (uses train)  (uses test)                                     ┃
┃       │                           │                                          ┃
┃       ├───────────┬───────────────┤                                          ┃
┃       ▼           ▼               ▼                                          ┃
┃  step_eval   step_experiment  (model)                                        ┃
┃       │           │                                                          ┃
┃       └───────┬───┘                                                          ┃
┃               ▼                                                               ┃
┃          step_cond                                                            ┃
┃               │                                                               ┃
┃               ├─ IF metrics OK → step_register                               ┃
┃               └─ ELSE → skip                                                 ┃
┃  ```                                                                          ┃
┃                                                                               ┃
┃  RETURNS: Pipeline object (ready to execute)                                 ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  STEP 9: execute_pipeline()                                                  ┃
┃  Lines: 424-441                                                               ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  PURPOSE: Create/update pipeline in SageMaker and execute                    ┃
┃                                                                               ┃
┃  EXECUTION:                                                                   ┃
┃  1. pipeline.upsert(role_arn=self.role)                                      ┃
┃     ├─ Creates pipeline if doesn't exist                                     ┃
┃     └─ Updates pipeline if already exists                                    ┃
┃                                                                               ┃
┃  2. execution = pipeline.start()                                             ┃
┃     ├─ Submits pipeline execution to SageMaker                               ┃
┃     ├─ Returns execution ARN                                                 ┃
┃     └─ Execution runs asynchronously                                         ┃
┃                                                                               ┃
┃  WHAT HAPPENS IN AWS:                                                         ┃
┃  ├─ SageMaker creates execution plan                                         ┃
┃  ├─ Launches EC2 instances for each step                                     ┃
┃  ├─ Mounts data from S3 to containers                                        ┃
┃  ├─ Runs scripts inside containers                                           ┃
┃  ├─ Uploads outputs back to S3                                               ┃
┃  └─ Terminates instances when done                                           ┃
┃                                                                               ┃
┃  MONITORING:                                                                  ┃
┃  └─ SageMaker Console → Pipelines → View execution graph                     ┃
┃                                                                               ┃
┃  RETURNS: Execution object (with ARN for tracking)                           ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛


════════════════════════════════════════════════════════════════════════════════════════════
                              KEY CONCEPTS - WHY IT ALL WORKS TOGETHER
════════════════════════════════════════════════════════════════════════════════════════════

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  1. PIPELINE CHAINING (Data Flow Between Steps)                              ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                                               ┃
┃  Instead of hardcoded S3 paths:                                              ┃
┃  ❌ BAD: s3://bucket/data/train/train.csv (brittle, date-specific)           ┃
┃                                                                               ┃
┃  Use step properties:                                                         ┃
┃  ✅ GOOD: step_process.properties.ProcessingOutputConfig                     ┃
┃           .Outputs['train'].S3Output.S3Uri                                   ┃
┃                                                                               ┃
┃  WHY:                                                                         ┃
┃  ├─ Runtime resolution (path created during execution)                       ┃
┃  ├─ Automatic dependency (SageMaker knows step_train needs step_process)     ┃
┃  ├─ No manual S3 path management                                             ┃
┃  └─ Pipeline is reproducible and date-agnostic                               ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  2. PROPERTY FILES (Conditional Logic)                                       ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                                               ┃
┃  evaluation_report = PropertyFile(                                           ┃
┃      name='EvaluationReport',                                                ┃
┃      output_name='evaluation',  # Which ProcessingOutput                     ┃
┃      path='evaluation_results.json'  # File within that output               ┃
┃  )                                                                            ┃
┃                                                                               ┃
┃  This allows:                                                                 ┃
┃  JsonGet(step_eval, evaluation_report, 'metrics.accuracy')                   ┃
┃  ↓                                                                            ┃
┃  SageMaker reads: s3://.../evaluation/evaluation_results.json                ┃
┃  Parses JSON: {"metrics": {"accuracy": 0.85}}                                ┃
┃  Extracts value: 0.85                                                        ┃
┃  Compares: 0.85 >= 0.75 → TRUE                                               ┃
┃                                                                               ┃
┃  WHY NEEDED:                                                                  ┃
┃  ├─ Pipeline makes decisions WITHOUT human intervention                      ┃
┃  ├─ Quality gates enforce standards                                          ┃
┃  └─ Fully automated MLOps workflow                                           ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  3. PARAMETERIZATION (Flexibility)                                           ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                                               ┃
┃  Pipeline can be re-run with different values:                               ┃
┃  ```                                                                          ┃
┃  pipeline.start(                                                             ┃
┃      parameters={                                                             ┃
┃          'MaxDepth': 7,  # Instead of default 5                              ┃
┃          'Eta': 0.1,     # Instead of default 0.2                            ┃
┃          'NumRound': 150 # Instead of default 100                            ┃
┃      }                                                                        ┃
┃  )                                                                            ┃
┃  ```                                                                          ┃
┃                                                                               ┃
┃  WHY:                                                                         ┃
┃  ├─ Hyperparameter tuning without code changes                               ┃
┃  ├─ Environment-specific configs (dev/staging/prod)                          ┃
┃  └─ A/B testing different model versions                                     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  4. SEPARATION OF CONCERNS                                                   ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                                               ┃
┃  ├─ training_pipeline.py: ORCHESTRATION (what steps, in what order)          ┃
┃  ├─ preprocessing.py: DATA LOGIC (how to clean data)                         ┃
┃  ├─ train.py: MODEL LOGIC (how to train XGBoost)                             ┃
┃  ├─ evaluate.py: EVALUATION LOGIC (how to calculate metrics)                 ┃
┃  └─ config.yaml: CONFIGURATION (what hyperparameters to use)                 ┃
┃                                                                               ┃
┃  WHY:                                                                         ┃
┃  ├─ Each script has ONE responsibility                                       ┃
┃  ├─ Easy to test individually                                                ┃
┃  ├─ Easy to modify without breaking others                                   ┃
┃  └─ Reusable components across projects                                      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛


════════════════════════════════════════════════════════════════════════════════════════════
                              EXECUTION TIMELINE (What Actually Happens)
════════════════════════════════════════════════════════════════════════════════════════════

T=0s    │ User runs: python pipelines/training_pipeline.py --execute
        │
T=1s    │ DiabetesPipeline.__init__() loads config
        │
T=2s    │ create_pipeline() assembles all steps
        │
T=3s    │ pipeline.upsert() creates/updates pipeline in AWS
        │
T=5s    │ pipeline.start() submits execution
        │
        ├─────────────────────────────────────────────────────────────────────
        │ STEP 1: PreprocessData
T=10s   │ ├─ SageMaker launches ml.m5.xlarge instance
T=30s   │ ├─ Downloads sklearn:1.0-1 container image
T=60s   │ ├─ Downloads preprocessing.py script
T=65s   │ ├─ Downloads diabetes.csv from S3
T=70s   │ ├─ Runs preprocessing.py
        │ │  ├─ Loads CSV (768 rows)
        │ │  ├─ Splits: 537 train, 115 val, 116 test
        │ │  ├─ Fits StandardScaler
        │ │  └─ Saves 4 outputs
T=300s  │ ├─ Uploads train.csv, validation.csv, test.csv, scaler.pkl to S3
T=320s  │ └─ Terminates instance
        │
        ├─────────────────────────────────────────────────────────────────────
        │ STEP 2: TrainModel (waits for step 1)
T=330s  │ ├─ SageMaker launches ml.m5.xlarge instance
T=350s  │ ├─ Downloads XGBoost:1.5-1 container image
T=380s  │ ├─ Downloads train.py script
T=385s  │ ├─ Downloads train.csv and validation.csv from S3
T=390s  │ ├─ Runs train.py
        │ │  ├─ Creates DMatrix
        │ │  ├─ Trains XGBoost (100 rounds)
        │ │  │  [0] train-auc:0.7234  validation-auc:0.7123
        │ │  │  [10] train-auc:0.8456  validation-auc:0.8234
        │ │  │  ...
        │ │  │  [95] train-auc:0.9234  validation-auc:0.8567
        │ │  │  [96] train-auc:0.9240  validation-auc:0.8565 (early stop)
        │ │  ├─ Saves xgboost-model
        │ │  └─ Logs to SageMaker Experiments
T=700s  │ ├─ Creates model.tar.gz and uploads to S3
T=720s  │ └─ Terminates instance
        │
        ├─────────────────────────────────────────────────────────────────────
        │ STEP 3: EvaluateModel (waits for step 2)
T=730s  │ ├─ SageMaker launches ml.m5.xlarge instance
T=750s  │ ├─ Downloads sklearn:1.0-1 container
T=770s  │ ├─ Downloads evaluate.py script
T=775s  │ ├─ Downloads model.tar.gz and test.csv from S3
T=780s  │ ├─ Runs evaluate.py
        │ │  ├─ Loads model
        │ │  ├─ Makes predictions on test set
        │ │  ├─ Calculates metrics:
        │ │  │  accuracy: 0.8534
        │ │  │  f1_score: 0.8321
        │ │  │  roc_auc: 0.8876
        │ │  └─ Saves evaluation_results.json
T=850s  │ ├─ Uploads evaluation_results.json to S3
T=860s  │ └─ Terminates instance
        │
        ├─────────────────────────────────────────────────────────────────────
        │ STEP 4: TrackExperiment (waits for step 3)
T=870s  │ ├─ Launches ml.t3.medium instance
T=890s  │ ├─ Runs track_experiment.py
        │ │  └─ Logs ALL metadata to SageMaker Experiments
T=920s  │ └─ Terminates instance
        │
        ├─────────────────────────────────────────────────────────────────────
        │ STEP 5: CheckModelQualityThresholds (conditional)
T=930s  │ ├─ SageMaker evaluates conditions:
        │ │  ├─ accuracy: 0.8534 >= 0.75 ✅ PASS
        │ │  ├─ f1_score: 0.8321 >= 0.70 ✅ PASS
        │ │  └─ roc_auc: 0.8876 >= 0.80 ✅ PASS
        │ │
        │ └─ All conditions TRUE → Execute RegisterModel
        │
        ├─────────────────────────────────────────────────────────────────────
        │ STEP 6: RegisterModel (runs because conditions passed)
T=940s  │ ├─ Creates Model Package in SageMaker Model Registry
        │ │  ├─ Package Group: diabetes-classification-models
        │ │  ├─ Version: 1 (auto-incremented)
        │ │  ├─ Model Data: s3://.../models/.../output/model.tar.gz
        │ │  ├─ Metrics: evaluation_results.json
        │ │  └─ Approval Status: PendingManualApproval
T=960s  │ └─ Model registered successfully
        │
T=965s  │ ✅ PIPELINE EXECUTION COMPLETE
        │ Total time: 16 minutes
        │ Total cost: ~$0.50 (with spot instances)


════════════════════════════════════════════════════════════════════════════════════════════
                                      SUMMARY
════════════════════════════════════════════════════════════════════════════════════════════

FUNCTIONS WORK TOGETHER BECAUSE:

1. **Dependency Chaining**: Each step references previous step outputs via `.properties`
2. **Shared Configuration**: All steps read from same config.yaml (consistent hyperparameters)
3. **Standard Interfaces**: All steps use SageMaker conventions (input/output paths)
4. **PropertyFiles**: Enable pipeline to read JSON and make decisions
5. **Parameters**: Allow runtime customization without code changes
6. **Orchestration**: SageMaker Pipeline manages execution order, retries, logging

RESULT: Fully automated ML workflow from raw data → deployed model
```


════════════════════════════════════════════════════════════════════════════════════════════
# 2. DEPLOYMENT PIPELINE MIND MAP
════════════════════════════════════════════════════════════════════════════════════════════

```text
🚀 MODEL DEPLOYMENT - FROM REGISTRY TO PRODUCTION ENDPOINT
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│                    ENTRY POINT: deploy.py                                   │
│                    src/deployment/deploy.py                                 │
└────────────────────────┬────────────────────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────────┐
        │  1. ModelDeployer.__init__()           │
        │  Load configuration & AWS session      │
        └────────────────┬───────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────────────────┐
│               2. get_approved_model()                                      │
│               Fetch Latest Approved Model from Registry                    │
├────────────────────────────────────────────────────────────────────────────┤
│  SEARCHES:                                                                 │
│  ├─ Model Package Group: diabetes-classification-models                   │
│  ├─ Approval Status: "Approved"                                            │
│  └─ Sort By: CreationTime (descending)                                     │
│                                                                            │
│  RETURNS:                                                                  │
│  └─ Model Package ARN                                                      │
│     Example: arn:aws:sagemaker:us-east-1:891807086260:                    │
│              model-package/diabetes-classification-models/1                │
│                                                                            │
│  WHY: Ensures only quality-approved models reach production                │
└────────────────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────────────────┐
│               3. create_model()                                            │
│               Create SageMaker Model Resource                              │
├────────────────────────────────────────────────────────────────────────────┤
│  COMPONENTS:                                                               │
│  ├─ Model Name: diabetes-classifier-{timestamp}                           │
│  ├─ Primary Container:                                                     │
│  │  ├─ Image: XGBoost 1.5-1 container                                     │
│  │  ├─ ModelDataUrl: s3://.../model.tar.gz                                │
│  │  └─ Environment: Custom inference variables                            │
│  ├─ Inference Code: inference.py (custom handlers)                        │
│  │  ├─ model_fn() - Load model & scaler                                   │
│  │  ├─ input_fn() - Deserialize JSON/CSV                                  │
│  │  ├─ predict_fn() - Scale & predict                                     │
│  │  └─ output_fn() - Format response                                      │
│  └─ Execution Role: SageMaker execution role                              │
│                                                                            │
│  WHY: Model resource is reusable across multiple endpoints                │
└────────────────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────────────────┐
│               4. create_endpoint_config()                                  │
│               Define Endpoint Configuration                                │
├────────────────────────────────────────────────────────────────────────────┤
│  PRODUCTION VARIANTS:                                                      │
│  ├─ Variant Name: AllTraffic                                              │
│  ├─ Instance Type: ml.t2.medium (dev) / ml.m5.large (prod)                │
│  ├─ Initial Instance Count: 1                                             │
│  └─ Initial Weight: 1.0 (100% traffic)                                    │
│                                                                            │
│  DATA CAPTURE CONFIG (for monitoring):                                    │
│  ├─ Enable: true                                                          │
│  ├─ Capture: Input & Output                                               │
│  ├─ Sampling: 100%                                                        │
│  └─ S3 Destination: s3://.../monitoring/data-capture/                     │
│                                                                            │
│  WHY: Separates config from endpoint (enables blue/green deployment)      │
└────────────────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────────────────┐
│               5. create_or_update_endpoint()                               │
│               Deploy Real-Time Inference Endpoint                          │
├────────────────────────────────────────────────────────────────────────────┤
│  IF ENDPOINT EXISTS:                                                       │
│  ├─ Update endpoint config (zero-downtime)                                │
│  ├─ Gradual traffic shift (if enabled)                                    │
│  └─ Old instances retired after new ones healthy                          │
│                                                                            │
│  IF NEW ENDPOINT:                                                          │
│  ├─ Create endpoint from scratch                                          │
│  ├─ Wait for "InService" status (5-10 min)                                │
│  └─ Run health checks                                                     │
│                                                                            │
│  WHAT HAPPENS:                                                             │
│  1. AWS provisions EC2 instances                                          │
│  2. Downloads model.tar.gz from S3                                        │
│  3. Loads XGBoost model & inference code                                  │
│  4. Starts HTTPS endpoint                                                 │
│  5. Begins accepting prediction requests                                  │
│                                                                            │
│  ENDPOINT URL:                                                             │
│  └─ https://runtime.sagemaker.us-east-1.amazonaws.com/endpoints/          │
│     diabetes-classifier-prod/invocations                                  │
└────────────────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────────────────┐
│               6. enable_autoscaling()                                      │
│               Configure Auto-Scaling Policy                                │
├────────────────────────────────────────────────────────────────────────────┤
│  TARGET TRACKING SCALING:                                                  │
│  ├─ Metric: InvocationsPerInstance                                        │
│  ├─ Target: 1000 invocations/instance                                     │
│  ├─ Min Capacity: 1 instance                                              │
│  ├─ Max Capacity: 5 instances (dev) / 10 (prod)                           │
│  ├─ Scale-Out Cooldown: 60 seconds                                        │
│  └─ Scale-In Cooldown: 300 seconds                                        │
│                                                                            │
│  HOW IT WORKS:                                                             │
│  ├─ If invocations > 1000/instance → Add instance                         │
│  ├─ If invocations < 1000/instance → Remove instance                      │
│  └─ CloudWatch monitors metrics every 60 seconds                          │
│                                                                            │
│  COST SAVINGS:                                                             │
│  └─ 50-70% savings by scaling down during low traffic                     │
└────────────────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────────────────┐
│               7. add_tags()                                                │
│               Apply Resource Tags for Governance                           │
├────────────────────────────────────────────────────────────────────────────┤
│  TAGS:                                                                     │
│  ├─ Project: DiabetesClassification                                       │
│  ├─ Environment: dev/staging/production                                   │
│  ├─ ManagedBy: MLOps                                                      │
│  ├─ CostCenter: DataScience                                               │
│  ├─ ModelVersion: v1.2.3                                                  │
│  └─ DeployedBy: GitHub Actions / Manual                                   │
│                                                                            │
│  WHY: Cost tracking, access control, compliance auditing                  │
└────────────────────────────────────────────────────────────────────────────┘


════════════════════════════════════════════════════════════════════════════════════════════
                              INFERENCE FLOW (RUNTIME)
════════════════════════════════════════════════════════════════════════════════════════════

CLIENT REQUEST
     │
     ▼
┌────────────────────────────────────────┐
│  POST /invocations                     │
│  Content-Type: text/csv OR             │
│                application/json        │
│  Body: "6,148,72,35,0,33.6,0.627,50"  │
└────────────────┬───────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────────────────────────┐
│               SAGEMAKER ENDPOINT                                           │
│               (Load Balancer → EC2 Instance)                               │
├────────────────────────────────────────────────────────────────────────────┤
│  STEP 1: input_fn(request_body, content_type)                             │
│  ├─ Deserializes CSV/JSON                                                 │
│  ├─ Validates 8 features                                                  │
│  └─ Returns: numpy array [[6, 148, 72, 35, 0, 33.6, 0.627, 50]]          │
│                                                                            │
│  STEP 2: predict_fn(input_data, model)                                    │
│  ├─ Loads scaler.pkl (from model.tar.gz)                                  │
│  ├─ Scales input: (value - mean) / std                                    │
│  ├─ Calls XGBoost model.predict()                                         │
│  └─ Returns: Prediction probabilities [0.2, 0.8]                          │
│                                                                            │
│  STEP 3: output_fn(prediction, accept_type)                               │
│  ├─ Formats as JSON                                                       │
│  └─ Returns: {"prediction": 1, "probability": 0.8, "confidence": "high"}  │
└────────────────────────────────────────────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────┐
│  HTTP 200 OK                           │
│  Content-Type: application/json        │
│  {                                     │
│    "prediction": 1,                    │
│    "probability": 0.8,                 │
│    "confidence": "high"                │
│  }                                     │
└────────────────────────────────────────┘


════════════════════════════════════════════════════════════════════════════════════════════
                              DEPLOYMENT PATTERNS
════════════════════════════════════════════════════════════════════════════════════════════

PATTERN 1: BLUE/GREEN DEPLOYMENT
├─ Create new endpoint config (green)
├─ Update endpoint to use green config
├─ SageMaker routes traffic gradually
├─ If successful → Delete blue config
└─ If failed → Rollback to blue config

PATTERN 2: CANARY DEPLOYMENT
├─ Create production variant: v1 (90% traffic)
├─ Create production variant: v2 (10% traffic)
├─ Monitor v2 metrics for 1 hour
├─ If v2 metrics good → Shift to 100%
└─ If v2 metrics bad → Route back to v1

PATTERN 3: A/B TESTING
├─ Variant A: Current model (50% traffic)
├─ Variant B: New model (50% traffic)
├─ Track business metrics (conversions, costs)
├─ After 1 week → Choose winner
└─ Route 100% traffic to winner
```


════════════════════════════════════════════════════════════════════════════════════════════
# 3. MONITORING SYSTEM MIND MAP
════════════════════════════════════════════════════════════════════════════════════════════

```text
📊 MODEL MONITORING - CONTINUOUS QUALITY & DRIFT DETECTION
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│                    MONITORING ARCHITECTURE                                  │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────────┐
                    │  Production Endpoint    │
                    │  (Real-time inference)  │
                    └───────────┬─────────────┘
                                │
                                │ Data Capture
                                │ (Input & Output)
                                ▼
                    ┌─────────────────────────┐
                    │  S3 Data Capture Bucket │
                    │  /monitoring/data-cap...│
                    └───────────┬─────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
        ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
        │ Data Quality │ │ Model Quality│ │ Drift        │
        │ Monitor      │ │ Monitor      │ │ Detection    │
        └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
               │                │                │
               └────────────────┼────────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │  CloudWatch Alarms      │
                    │  + SNS Notifications    │
                    └─────────────────────────┘


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  COMPONENT 1: Data Quality Monitoring                                        ┃
┃  File: src/monitoring/drift_detection.py                                     ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  PURPOSE: Detect changes in input data distribution                          ┃
┃                                                                               ┃
┃  BASELINE CREATION (One-Time):                                               ┃
┃  1. Load training data → s3://.../data/train/train.csv                       ┃
┃  2. Calculate statistics:                                                    ┃
┃     ├─ Mean, Std Dev for each feature                                        ┃
┃     ├─ Min, Max, Median, Quartiles                                           ┃
┃     └─ Data types, null counts                                               ┃
┃  3. Save baseline → s3://.../monitoring/baseline/                            ┃
┃                                                                               ┃
┃  CONTINUOUS MONITORING (Hourly):                                             ┃
┃  1. Read captured data from endpoint                                         ┃
┃  2. Calculate same statistics                                                ┃
┃  3. Compare with baseline:                                                   ┃
┃     ├─ Feature drift (KL divergence)                                         ┃
┃     ├─ Schema changes (new/missing columns)                                  ┃
┃     └─ Data type changes                                                     ┃
┃  4. Generate violations report                                               ┃
┃  5. Trigger alarm if drift > threshold                                       ┃
┃                                                                               ┃
┃  DRIFT METRICS:                                                               ┃
┃  ├─ KL Divergence > 0.2 → WARNING                                            ┃
┃  ├─ KL Divergence > 0.5 → CRITICAL                                           ┃
┃  └─ Missing features → CRITICAL                                              ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  COMPONENT 2: Model Quality Monitoring                                       ┃
┃  File: src/monitoring/model_monitor.py                                       ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  PURPOSE: Track model performance degradation over time                      ┃
┃                                                                               ┃
┃  REQUIRES:                                                                    ┃
┃  └─ Ground truth labels (delayed feedback from users)                        ┃
┃     Example: Patient diagnosis confirmed weeks later                         ┃
┃                                                                               ┃
┃  MONITORING SCHEDULE:                                                         ┃
┃  ├─ Frequency: Daily (when ground truth available)                           ┃
┃  ├─ Batch size: Last 1000 predictions                                        ┃
┃  └─ Instance: ml.m5.large                                                    ┃
┃                                                                               ┃
┃  CALCULATED METRICS:                                                          ┃
┃  ├─ Accuracy (against ground truth)                                          ┃
┃  ├─ Precision / Recall / F1                                                  ┃
┃  ├─ ROC-AUC                                                                  ┃
┃  ├─ Confusion Matrix                                                         ┃
┃  └─ Business Cost Metric                                                     ┃
┃                                                                               ┃
┃  QUALITY GATES:                                                               ┃
┃  ├─ Accuracy < 0.70 → Retrain recommended                                    ┃
┃  ├─ F1 < 0.65 → Investigate                                                  ┃
┃  └─ ROC-AUC < 0.75 → Critical degradation                                    ┃
┃                                                                               ┃
┃  AUTOMATED ACTIONS:                                                           ┃
┃  1. Send SNS alert to data science team                                      ┃
┃  2. Create Jira ticket (optional)                                            ┃
┃  3. Trigger retraining pipeline (optional)                                   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  COMPONENT 3: Experiment Tracking                                            ┃
┃  File: src/monitoring/experiment_tracker.py                                  ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  PURPOSE: Track all training runs for reproducibility                        ┃
┃                                                                               ┃
┃  SAGEMAKER EXPERIMENTS INTEGRATION:                                           ┃
┃  ├─ Experiment: diabetes-classification-experiments                          ┃
┃  ├─ Trial: training-job-{timestamp}                                          ┃
┃  └─ Run: Hyperparameters + Metrics + Artifacts                               ┃
┃                                                                               ┃
┃  LOGGED INFORMATION:                                                          ┃
┃  1. Hyperparameters:                                                         ┃
┃     ├─ max_depth: 5                                                          ┃
┃     ├─ eta: 0.2                                                              ┃
┃     ├─ num_round: 100                                                        ┃
┃     └─ objective: binary:logistic                                            ┃
┃                                                                               ┃
┃  2. Training Metrics:                                                        ┃
┃     ├─ train-auc (by epoch)                                                  ┃
┃     ├─ validation-auc (by epoch)                                             ┃
┃     └─ training_time_seconds                                                 ┃
┃                                                                               ┃
┃  3. Evaluation Metrics:                                                      ┃
┃     ├─ test_accuracy                                                         ┃
┃     ├─ test_f1_score                                                         ┃
┃     ├─ test_roc_auc                                                          ┃
┃     └─ business_cost                                                         ┃
┃                                                                               ┃
┃  4. Artifacts:                                                               ┃
┃     ├─ Model: s3://.../models/model.tar.gz                                   ┃
┃     ├─ Training data: s3://.../data/train/                                   ┃
┃     └─ Evaluation results: evaluation_results.json                           ┃
┃                                                                               ┃
┃  COMPARISON & ANALYSIS:                                                       ┃
┃  └─ SageMaker Studio → Experiments → Compare trials side-by-side            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛


════════════════════════════════════════════════════════════════════════════════════════════
                              CLOUDWATCH ALARMS & ALERTS
════════════════════════════════════════════════════════════════════════════════════════════

ALARM 1: Model Invocation Errors
├─ Metric: ModelInvocationErrors (AWS/SageMaker)
├─ Threshold: > 10 errors in 5 minutes
├─ Action: Send SNS alert
└─ Use Case: Detect endpoint failures

ALARM 2: Model Latency
├─ Metric: ModelLatency (AWS/SageMaker)
├─ Threshold: > 1000 ms (p99)
├─ Action: Send SNS alert + Auto-scale
└─ Use Case: Maintain SLA compliance

ALARM 3: Data Drift
├─ Metric: Custom (from drift_detection.py)
├─ Threshold: KL divergence > 0.5
├─ Action: Trigger retraining pipeline
└─ Use Case: Adapt to changing data

ALARM 4: Model Quality Degradation
├─ Metric: Accuracy (from model_monitor.py)
├─ Threshold: < 0.70
├─ Action: Page on-call engineer
└─ Use Case: Critical quality issues
```


════════════════════════════════════════════════════════════════════════════════════════════
# 4. EVALUATION FRAMEWORK MIND MAP
════════════════════════════════════════════════════════════════════════════════════════════

```text
📈 MODEL EVALUATION - COMPREHENSIVE METRICS & QUALITY GATES
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│                    ENTRY POINT: evaluate.py                                 │
│                    src/evaluation/evaluate.py                               │
└────────────────────────┬────────────────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────────────────┐
│               1. Load Model & Test Data                                    │
├────────────────────────────────────────────────────────────────────────────┤
│  MODEL SOURCE:                                                             │
│  └─ /opt/ml/processing/model/xgboost-model (from training job)            │
│                                                                            │
│  TEST DATA:                                                                │
│  └─ /opt/ml/processing/test/test.csv (held-out 15% of data)               │
│                                                                            │
│  VALIDATION:                                                               │
│  ├─ Verify 8 features present                                             │
│  ├─ Check for missing values                                              │
│  └─ Validate target column exists                                         │
└────────────────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────────────────┐
│               2. Generate Predictions                                      │
├────────────────────────────────────────────────────────────────────────────┤
│  PROCESS:                                                                  │
│  1. Scale features using scaler.pkl                                       │
│  2. Call model.predict_proba(X_test)                                      │
│  3. Get prediction probabilities                                          │
│     └─ [[0.2, 0.8], [0.9, 0.1], ...]  # [no diabetes, diabetes]          │
│  4. Apply threshold (default 0.5)                                         │
│     └─ If prob[1] >= 0.5 → Predict 1 (diabetes)                           │
│                                                                            │
│  OUTPUT:                                                                   │
│  ├─ y_pred: Binary predictions [0, 1, 1, 0, ...]                          │
│  └─ y_prob: Probabilities [0.2, 0.9, 0.8, 0.1, ...]                       │
└────────────────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────────────────┐
│               3. Calculate Standard Metrics                                │
│               (src/evaluation/metrics.py)                                  │
├────────────────────────────────────────────────────────────────────────────┤
│  CLASSIFICATION METRICS:                                                   │
│  ├─ Accuracy: (TP + TN) / Total                                            │
│  │  Example: 85% correct predictions                                      │
│  │                                                                         │
│  ├─ Precision: TP / (TP + FP)                                              │
│  │  Example: 80% of predicted diabetes cases are correct                  │
│  │                                                                         │
│  ├─ Recall (Sensitivity): TP / (TP + FN)                                   │
│  │  Example: 75% of actual diabetes cases detected                        │
│  │                                                                         │
│  ├─ F1-Score: 2 * (Precision * Recall) / (Precision + Recall)             │
│  │  Example: 0.77 (harmonic mean)                                         │
│  │                                                                         │
│  └─ ROC-AUC: Area under ROC curve                                          │
│     Example: 0.88 (excellent discrimination)                              │
│                                                                            │
│  CONFUSION MATRIX:                                                         │
│                 Predicted                                                  │
│               No    Yes                                                    │
│  Actual  No  [TN]   [FP]   ← False Positive (Type I Error)                │
│          Yes [FN]   [TP]   ← False Negative (Type II Error)               │
│                                                                            │
│  Example:                                                                  │
│  [[50, 10],     50 correct negatives, 10 false alarms                     │
│   [15, 41]]     15 missed cases, 41 correct positives                     │
└────────────────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────────────────┐
│               4. Calculate Business Metrics                                │
│               (Custom metrics for healthcare domain)                       │
├────────────────────────────────────────────────────────────────────────────┤
│  BUSINESS COST METRIC:                                                     │
│  ├─ False Positive Cost: $100                                             │
│  │  └─ Unnecessary medical tests/treatment                                │
│  │                                                                         │
│  ├─ False Negative Cost: $500                                             │
│  │  └─ Missed diagnosis → delayed treatment → complications               │
│  │                                                                         │
│  └─ Total Cost = (FP × $100) + (FN × $500)                                │
│     Example: (10 × $100) + (15 × $500) = $8,500                           │
│                                                                            │
│  YOUDEN'S INDEX:                                                           │
│  └─ Sensitivity + Specificity - 1                                          │
│     Example: 0.75 + 0.83 - 1 = 0.58 (good)                                │
│     Use: Find optimal classification threshold                            │
│                                                                            │
│  CALIBRATION ERROR:                                                        │
│  └─ Are predicted probabilities reliable?                                  │
│     Example: If model says 80% → is it correct 80% of time?               │
└────────────────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────────────────┐
│               5. Generate Visualizations                                   │
├────────────────────────────────────────────────────────────────────────────┤
│  PLOTS CREATED:                                                            │
│  ├─ Confusion Matrix Heatmap                                               │
│  ├─ ROC Curve                                                              │
│  ├─ Precision-Recall Curve                                                 │
│  ├─ Feature Importance Bar Chart                                           │
│  └─ Calibration Curve                                                      │
│                                                                            │
│  SAVED TO:                                                                 │
│  └─ /opt/ml/processing/evaluation/plots/                                   │
│     → s3://.../evaluation/plots/                                           │
└────────────────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────────────────┐
│               6. Save Evaluation Report                                    │
├────────────────────────────────────────────────────────────────────────────┤
│  OUTPUT FILE: evaluation_results.json                                      │
│  {                                                                         │
│    "metrics": {                                                            │
│      "accuracy": 0.85,                                                     │
│      "precision": 0.80,                                                    │
│      "recall": 0.75,                                                       │
│      "f1_score": 0.77,                                                     │
│      "roc_auc": 0.88,                                                      │
│      "business_cost": 8500,                                                │
│      "youden_index": 0.58                                                  │
│    },                                                                      │
│    "confusion_matrix": [[50, 10], [15, 41]],                              │
│    "classification_report": {...},                                         │
│    "threshold": 0.5,                                                       │
│    "timestamp": "2025-11-06T12:00:00Z"                                     │
│  }                                                                         │
│                                                                            │
│  DESTINATION:                                                              │
│  └─ s3://.../evaluation/evaluation_results.json                            │
│                                                                            │
│  USED BY:                                                                  │
│  ├─ ConditionStep (quality gates)                                         │
│  ├─ Model Registry (metadata)                                             │
│  └─ Monitoring dashboard                                                  │
└────────────────────────────────────────────────────────────────────────────┘


════════════════════════════════════════════════════════════════════════════════════════════
                              QUALITY GATES (CONDITIONAL REGISTRATION)
════════════════════════════════════════════════════════════════════════════════════════════

GATE 1: Accuracy >= 0.75
├─ IF PASS → Continue to next gate
└─ IF FAIL → Skip model registration

GATE 2: F1-Score >= 0.70
├─ IF PASS → Continue to next gate
└─ IF FAIL → Skip model registration

GATE 3: ROC-AUC >= 0.80
├─ IF PASS → Register model to Model Registry
└─ IF FAIL → Skip model registration

ALL GATES MUST PASS (AND logic)
└─ Ensures only high-quality models reach production
```


════════════════════════════════════════════════════════════════════════════════════════════
# 5. DATA PROCESSING MIND MAP
════════════════════════════════════════════════════════════════════════════════════════════

```text
🔄 DATA PROCESSING - FROM RAW TO MODEL-READY
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│                    ENTRY POINT: preprocessing.py                            │
│                    src/processing/preprocessing.py                          │
└────────────────────────┬────────────────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────────────────┐
│               1. Download Raw Data                                         │
├────────────────────────────────────────────────────────────────────────────┤
│  SOURCE OPTIONS:                                                           │
│  ├─ Option A: Download from public URL                                    │
│  │  └─ https://raw.githubusercontent.com/.../diabetes.data.csv            │
│  │                                                                         │
│  └─ Option B: Read from S3                                                │
│     └─ s3://.../data/raw/diabetes.csv                                     │
│                                                                            │
│  RAW DATA SHAPE:                                                           │
│  ├─ Rows: 768 samples                                                     │
│  ├─ Columns: 9 (8 features + 1 target)                                   │
│  └─ No headers (column names added)                                       │
│                                                                            │
│  FEATURES:                                                                 │
│  ├─ Pregnancies (number of times pregnant)                                │
│  ├─ Glucose (plasma glucose concentration)                                │
│  ├─ BloodPressure (diastolic blood pressure mm Hg)                        │
│  ├─ SkinThickness (triceps skin fold thickness mm)                        │
│  ├─ Insulin (2-Hour serum insulin mu U/ml)                                │
│  ├─ BMI (body mass index weight/height²)                                  │
│  ├─ DiabetesPedigreeFunction (diabetes pedigree function)                 │
│  └─ Age (years)                                                           │
│                                                                            │
│  TARGET:                                                                   │
│  └─ Outcome (0 = no diabetes, 1 = diabetes)                               │
└────────────────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────────────────┐
│               2. Data Quality Checks                                       │
├────────────────────────────────────────────────────────────────────────────┤
│  VALIDATION CHECKS:                                                        │
│  ├─ Missing Values:                                                       │
│  │  └─ Replace 0 with NaN for biological features                        │
│  │     (Glucose, BP, SkinThickness, Insulin, BMI can't be 0)             │
│  │                                                                         │
│  ├─ Data Types:                                                           │
│  │  └─ All features must be numeric                                       │
│  │                                                                         │
│  ├─ Value Ranges:                                                         │
│  │  ├─ Glucose: 0-200 mg/dL (normal range)                               │
│  │  ├─ BMI: 0-70                                                         │
│  │  └─ Age: 0-120                                                        │
│  │                                                                         │
│  └─ Outlier Detection:                                                    │
│     └─ IQR method (values > Q3 + 1.5*IQR)                                 │
│                                                                            │
│  ACTIONS ON ISSUES:                                                        │
│  ├─ Log warnings                                                          │
│  ├─ Save data quality report                                              │
│  └─ Continue if < 10% missing                                             │
└────────────────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────────────────┐
│               3. Handle Missing Values                                     │
├────────────────────────────────────────────────────────────────────────────┤
│  IMPUTATION STRATEGY:                                                      │
│  ├─ Numeric Features → Median imputation                                  │
│  │  Example: BMI missing → Fill with median BMI (32.0)                   │
│  │                                                                         │
│  └─ Categorical Features → Mode imputation                                │
│     (Not applicable for this dataset)                                     │
│                                                                            │
│  WHY MEDIAN (not mean)?                                                    │
│  └─ Robust to outliers                                                    │
│     Example: If few patients have BMI > 50                                │
│              Median won't be affected                                     │
└────────────────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────────────────┐
│               4. Train/Validation/Test Split                               │
├────────────────────────────────────────────────────────────────────────────┤
│  SPLIT STRATEGY:                                                           │
│  ├─ Training: 70% (537 samples)                                           │
│  │  └─ Used for: Model training                                           │
│  │                                                                         │
│  ├─ Validation: 15% (115 samples)                                         │
│  │  └─ Used for: Hyperparameter tuning, early stopping                   │
│  │                                                                         │
│  └─ Test: 15% (116 samples)                                               │
│     └─ Used for: Final model evaluation (never seen during training)     │
│                                                                            │
│  STRATIFICATION:                                                           │
│  └─ Maintain class balance across splits                                  │
│     Example: If 35% diabetes in original                                  │
│              → 35% diabetes in train/val/test                             │
│                                                                            │
│  RANDOM SEED: 42 (for reproducibility)                                    │
└────────────────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────────────────┐
│               5. Feature Scaling                                           │
├────────────────────────────────────────────────────────────────────────────┤
│  METHOD: StandardScaler (Z-score normalization)                            │
│  Formula: z = (x - μ) / σ                                                 │
│                                                                            │
│  CRITICAL: Fit on training data ONLY                                       │
│  ┌────────────────────────────────────────────────────────────┐           │
│  │  1. scaler.fit(X_train)                                    │           │
│  │     └─ Calculate mean & std from training data             │           │
│  │                                                            │           │
│  │  2. X_train_scaled = scaler.transform(X_train)             │           │
│  │     X_val_scaled = scaler.transform(X_val)                 │           │
│  │     X_test_scaled = scaler.transform(X_test)               │           │
│  │     └─ Apply SAME mean & std to all splits                 │           │
│  │                                                            │           │
│  │  3. Save scaler.pkl                                        │           │
│  │     └─ Reuse for inference (production)                    │           │
│  └────────────────────────────────────────────────────────────┘           │
│                                                                            │
│  WHY SCALING?                                                              │
│  └─ XGBoost doesn't strictly require it, but it helps:                    │
│     ├─ Faster convergence                                                 │
│     ├─ Better numerical stability                                         │
│     └─ Consistent with production inference                               │
│                                                                            │
│  DATA LEAKAGE PREVENTION:                                                  │
│  ❌ WRONG: scaler.fit(X_all) → Uses test data info                        │
│  ✅ CORRECT: scaler.fit(X_train) → Only training data                     │
└────────────────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────────────────┐
│               6. Save Processed Data                                       │
├────────────────────────────────────────────────────────────────────────────┤
│  OUTPUT FILES:                                                             │
│  ├─ /opt/ml/processing/output/train/train.csv                             │
│  │  → s3://.../data/train/train.csv                                       │
│  │                                                                         │
│  ├─ /opt/ml/processing/output/validation/validation.csv                   │
│  │  → s3://.../data/validation/validation.csv                             │
│  │                                                                         │
│  ├─ /opt/ml/processing/output/test/test.csv                               │
│  │  → s3://.../data/test/test.csv                                         │
│  │                                                                         │
│  └─ /opt/ml/processing/output/model/scaler.pkl                            │
│     → s3://.../preprocessing/model/scaler.pkl                              │
│                                                                            │
│  METADATA:                                                                 │
│  └─ metadata.json (statistics, column names, data quality report)         │
└────────────────────────────────────────────────────────────────────────────┘


════════════════════════════════════════════════════════════════════════════════════════════
                              FEATURE ENGINEERING (OPTIONAL)
════════════════════════════════════════════════════════════════════════════════════════════

POTENTIAL ENHANCEMENTS (src/processing/feature_engineering.py):

1. Polynomial Features
   ├─ BMI² (captures non-linear relationships)
   └─ Age × Glucose (interaction term)

2. Binning
   ├─ Age groups: [<30, 30-45, 45-60, >60]
   └─ Glucose levels: [Normal, Pre-diabetic, Diabetic]

3. Domain-Specific Features
   ├─ BMI Category: Underweight/Normal/Overweight/Obese
   ├─ Risk Score: Combined feature based on medical guidelines
   └─ Metabolic Syndrome Indicator: Multiple risk factors present
```


════════════════════════════════════════════════════════════════════════════════════════════
# 6. COMPLETE END-TO-END FLOW
════════════════════════════════════════════════════════════════════════════════════════════

```text
🔄 COMPLETE MLOPS WORKFLOW - FROM CODE TO PRODUCTION
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│                         PHASE 1: DEVELOPMENT                                │
└─────────────────────────────────────────────────────────────────────────────┘

Developer
    │
    ├─ 1. Write code (VSCode)
    │  ├─ pipelines/training_pipeline.py
    │  ├─ src/training/train.py
    │  ├─ src/evaluation/evaluate.py
    │  └─ config/config.yaml
    │
    ├─ 2. Local testing
    │  ├─ pytest tests/
    │  ├─ black src/
    │  └─ flake8 src/
    │
    └─ 3. Git commit & push
       └─ git push origin main


┌─────────────────────────────────────────────────────────────────────────────┐
│                         PHASE 2: CI/CD (GITHUB ACTIONS)                     │
└─────────────────────────────────────────────────────────────────────────────┘

GitHub Actions (.github/workflows/mlops_pipeline.yaml)
    │
    ├─ Job 1: Code Quality (2 min)
    │  ├─ Run tests (pytest)
    │  ├─ Check formatting (black)
    │  └─ Lint (flake8)
    │
    ├─ Job 2: Data Validation (1 min)
    │  └─ Download & validate diabetes.csv
    │
    ├─ Job 3: Upload to S3 (1 min)
    │  └─ aws s3 cp → s3://.../data/raw/
    │
    └─ Job 4: Execute Pipeline (25 min)
       └─ python pipelines/training_pipeline.py --execute


┌─────────────────────────────────────────────────────────────────────────────┐
│                         PHASE 3: SAGEMAKER PIPELINE                         │
└─────────────────────────────────────────────────────────────────────────────┘

SageMaker Pipeline (diabetes-classification-pipeline)
    │
    ├─ Step 1: PreprocessData (5 min)
    │  ├─ Instance: ml.m5.xlarge
    │  ├─ Download diabetes.csv
    │  ├─ Split train/val/test
    │  ├─ Scale features
    │  └─ Upload to S3
    │
    ├─ Step 2: TrainModel (10 min)
    │  ├─ Instance: ml.m5.xlarge (SPOT!)
    │  ├─ Train XGBoost
    │  ├─ Early stopping
    │  ├─ Save model.tar.gz
    │  └─ Checkpoint to S3
    │
    ├─ Step 3: EvaluateModel (5 min)
    │  ├─ Load model & test data
    │  ├─ Calculate metrics
    │  └─ Save evaluation_results.json
    │
    ├─ Step 4: TrackExperiment (2 min)
    │  └─ Log to SageMaker Experiments
    │
    └─ Step 5: Conditional Registration
       ├─ Check: accuracy >= 0.75?
       ├─ Check: f1_score >= 0.70?
       ├─ Check: roc_auc >= 0.80?
       │
       ├─ IF ALL PASS:
       │  └─ Register to Model Registry
       │     └─ Status: PendingManualApproval
       │
       └─ IF ANY FAIL:
          └─ Skip registration (send alert)


┌─────────────────────────────────────────────────────────────────────────────┐
│                         PHASE 4: MODEL REGISTRY                             │
└─────────────────────────────────────────────────────────────────────────────┘

SageMaker Model Registry
    │
    ├─ Model Package Group: mlops-diabetes-model-group-dev
    │
    ├─ Model Version: v1
    │  ├─ Model Data: s3://.../models/model.tar.gz
    │  ├─ Metrics: evaluation_results.json
    │  ├─ Status: PendingManualApproval
    │  └─ Lineage: Training job ARN
    │
    └─ Manual/Automated Approval
       ├─ Review metrics
       ├─ Check lineage
       └─ Approve → Status: Approved


┌─────────────────────────────────────────────────────────────────────────────┐
│                         PHASE 5: DEPLOYMENT                                 │
└─────────────────────────────────────────────────────────────────────────────┘

Deployment (GitHub Actions Job 5 OR Manual)
    │
    ├─ 1. Get approved model
    │  └─ sagemaker.list_model_packages(Approved)
    │
    ├─ 2. Create SageMaker Model
    │  └─ Includes inference.py handlers
    │
    ├─ 3. Create Endpoint Config
    │  ├─ Instance: ml.t2.medium
    │  └─ Data capture enabled
    │
    ├─ 4. Deploy Endpoint (5-10 min)
    │  └─ diabetes-classifier-prod
    │
    └─ 5. Enable Auto-scaling
       ├─ Min: 1 instance
       └─ Max: 5 instances


┌─────────────────────────────────────────────────────────────────────────────┐
│                         PHASE 6: MONITORING                                 │
└─────────────────────────────────────────────────────────────────────────────┘

Continuous Monitoring
    │
    ├─ Data Quality Monitor (Hourly)
    │  ├─ Check feature drift
    │  ├─ Compare with baseline
    │  └─ Alert if drift > 0.5
    │
    ├─ Model Quality Monitor (Daily)
    │  ├─ Check accuracy vs ground truth
    │  ├─ Track F1, ROC-AUC
    │  └─ Alert if accuracy < 0.70
    │
    ├─ CloudWatch Alarms
    │  ├─ Model latency > 1000ms
    │  ├─ Invocation errors > 10
    │  └─ Auto-scale triggers
    │
    └─ Automated Actions
       ├─ Send SNS alerts
       ├─ Create Jira tickets
       └─ Trigger retraining (if drift)


┌─────────────────────────────────────────────────────────────────────────────┐
│                         PHASE 7: PRODUCTION INFERENCE                       │
└─────────────────────────────────────────────────────────────────────────────┘

Client Application
    │
    ├─ Send request
    │  └─ POST https://.../endpoints/diabetes-classifier-prod/invocations
    │     Body: {"features": [6, 148, 72, 35, 0, 33.6, 0.627, 50]}
    │
    ├─ SageMaker Endpoint
    │  ├─ input_fn() → Parse JSON
    │  ├─ predict_fn() → Scale & predict
    │  └─ output_fn() → Format response
    │
    └─ Receive response
       └─ {"prediction": 1, "probability": 0.85, "confidence": "high"}


┌─────────────────────────────────────────────────────────────────────────────┐
│                         PHASE 8: RETRAINING (CONTINUOUS IMPROVEMENT)        │
└─────────────────────────────────────────────────────────────────────────────┘

Retraining Triggers
    │
    ├─ Trigger 1: Data Drift Detected
    │  └─ KL divergence > 0.5 for 3 days
    │
    ├─ Trigger 2: Model Quality Drop
    │  └─ Accuracy < 0.70 for 1 week
    │
    ├─ Trigger 3: Scheduled (Monthly)
    │  └─ Cron: 0 0 1 * *
    │
    └─ Action: Re-run pipeline
       └─ Fetch new data → Train → Evaluate → Deploy


════════════════════════════════════════════════════════════════════════════════════════════
                              SUMMARY: WHY THIS ARCHITECTURE WORKS
════════════════════════════════════════════════════════════════════════════════════════════

1. **Automation**: GitHub Actions → SageMaker Pipeline (no manual steps)
2. **Quality Gates**: Only good models reach production (metrics thresholds)
3. **Reproducibility**: Everything tracked (experiments, lineage, git commits)
4. **Cost Optimization**: Spot instances, auto-scaling, lifecycle policies
5. **Monitoring**: Continuous quality tracking with automated alerts
6. **Scalability**: Auto-scales from 1 to 5 instances based on traffic
7. **Security**: IAM roles, VPC endpoints, encryption at rest
8. **Compliance**: Full audit trail (CloudTrail, SageMaker logs)
9. **Modularity**: Each component independent, easy to update
10. **Production-Ready**: Tested, monitored, and battle-hardened patterns

COST: ~$0.08 per training run, ~$20/month for 1 endpoint
TIME: 25 minutes from code push to deployed model
QUALITY: Only 85%+ accuracy models reach production
```

---

## Document Change Log

| Date | Version | Changes |
|------|---------|---------|
| 2025-11-05 | 1.0 | Initial training pipeline mindmap |
| 2025-11-06 | 2.0 | Added deployment, monitoring, evaluation, data processing, and end-to-end flow mindmaps |

---

## How to Use These Mind Maps

1. **Training Pipeline** - Understand how models are trained in SageMaker
2. **Deployment Pipeline** - Learn how models go from registry to production
3. **Monitoring System** - See how quality is tracked continuously
4. **Evaluation Framework** - Understand quality gates and metrics
5. **Data Processing** - Follow data from raw to model-ready
6. **End-to-End Flow** - Complete picture from code to production

**Use Cases:**
- Onboarding new team members
- Debugging pipeline issues
- Planning new features
- Documentation for audits
- Architecture reviews
```