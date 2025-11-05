# Training Pipeline Mind Map

Generated: 2025-11-05

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
