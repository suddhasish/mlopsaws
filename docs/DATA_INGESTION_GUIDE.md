# 📊 Data Ingestion & Processing Guide

**Complete guide to how data flows through the MLOps pipeline**

---

## 🔍 Current Data Flow (As Implemented)

### Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA FLOW ARCHITECTURE                        │
└─────────────────────────────────────────────────────────────────┘

STEP 1: Data Source
┌──────────────────────────────────────┐
│ GitHub Public Repository             │
│ https://raw.githubusercontent.com/   │
│ jbrownlee/Datasets/master/           │
│ pima-indians-diabetes.data.csv       │
└──────────────┬───────────────────────┘
               │
               ▼
STEP 2: GitHub Actions Workflow Triggered
┌──────────────────────────────────────┐
│ .github/workflows/                   │
│ mlops_pipeline.yaml                  │
│                                      │
│ Jobs:                                │
│ 1. Code Quality ✅                   │
│ 2. Unit Tests ✅                     │
│ 3. Data Validation ✅                │
│ 4. Upload Data to S3 ← YOU ARE HERE  │
└──────────────┬───────────────────────┘
               │
               ▼
STEP 3: Download Script Runs (GitHub Runner)
┌──────────────────────────────────────┐
│ src/processing/download_data.py      │
│                                      │
│ Actions:                             │
│ 1. Downloads CSV from GitHub         │
│ 2. Saves to data/raw/diabetes.csv    │
│ 3. Validates shape & content         │
└──────────────┬───────────────────────┘
               │
               ▼
STEP 4: Upload to AWS S3 (GitHub Runner)
┌──────────────────────────────────────┐
│ aws s3 cp data/raw/diabetes.csv \    │
│   s3://BUCKET/diabetes-project/      │
│         data/raw/diabetes.csv        │
└──────────────┬───────────────────────┘
               │
               ▼
STEP 5: S3 Bucket Storage
┌──────────────────────────────────────┐
│ AWS S3: mlops-diabetes-ACCOUNT-ENV   │
│                                      │
│ Structure:                           │
│ s3://BUCKET/                         │
│ └── diabetes-project/                │
│     ├── data/                        │
│     │   ├── raw/                     │
│     │   │   └── diabetes.csv ✅      │
│     │   ├── processed/               │
│     │   │   ├── train.csv            │
│     │   │   ├── validation.csv       │
│     │   │   └── test.csv             │
│     │   └── baseline/                │
│     ├── models/                      │
│     └── monitoring/                  │
└──────────────┬───────────────────────┘
               │
               ▼
STEP 6: SageMaker Processing Job
┌──────────────────────────────────────┐
│ SageMaker Processing (Scikit-Learn)  │
│                                      │
│ Input: s3://BUCKET/.../raw/          │
│ Output: s3://BUCKET/.../processed/   │
│                                      │
│ Actions:                             │
│ 1. Read diabetes.csv from S3         │
│ 2. Feature engineering               │
│ 3. Train/validation/test split       │
│ 4. Scale features                    │
│ 5. Save processed CSVs to S3         │
└──────────────┬───────────────────────┘
               │
               ▼
STEP 7: SageMaker Training Job
┌──────────────────────────────────────┐
│ SageMaker Training (XGBoost)         │
│                                      │
│ Input: s3://BUCKET/.../processed/    │
│ Output: s3://BUCKET/.../models/      │
│                                      │
│ Actions:                             │
│ 1. Read train.csv & validation.csv   │
│ 2. Train XGBoost model               │
│ 3. Evaluate on validation set        │
│ 4. Save model to S3                  │
└──────────────┬───────────────────────┘
               │
               ▼
