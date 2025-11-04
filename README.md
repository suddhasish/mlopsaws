# End-to-End MLOps Project: Diabetes Classification on AWS SageMaker

## 🎯 Project Overview

This is a **production-ready MLOps mini project** that demonstrates industry best practices for building, deploying, and maintaining machine learning models on AWS SageMaker. You'll build a complete ML pipeline for diabetes classification using the Pima Indians Diabetes dataset.

**Timeline:** 2 Days  
**Difficulty Level:** Intermediate  
**Prerequisites:** Basic Python, AWS Account, Understanding of ML concepts

---

## 🏆 What You Will Achieve

By completing this project, you will:

### ✅ Day 1 Objectives
1. **Understand MLOps Fundamentals**
   - Learn the complete ML lifecycle from data to deployment
   - Understand the importance of automation and monitoring

2. **Data Engineering**
   - Implement data ingestion from S3
   - Build SageMaker Processing Jobs for data preprocessing
   - Create reusable data pipelines

3. **Feature Engineering**
   - Implement feature scaling and transformations
   - Set up SageMaker Feature Store (optional)
   - Handle missing values and outliers

4. **Model Training**
   - Train XGBoost classification model
   - Implement hyperparameter tuning
   - Use SageMaker Training Jobs

### ✅ Day 2 Objectives
5. **Model Evaluation & Registry**
   - Calculate classification metrics (Accuracy, Precision, Recall, F1, ROC-AUC)
   - Register models in SageMaker Model Registry
   - Implement model approval workflow

6. **Model Deployment**
   - Deploy to real-time SageMaker endpoint
   - Configure auto-scaling
   - Test endpoint inference

7. **CI/CD Pipeline**
   - Orchestrate with SageMaker Pipelines
   - Set up GitHub Actions for automation
   - Implement automated testing

8. **Monitoring & Retraining**
   - Configure SageMaker Model Monitor
   - Detect data drift and model degradation
   - Set up CloudWatch alerts
   - Implement automated retraining triggers

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Data Source (S3)                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              SageMaker Processing Job                            │
│         (Data Validation & Preprocessing)                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Feature Store (Optional)                            │
│         (Feature Registry & Versioning)                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              SageMaker Training Job                              │
│         (XGBoost Classifier + HPO)                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Model Evaluation                                    │
│         (Metrics: Accuracy, F1, ROC-AUC)                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                    ┌────┴────┐
                    │ Approve?│
                    └────┬────┘
                         │ YES
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Model Registry                                      │
│         (Versioning & Approval Status)                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              SageMaker Endpoint                                  │
│         (Real-time Inference + Auto-scaling)                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Model Monitor                                       │
│         (Data Drift, Model Quality, Bias)                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                    ┌────┴────┐
                    │  Drift? │
                    └────┬────┘
                         │ YES
                         ▼
              ┌─────────────────────┐
              │  Trigger Retraining │
              └─────────────────────┘
```

---

## 📁 Project Structure

```
mlops-aws-sagemaker/
│
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── config/
│   ├── config.yaml                   # Project configuration
│   └── aws_config.yaml               # AWS-specific settings
│
├── data/
│   ├── raw/                          # Raw dataset
│   └── processed/                    # Processed data
│
├── src/
│   ├── processing/
│   │   ├── preprocessing.py          # Data preprocessing script
│   │   └── feature_engineering.py    # Feature engineering
│   │
│   ├── training/
│   │   ├── train.py                  # Training script
│   │   └── hyperparameters.py        # Hyperparameter configuration
│   │
│   ├── evaluation/
│   │   ├── evaluate.py               # Model evaluation script
│   │   └── metrics.py                # Custom metrics
│   │
│   ├── deployment/
│   │   ├── deploy.py                 # Deployment script
│   │   ├── inference.py              # Custom inference handler
│   │   └── autoscaling.py            # Auto-scaling configuration
│   │
│   └── monitoring/
│       ├── model_monitor.py          # Model monitoring setup
│       ├── drift_detection.py        # Drift detection logic
│       └── cloudwatch_alerts.py      # CloudWatch alerts
│
├── pipelines/
│   ├── training_pipeline.py          # SageMaker training pipeline
│   ├── inference_pipeline.py         # Inference pipeline
│   └── retraining_pipeline.py        # Automated retraining
│
├── notebooks/
│   ├── 01_data_exploration.ipynb     # EDA notebook
│   ├── 02_local_testing.ipynb        # Local model testing
│   └── 03_endpoint_testing.ipynb     # Endpoint testing
│
├── tests/
│   ├── test_preprocessing.py         # Unit tests
│   ├── test_training.py
│   └── test_deployment.py
│
└── .github/
    └── workflows/
        └── mlops_pipeline.yaml       # GitHub Actions CI/CD