STEP 8: Model Deployment
┌──────────────────────────────────────┐
│ SageMaker Endpoint                   │
│                                      │
│ Model: s3://BUCKET/.../models/       │
│ Status: InService                    │
│                                      │
│ Ready for real-time predictions!     │
└──────────────────────────────────────┘
```

---

## 📝 Current Implementation Details

### Where Data Comes From

**Current Source:** Public GitHub repository  
**URL:** `https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv`

**Why GitHub?**
- ✅ Free public dataset
- ✅ Always available
- ✅ No authentication needed
- ✅ Good for learning/demo
- ⚠️ **Not for production use**

### Current Workflow File

**File:** `.github/workflows/mlops_pipeline.yaml`

```yaml
# Job 4: Upload Data to S3
upload-data:
  name: Upload Data to S3
  runs-on: ubuntu-latest
  needs: data-validation
  if: github.ref == 'refs/heads/main'
  
  steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_REGION }}
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install boto3 pandas
    
    # Downloads from GitHub public repo
    - name: Download data
      run: |
        python src/processing/download_data.py
    
    # Uploads to S3
    - name: Upload to S3
      env:
        S3_BUCKET: ${{ secrets.S3_BUCKET_NAME }}
      run: |
        aws s3 cp data/raw/diabetes.csv s3://$S3_BUCKET/diabetes-project/data/raw/diabetes.csv
```

### Current Download Script

**File:** `src/processing/download_data.py`

```python
def download_diabetes_dataset(output_dir='data/raw'):
    """
    Download the Pima Indians Diabetes dataset
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Dataset URL
    url = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv"
    output_path = os.path.join(output_dir, 'diabetes.csv')
    
    logger.info(f"Downloading dataset from {url}")
    
    try:
        # Download the file
        urllib.request.urlretrieve(url, output_path)
        logger.info(f"Dataset downloaded successfully to {output_path}")
        
        # Verify the download
        df = pd.read_csv(output_path, header=None)
        logger.info(f"Dataset shape: {df.shape}")
        
        return output_path
    except Exception as e:
        logger.error(f"Error downloading dataset: {str(e)}")
        raise
```

---

## ❓ Should S3 Always Pick Data from Repo?

### **Short Answer: NO** ❌

**The GitHub repository should NOT be the production data source.**

### Why Current Approach Works for Learning

✅ **Pros:**
- Simple setup
- No external dependencies
- Reproducible
- Good for demos/tutorials
- Free public dataset

❌ **Cons for Production:**
- Not your real data
- No control over source
- External dependency (GitHub could change/delete)
- No versioning control
- No data governance
- Can't handle private/sensitive data

---

## 🏭 Production Data Ingestion Options

### Option 1: Direct S3 Upload (Simple) ⭐ RECOMMENDED FOR SMALL DATASETS

**Use Case:** Manual data updates, small datasets, one-time ingestion

**Architecture:**
```
Your Data Source (CSV/Database/API)
           │
           ▼
┌─────────────────────┐
│ Manual Upload       │
│ via AWS CLI/Console │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ S3: mlops-diabetes- │
│ ACCOUNT-ENV         │
│ /data/raw/          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ SageMaker Pipeline  │
│ Auto-Triggered      │
└─────────────────────┘
```

**Implementation:**

```powershell
# Upload new data manually
aws s3 cp your-new-data.csv s3://mlops-diabetes-123456789012-dev/diabetes-project/data/raw/diabetes.csv

# Verify upload
aws s3 ls s3://mlops-diabetes-123456789012-dev/diabetes-project/data/raw/

# Trigger pipeline manually (GitHub Actions)
gh workflow run mlops_pipeline.yaml
```

**Pros:**
- ✅ Simple and direct
- ✅ Full control over data
- ✅ No intermediate systems
- ✅ Good for infrequent updates

**Cons:**
- ❌ Manual process
- ❌ No automation
- ❌ Human error prone

---

### Option 2: S3 Event-Triggered Pipeline ⭐ RECOMMENDED FOR PRODUCTION

**Use Case:** Automated ingestion, real-time updates, production workloads

**Architecture:**
```
┌────────────────────────────────────────────────────────────┐
│ Data Source (Database/API/File Upload)                     │
└──────────────────┬─────────────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────────┐
│ Upload to S3                                               │
│ s3://mlops-diabetes-ACCOUNT/data/raw/new-data-TIMESTAMP.csv│
└──────────────────┬─────────────────────────────────────────┘
                   │
                   ▼ (S3 Event Notification)
┌────────────────────────────────────────────────────────────┐
│ AWS Lambda Function                                        │
│ - Triggered automatically on S3 upload                     │
│ - Validates data schema                                    │
│ - Checks data quality                                      │
│ - Triggers SageMaker Pipeline                              │
└──────────────────┬─────────────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────────┐
│ SageMaker Pipeline Execution                               │
│ - Processing Job (feature engineering)                     │
│ - Training Job (model training)                            │
│ - Deployment (model update)                                │
└────────────────────────────────────────────────────────────┘
```

**Implementation:**

**Step 1: Create Lambda Function**

```python
# lambda/s3_trigger_pipeline.py
import json
import boto3
import os

sagemaker = boto3.client('sagemaker')

def lambda_handler(event, context):
    """
    Triggered when new data uploaded to S3
    Starts SageMaker Pipeline
    """
    # Get S3 event details
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    print(f"New data detected: s3://{bucket}/{key}")
    
    # Validate data path
    if not key.startswith('data/raw/'):
        print(f"Ignoring non-data file: {key}")
        return {'statusCode': 200, 'body': 'Ignored'}
    
    # Start SageMaker Pipeline
    pipeline_name = os.environ['PIPELINE_NAME']
    
    response = sagemaker.start_pipeline_execution(
        PipelineName=pipeline_name,
        PipelineParameters=[
            {
                'Name': 'InputDataUrl',
                'Value': f"s3://{bucket}/{key}"
            }
        ]
    )
    
    print(f"Started pipeline: {response['PipelineExecutionArn']}")
    
    return {
        'statusCode': 200,
        'body': json.dumps(f"Pipeline triggered: {response['PipelineExecutionArn']}")
    }
```

**Step 2: Configure S3 Event Notification**

```bash
# Create S3 event notification
aws s3api put-bucket-notification-configuration \
  --bucket mlops-diabetes-123456789012-dev \
  --notification-configuration file://s3-notification.json
```

**s3-notification.json:**
```json
{
  "LambdaFunctionConfigurations": [
    {
      "Id": "TriggerMLOpsPipeline",
      "LambdaFunctionArn": "arn:aws:lambda:us-east-1:123456789012:function:trigger-mlops-pipeline",
      "Events": ["s3:ObjectCreated:*"],
      "Filter": {
        "Key": {
          "FilterRules": [
            {
              "Name": "prefix",
              "Value": "diabetes-project/data/raw/"
            },
            {
              "Name": "suffix",
              "Value": ".csv"
            }
          ]
        }
      }
    }
  ]
}
```

**Pros:**
- ✅ Fully automated
- ✅ Real-time processing
- ✅ Scales automatically
- ✅ Production-ready
- ✅ Event-driven architecture

**Cons:**
- ⚠️ More complex setup
- ⚠️ Additional AWS costs (Lambda executions)

---

### Option 3: Scheduled Data Ingestion ⭐ RECOMMENDED FOR BATCH UPDATES

**Use Case:** Daily/weekly data updates from external systems

**Architecture:**
```
┌────────────────────────────────────────────────────────────┐
│ External Data Source (Database, API, Data Lake)            │
└──────────────────┬─────────────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────────┐
│ AWS EventBridge Schedule (Cron)                            │
│ - Daily: cron(0 2 * * ? *)      ← 2 AM every day          │
│ - Weekly: cron(0 2 ? * MON *)   ← 2 AM every Monday       │
└──────────────────┬─────────────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────────┐
│ AWS Lambda Function                                        │
│ - Extracts data from source                                │
│ - Transforms to required format                            │
│ - Uploads to S3                                            │
│ - Triggers SageMaker Pipeline                              │
└──────────────────┬─────────────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────────┐
│ S3 Bucket                                                  │
│ s3://mlops-diabetes-*/data/raw/diabetes-YYYY-MM-DD.csv     │
└──────────────────┬─────────────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────────┐
│ SageMaker Pipeline                                         │
│ - Processes latest data                                    │
│ - Trains model if data drift detected                      │
│ - Deploys if performance improves                          │
└────────────────────────────────────────────────────────────┘
```

**Implementation:**

```python
# lambda/scheduled_data_ingestion.py
import boto3
import pandas as pd
import os
from datetime import datetime

s3 = boto3.client('s3')
sagemaker = boto3.client('sagemaker')

def lambda_handler(event, context):
    """
    Scheduled data ingestion from external source
    """
    # 1. Extract data from source (example: RDS database)
    data = extract_data_from_source()
    
    # 2. Transform to required format
    df = transform_data(data)
    
    # 3. Upload to S3 with timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d')
    bucket = os.environ['S3_BUCKET']
    key = f"diabetes-project/data/raw/diabetes-{timestamp}.csv"
    
    # Save to S3
    df.to_csv(f"/tmp/diabetes-{timestamp}.csv", index=False)
    s3.upload_file(
        f"/tmp/diabetes-{timestamp}.csv",
        bucket,
        key
    )
    
    print(f"Uploaded data to s3://{bucket}/{key}")
    
    # 4. Trigger SageMaker Pipeline
    pipeline_name = os.environ['PIPELINE_NAME']
    response = sagemaker.start_pipeline_execution(
        PipelineName=pipeline_name,
        PipelineParameters=[
            {
                'Name': 'InputDataUrl',
                'Value': f"s3://{bucket}/{key}"
            },
            {
                'Name': 'DataDate',
                'Value': timestamp
            }
        ]
    )
    
    return {
        'statusCode': 200,
        'body': f"Pipeline triggered for {timestamp}"
    }

def extract_data_from_source():
    """Extract data from external source"""
    # Example: Query database
    # connection = psycopg2.connect(...)
    # df = pd.read_sql_query("SELECT * FROM diabetes_data WHERE date > ...", connection)
    # return df
    pass

def transform_data(data):
    """Transform data to required format"""
    # Apply business logic
    # Handle missing values
    # Feature engineering
    # return transformed_df
    pass
```

**EventBridge Rule (Terraform):**

```hcl
resource "aws_cloudwatch_event_rule" "daily_data_ingestion" {
  name                = "daily-data-ingestion-${var.environment}"
  description         = "Trigger data ingestion daily at 2 AM"
  schedule_expression = "cron(0 2 * * ? *)"
}

resource "aws_cloudwatch_event_target" "lambda" {
  rule      = aws_cloudwatch_event_rule.daily_data_ingestion.name
  target_id = "TriggerDataIngestion"
  arn       = aws_lambda_function.data_ingestion.arn
}
```

**Pros:**
- ✅ Automated on schedule
- ✅ Predictable execution
- ✅ Good for batch processing
- ✅ Can handle complex ETL

**Cons:**
- ⚠️ Not real-time
- ⚠️ Delayed updates

---

### Option 4: AWS Glue ETL Pipeline (Enterprise)

**Use Case:** Complex data transformations, multiple data sources, data lake

**Architecture:**
```
┌─────────────────────────────────────────────────────────────┐
│ Multiple Data Sources                                       │
│ ├── RDS Database                                            │
│ ├── S3 Data Lake                                            │
│ ├── DynamoDB                                                │
│ └── External APIs                                           │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ AWS Glue Crawler                                            │
│ - Discovers schema                                          │
│ - Updates Data Catalog                                      │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ AWS Glue ETL Job                                            │
│ - Joins data from multiple sources                          │
│ - Data cleaning & transformation                            │
│ - Feature engineering                                       │
│ - Outputs to S3 in Parquet format                           │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ S3 (Processed Data)                                         │
│ - Partitioned by date                                       │
│ - Columnar format (Parquet)                                 │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ SageMaker Pipeline                                          │
│ - Reads processed data                                      │
│ - Trains model                                              │
└─────────────────────────────────────────────────────────────┘
```

**Pros:**
- ✅ Handles large-scale data
- ✅ Serverless ETL
- ✅ Integrates with Data Catalog
- ✅ Supports complex transformations

**Cons:**
- ❌ Higher cost
- ❌ Complex setup
- ❌ Overkill for small datasets

---

### Option 5: Amazon Kinesis (Real-Time Streaming)

**Use Case:** Real-time data streams, IoT devices, continuous updates

**Architecture:**
```
┌─────────────────────────────────────────────────────────────┐
│ Real-Time Data Sources                                      │
│ ├── IoT Devices                                             │
│ ├── Mobile Apps                                             │
│ ├── Web Applications                                        │
│ └── Streaming APIs                                          │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ Amazon Kinesis Data Stream                                  │
│ - Ingests real-time data                                    │
│ - Shards scale automatically                                │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ Amazon Kinesis Firehose                                     │
│ - Buffers data                                              │
│ - Transforms (optional Lambda)                              │
│ - Delivers to S3 in batches                                 │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ S3 Bucket                                                   │
│ - Data stored in time-based partitions                      │
│ - s3://.../YYYY/MM/DD/HH/data-*.json                        │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ SageMaker Pipeline (Triggered by S3 Events)                 │
│ - Aggregates streaming data                                 │
│ - Retrains model periodically                               │
└─────────────────────────────────────────────────────────────┘
```

**Pros:**
- ✅ Real-time processing
- ✅ Scales to millions of events/sec
- ✅ Built-in data buffering

**Cons:**
- ❌ Complex architecture
- ❌ Higher costs
- ❌ Not needed for batch ML

---

## 🎯 Recommended Approach by Use Case

### Learning / Demo Projects
**Use:** Current implementation (GitHub download)
```python
# Keep existing: src/processing/download_data.py
python src/processing/download_data.py
aws s3 cp data/raw/diabetes.csv s3://BUCKET/data/raw/
```

### Small Production (Manual Updates)
**Use:** Option 1 - Direct S3 Upload
```bash
# Upload your data manually
aws s3 cp your-data.csv s3://BUCKET/data/raw/diabetes.csv

# Trigger pipeline via GitHub Actions
gh workflow run mlops_pipeline.yaml
```

### Production (Automated)
**Use:** Option 2 - S3 Event-Triggered
- Upload data to S3
- Lambda auto-triggers pipeline
- Fully automated

### Enterprise (Complex ETL)
**Use:** Option 3 (Scheduled) + Option 4 (Glue)
- Scheduled ingestion from databases
- Glue for complex transformations
- SageMaker for training

### Real-Time Applications
**Use:** Option 5 - Kinesis Streaming
- Continuous data streams
- Real-time model updates

---

## 📋 Decision Matrix

| Criteria | Current (GitHub) | Direct S3 | S3 Events | Scheduled | Glue | Kinesis |
|----------|-----------------|-----------|-----------|-----------|------|---------|
| **Setup Complexity** | ⭐ Easy | ⭐ Easy | ⭐⭐ Medium | ⭐⭐ Medium | ⭐⭐⭐ Hard | ⭐⭐⭐ Hard |
| **Automation** | ❌ None | ❌ Manual | ✅ Full | ✅ Full | ✅ Full | ✅ Full |
| **Real-Time** | ❌ No | ❌ No | ✅ Yes | ❌ No | ❌ No | ✅ Yes |
| **Production Ready** | ❌ No | ⚠️ Limited | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Cost** | 💰 Free | 💰 Low | 💰💰 Medium | 💰💰 Medium | 💰💰💰 High | 💰💰💰 High |
| **Best For** | Learning | Small data | Event-driven | Batch updates | Enterprise | Streaming |

---

## 🚀 Migration Path (Current → Production)

### Phase 1: Keep Current (Learning) ✅ YOU ARE HERE

```yaml
# .github/workflows/mlops_pipeline.yaml (current)
- name: Download data
  run: python src/processing/download_data.py

- name: Upload to S3
  run: aws s3 cp data/raw/diabetes.csv s3://$BUCKET/data/raw/
```

### Phase 2: Add Manual Upload Option

```yaml
# .github/workflows/mlops_pipeline.yaml (updated)
- name: Download or use existing data
  run: |
    if [ ! -f data/raw/diabetes.csv ]; then
      echo "Downloading sample data..."
      python src/processing/download_data.py
    else
      echo "Using existing data/raw/diabetes.csv"
    fi

- name: Upload to S3
  run: aws s3 cp data/raw/diabetes.csv s3://$BUCKET/data/raw/
```

**Now you can:**
- Place your own `diabetes.csv` in `data/raw/`
- Commit and push
- Pipeline uses YOUR data instead of downloading

### Phase 3: Add S3 Event Trigger (Production)

**Step 1: Create Lambda function**
```bash
# See "Option 2" above for Lambda code
cd lambda
zip -r function.zip s3_trigger_pipeline.py
aws lambda create-function \
  --function-name trigger-mlops-pipeline \
  --runtime python3.9 \
  --handler s3_trigger_pipeline.lambda_handler \
  --zip-file fileb://function.zip \
  --role arn:aws:iam::ACCOUNT:role/lambda-execution-role
```

**Step 2: Configure S3 notification**
```bash
# Add S3 event notification (see Option 2)
aws s3api put-bucket-notification-configuration ...
```

**Step 3: Upload triggers auto-execution**
```bash
# Now just upload data
aws s3 cp new-data.csv s3://BUCKET/data/raw/diabetes.csv
# Pipeline starts automatically! ✅
```

---

## 📊 Data Versioning Best Practices

### Recommended S3 Structure

```
s3://mlops-diabetes-ACCOUNT-ENV/
└── diabetes-project/
    ├── data/
    │   ├── raw/                          ← Raw data
    │   │   ├── diabetes-2024-11-01.csv  ← Dated versions
    │   │   ├── diabetes-2024-11-02.csv
    │   │   └── diabetes-latest.csv      ← Symlink/copy to latest
    │   ├── processed/                    ← After preprocessing
    │   │   ├── 2024-11-01/
    │   │   │   ├── train.csv
    │   │   │   ├── validation.csv
    │   │   │   └── test.csv
    │   │   └── 2024-11-02/
    │   │       └── ...
    │   └── baseline/                     ← For model monitoring
    │       └── baseline-2024-11-01.csv
    ├── models/                           ← Trained models
    │   ├── 2024-11-01/
    │   └── 2024-11-02/
    └── monitoring/                       ← Monitoring results
        └── violations/
```

### Enable S3 Versioning

```bash
# Enable versioning on bucket
aws s3api put-bucket-versioning \
  --bucket mlops-diabetes-123456789012-dev \
  --versioning-configuration Status=Enabled

# List versions
aws s3api list-object-versions \
  --bucket mlops-diabetes-123456789012-dev \
  --prefix diabetes-project/data/raw/
```

**Benefits:**
- ✅ Rollback to previous data versions
- ✅ Track data lineage
- ✅ Reproducibility
- ✅ Disaster recovery

---

## 🔒 Security Best Practices

### 1. Encryption

```hcl
# In Terraform (already implemented)
resource "aws_s3_bucket_server_side_encryption_configuration" "default" {
  bucket = aws_s3_bucket.mlops_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.mlops_key.arn
    }
  }
}
```

### 2. Access Control

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "sagemaker.amazonaws.com"
      },
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::mlops-diabetes-*/data/*"
    }
  ]
}
```

### 3. Data Validation

```python
# Add to workflow before upload
def validate_data(file_path):
    """Validate data before upload"""
    df = pd.read_csv(file_path)
    
    # Check shape
    assert df.shape[1] == 9, "Expected 9 columns"
    
    # Check for nulls
    assert df.isnull().sum().sum() == 0, "Data contains nulls"
    
    # Check data types
    assert df.dtypes[8] == 'int64', "Target must be binary"
    
    # Check target values
    assert set(df.iloc[:, 8].unique()) == {0, 1}, "Target must be 0 or 1"
    
    print("✅ Data validation passed")
    return True
```

---

## 📖 Next Steps

### For Current Learning Setup
1. Keep using GitHub download (simple)
2. Focus on ML pipeline
3. Migrate to production approach later

### For Production Deployment
1. Review options above
2. Choose based on your use case
3. Implement Option 2 (S3 Events) for automation
4. Add data validation
5. Enable S3 versioning
6. Set up monitoring

### Documentation to Create
- [ ] Data ingestion SOP (Standard Operating Procedure)
- [ ] Data schema documentation
- [ ] Data quality metrics
- [ ] Disaster recovery plan

---

## 🆘 Troubleshooting

### Data Not Uploading to S3

```bash
# Check AWS credentials
aws sts get-caller-identity

# Check S3 bucket exists
aws s3 ls s3://mlops-diabetes-123456789012-dev/

# Check file exists locally
ls -la data/raw/diabetes.csv

# Try manual upload with verbose
aws s3 cp data/raw/diabetes.csv s3://BUCKET/data/raw/ --debug
```

### Pipeline Not Triggering

```bash
# Check S3 event notification configured
aws s3api get-bucket-notification-configuration \
  --bucket mlops-diabetes-123456789012-dev

# Check Lambda permissions
aws lambda get-policy --function-name trigger-mlops-pipeline

# Check CloudWatch logs
aws logs tail /aws/lambda/trigger-mlops-pipeline --follow
```

---

**Summary:**
- **Current:** Download from GitHub → Good for learning ✅
- **Production:** S3 upload → Lambda trigger → SageMaker Pipeline ⭐
- **Enterprise:** Scheduled ETL → Glue → S3 → SageMaker 🏢

**Last Updated:** November 4, 2025