```

---

## 🚀 Getting Started

### 📖 **THE ONLY GUIDE YOU NEED**

**👉 [docs/COMPLETE_SETUP_GUIDE.md](docs/COMPLETE_SETUP_GUIDE.md) ⭐**

This single comprehensive guide contains **everything** you need:

✅ **100% Complete** - No missing steps  
✅ **Clear Labels** - Manual 🔴 vs Automated 🟢 steps  
✅ **GitHub Actions** - Fully automated CI/CD  
✅ **PowerShell Scripts** - Local alternative explained  
✅ **Troubleshooting** - Common issues solved  
✅ **Production Ready** - Deploy to prod with approval gates  

**Time:** 2-3 hours (one-time setup)  
**Result:** Automated MLOps infrastructure on AWS

---

### Quick Overview (Read Full Guide for Details)

**Step 1: Manual Setup (1 hour)**
- Create AWS account + OIDC provider
- Configure GitHub repository + secrets
- Update configuration files

**Step 2: Automated Deployment (40 minutes)**
- Push to GitHub → GitHub Actions deploys infrastructure
- Automated MLOps pipeline trains and deploys model
- Monitoring and alerts configured automatically

**Step 3: Production (Manual approval)**
- Review deployment plan
- Approve production deployment
- Production endpoint live!

---

### Prerequisites Summary

**Before starting, you need:**

1. **AWS Account** (free tier available, but SageMaker costs ~$30-50/month)
2. **GitHub Account** (free)
3. **Local Tools** (Git, Python 3.8+, text editor)

**Everything else is automated!**

---

### What Gets Automated

After initial setup, GitHub Actions automatically:

- ✅ Validates all code changes
- ✅ Deploys infrastructure (Terraform)
- ✅ Uploads data to S3
- ✅ Trains ML models
- ✅ Evaluates model performance
- ✅ Deploys to endpoints
- ✅ Configures monitoring
- ✅ Sends alerts
- ✅ Generates cost estimates

**You just push code and watch it deploy! 🚀**

---

## 📚 Day 1: Foundation & Training

### Step 1: Data Preparation (2 hours)

1. **Download the Pima Indians Diabetes Dataset**
   ```bash
   python src/processing/download_data.py
   ```

2. **Explore the Data**
   - Open `notebooks/01_data_exploration.ipynb`
   - Understand the features and target variable
   - Identify data quality issues

3. **Run Data Processing**
   ```bash
   python pipelines/training_pipeline.py --step preprocessing
   ```

**Learning Outcomes:**
- Understand SageMaker Processing Jobs
- Learn data validation techniques
- Handle missing values and outliers

---

### Step 2: Feature Engineering (1.5 hours)

1. **Feature Transformation**
   - Standardization using StandardScaler
   - Feature selection based on correlation

2. **Optional: Feature Store Setup**
   ```bash
   python src/processing/feature_engineering.py --use-feature-store
   ```

**Learning Outcomes:**
- Build reusable feature pipelines
- Understand Feature Store benefits
- Implement feature versioning

---

### Step 3: Model Training (2 hours)

1. **Configure Training Job**
   - Edit `config/config.yaml` for hyperparameters
   - Choose instance type (ml.m5.xlarge recommended)

2. **Run Training**
   ```bash
   python pipelines/training_pipeline.py --step training
   ```

3. **Monitor Training**
   - Check SageMaker console for training job status
   - Review CloudWatch logs

**Learning Outcomes:**
- Use SageMaker built-in algorithms (XGBoost)
- Implement hyperparameter tuning
- Understand distributed training

---

### Step 4: Model Evaluation (1.5 hours)

1. **Evaluate Model Performance**
   ```bash
   python pipelines/training_pipeline.py --step evaluation
   ```

2. **Review Metrics**
   - Accuracy
   - Precision & Recall
   - F1 Score
   - ROC-AUC
   - Confusion Matrix

3. **Register Model**
   ```bash
   python src/evaluation/register_model.py
   ```

**Learning Outcomes:**
- Implement comprehensive evaluation
- Use SageMaker Model Registry
- Set approval workflows

---

## 📚 Day 2: Deployment & Operations

### Step 5: Model Deployment (2 hours)

1. **Deploy to Endpoint**
   ```bash
   python src/deployment/deploy.py --model-name diabetes-classifier-v1
   ```

2. **Configure Auto-scaling**
   ```bash
   python src/deployment/autoscaling.py --min-instances 1 --max-instances 5
   ```

3. **Test Inference**
   ```bash
   python src/deployment/test_endpoint.py
   ```

**Learning Outcomes:**
- Deploy real-time endpoints
- Configure auto-scaling policies
- Implement custom inference logic

---

### Step 6: CI/CD Pipeline (2 hours)

1. **Review SageMaker Pipeline**
   - Open `pipelines/training_pipeline.py`
   - Understand pipeline orchestration

2. **Set Up GitHub Actions**
   - Configure secrets in GitHub
   - Push code to trigger pipeline

3. **Automated Testing**
   ```bash
   pytest tests/
   ```

**Learning Outcomes:**
- Build end-to-end ML pipelines
- Automate with GitHub Actions
- Implement testing strategies

---

### Step 7: Monitoring & Drift Detection (2 hours)

1. **Enable Model Monitor**
   ```bash
   python src/monitoring/model_monitor.py --endpoint-name diabetes-classifier
   ```

2. **Configure Data Quality Monitoring**
   - Baseline creation
   - Schedule monitoring jobs

3. **Set Up Alerts**
   ```bash
   python src/monitoring/cloudwatch_alerts.py
   ```

**Learning Outcomes:**
- Detect data drift
- Monitor model quality
- Set up automated alerts

---

### Step 8: Retraining Pipeline (1 hour)

1. **Configure Retraining Trigger**
   ```bash
   python pipelines/retraining_pipeline.py --setup
   ```

2. **Test Retraining**
   - Simulate drift
   - Verify automatic retraining

**Learning Outcomes:**
- Implement automated retraining
- Handle model versioning
- Manage continuous improvement

---

## 🎓 Industry Best Practices Implemented

### 1. **Version Control**
- Git for code versioning
- Model versioning in SageMaker Model Registry
- Data versioning with S3 versioning

### 2. **Infrastructure as Code**
- Configuration files for reproducibility
- Parameterized pipelines
- Environment management

### 3. **Testing**
- Unit tests for preprocessing
- Integration tests for pipelines
- Endpoint validation tests

### 4. **Monitoring**
- Real-time model monitoring
- Data quality checks
- Performance tracking

### 5. **Security**
- IAM roles and policies
- Encryption at rest and in transit
- Secrets management

### 6. **Cost Optimization**
- Auto-scaling endpoints
- Spot instances for training
- Scheduled monitoring jobs

### 7. **Documentation**
- Comprehensive README
- Code comments
- Architecture diagrams

---

## 🔧 Configuration

### Key Configuration Files

**`config/config.yaml`**
```yaml
project:
  name: diabetes-classification
  region: us-east-1
  
data:
  s3_bucket: mlops-diabetes-project
  raw_data_prefix: data/raw
  processed_data_prefix: data/processed
  
training:
  instance_type: ml.m5.xlarge
  instance_count: 1
  max_runtime: 3600
  
hyperparameters:
  max_depth: 5
  eta: 0.2
  objective: binary:logistic
  num_round: 100
```

---

## 📊 Expected Results

After completing this project, you should achieve:

- **Model Performance:**
  - Accuracy: ~75-80%
  - F1 Score: ~0.70-0.75
  - ROC-AUC: ~0.80-0.85

- **Operational Metrics:**
  - Endpoint latency: <100ms
  - Pipeline execution time: ~30 minutes
  - Monitoring frequency: Hourly

---

## 🐛 Troubleshooting

### Common Issues

1. **IAM Permission Errors**
   - Ensure SageMaker execution role has S3 access
   - Check CloudWatch Logs permissions

2. **Endpoint Deployment Failures**
   - Verify instance type availability in region
   - Check model artifacts in S3

3. **Pipeline Execution Errors**
   - Review CloudWatch logs
   - Validate input data format

---

## 📖 Learning Resources

- [AWS SageMaker Documentation](https://docs.aws.amazon.com/sagemaker/)
- [SageMaker Pipelines Guide](https://docs.aws.amazon.com/sagemaker/latest/dg/pipelines.html)
- [MLOps Best Practices](https://ml-ops.org/)
- [Model Monitoring Guide](https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor.html)

---

## 🎯 Next Steps After Completion

1. **Enhance the Project:**
   - Try different algorithms (Neural Networks, Random Forest)
   - Implement A/B testing
   - Add batch inference

2. **Production Readiness:**
   - Add comprehensive logging
   - Implement blue/green deployment
   - Set up disaster recovery

3. **Advanced MLOps:**
   - Multi-model endpoints
   - Model explainability (SHAP, LIME)
   - Advanced drift detection

---

## 📝 License

This project is for educational purposes.

---

## 👨‍💼 About This Project

This mini project is designed as a **comprehensive learning experience** for aspiring MLOps engineers. It covers the entire ML lifecycle and follows AWS Well-Architected Framework principles.

**Skills You'll Gain:**
- AWS SageMaker expertise
- MLOps pipeline development
- Production ML deployment
- Model monitoring and maintenance
- CI/CD for ML systems

**Perfect for:**
- Data Scientists transitioning to MLOps
- ML Engineers seeking AWS certification
- Teams building ML platforms
- Portfolio/resume projects

---

## 🤝 Support

For questions or issues:
1. Check the troubleshooting section
2. Review CloudWatch logs
3. Consult AWS SageMaker documentation

---

**Happy Learning! 🚀**

*Remember: MLOps is not just about models, it's about building sustainable, scalable, and maintainable ML systems.*
