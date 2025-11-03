# Quick Start Guide

## 🚀 Quick Start (2-Day Learning Path)

### Day 1: Foundation & Pipeline (6-8 hours)

#### Morning (3-4 hours): Setup & Data Processing

1. **Initial Setup** (30 mins)
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Configure AWS
   aws configure
   ```

2. **Update Configuration** (15 mins)
   - Edit `config/config.yaml`
   - Add your AWS account details
   - Set S3 bucket name
   - Configure SageMaker role

3. **Data Preparation** (1 hour)
   ```bash
   # Download dataset
   python src/processing/download_data.py
   
   # Upload to S3
   aws s3 cp data/raw/diabetes.csv s3://YOUR-BUCKET/diabetes-project/data/raw/
   ```

4. **Explore Data** (1-2 hours)
   - Open `notebooks/01_data_exploration.ipynb`
   - Understand the dataset
   - Review preprocessing logic in `src/processing/preprocessing.py`

#### Afternoon (3-4 hours): Training & Evaluation

5. **Training Pipeline** (2 hours)
   - Review `src/training/train.py`
   - Understand hyperparameters in `config/config.yaml`
   - Study pipeline in `pipelines/training_pipeline.py`

6. **Execute Pipeline** (1 hour)
   ```bash
   # Create and run pipeline
   python pipelines/training_pipeline.py --config config/config.yaml --execute
   ```
   
   Monitor in SageMaker Console while it runs (~20-30 mins)

7. **Review Results** (30 mins)
   - Check model metrics in S3
   - Review evaluation reports
   - Approve model in Model Registry

---

### Day 2: Deployment & Operations (6-8 hours)

#### Morning (3-4 hours): Deployment & Testing

8. **Model Deployment** (1 hour)
   ```bash
   # Deploy approved model
   python src/deployment/deploy.py \
       --config config/config.yaml \
       --endpoint-name diabetes-classifier \
       --enable-autoscaling \
       --test
   ```

9. **Test Endpoint** (1 hour)
   - Review `src/deployment/inference.py`
   - Test with sample data
   - Understand auto-scaling configuration

10. **Explore Monitoring** (1-2 hours)
    - Study `src/monitoring/model_monitor.py`
    - Understand drift detection in `src/monitoring/drift_detection.py`

#### Afternoon (3-4 hours): CI/CD & Best Practices

11. **Setup Monitoring** (1-2 hours)
    ```bash
    # Enable data capture
    python src/monitoring/model_monitor.py \
        --endpoint-name diabetes-classifier \
        --enable-capture
    
    # Create baseline
    python src/monitoring/model_monitor.py \
        --endpoint-name diabetes-classifier \
        --baseline-data s3://YOUR-BUCKET/diabetes-project/data/train/train.csv \
        --create-baseline
    
    # Create monitoring schedule
    python src/monitoring/model_monitor.py \
        --endpoint-name diabetes-classifier \
        --create-schedule
    ```

12. **CI/CD Setup** (1 hour)
    - Review `.github/workflows/mlops_pipeline.yaml`
    - Understand automation workflow
    - Setup GitHub repository (if using)

13. **Review & Cleanup** (1 hour)
    - Review all components
    - Clean up resources
    - Plan next steps

---

## 📝 Key Files to Review

### Must Read (Day 1)
- `README.md` - Complete project overview
- `SETUP.md` - Detailed setup instructions
- `config/config.yaml` - Configuration settings
- `src/processing/preprocessing.py` - Data preprocessing
- `src/training/train.py` - Model training
- `pipelines/training_pipeline.py` - ML pipeline

### Must Read (Day 2)
- `src/deployment/deploy.py` - Model deployment
- `src/deployment/inference.py` - Inference logic
- `src/monitoring/model_monitor.py` - Monitoring setup
- `src/monitoring/drift_detection.py` - Drift detection
- `.github/workflows/mlops_pipeline.yaml` - CI/CD workflow

---

## 🎯 Learning Objectives Checklist

### Day 1
- [ ] Understand MLOps workflow
- [ ] Configure AWS services
- [ ] Process data with SageMaker Processing Jobs
- [ ] Train models with SageMaker Training Jobs
- [ ] Evaluate model performance
- [ ] Use SageMaker Model Registry
- [ ] Build SageMaker Pipelines

### Day 2
- [ ] Deploy models to endpoints
- [ ] Configure auto-scaling
- [ ] Test inference
- [ ] Setup model monitoring
- [ ] Detect data drift
- [ ] Understand CI/CD for ML
- [ ] Implement retraining triggers

---

## 💡 Tips for Success

1. **Take Breaks**: This is intensive material. Take 10-min breaks every hour.

2. **Hands-On Practice**: Run every command yourself. Don't just read.

3. **Monitor Costs**: Use `ml.t2.medium` for endpoints to minimize costs.

4. **Ask Questions**: Use comments in code to note your questions.

5. **Document Learning**: Keep notes on what you learned each hour.

6. **Clean Up**: Delete endpoints after testing to avoid charges:
   ```bash
   aws sagemaker delete-endpoint --endpoint-name diabetes-classifier
   ```

---

## 🔍 Common Commands Reference

### AWS CLI
```bash
# List SageMaker resources
aws sagemaker list-training-jobs --max-results 5
aws sagemaker list-endpoints
aws sagemaker list-monitoring-schedules

# S3 operations
aws s3 ls s3://YOUR-BUCKET/diabetes-project/
aws s3 cp file.txt s3://YOUR-BUCKET/path/

# View logs
aws logs tail /aws/sagemaker/TrainingJobs --follow
```

### Python Scripts
```bash
# Data processing
python src/processing/download_data.py
python src/processing/preprocessing.py

# Training
python src/training/train.py

# Deployment
python src/deployment/deploy.py --config config/config.yaml

# Monitoring
python src/monitoring/model_monitor.py --help
```

---

## 🎓 After Completion

### Immediate Next Steps
1. Review metrics and model performance
2. Experiment with different hyperparameters
3. Try batch inference
4. Implement A/B testing

### Advanced Topics
1. Add model explainability (SHAP, LIME)
2. Implement multi-model endpoints
3. Add blue/green deployment
4. Create custom containers
5. Integrate with Lambda for serverless inference

---

## 📚 Additional Resources

- [AWS SageMaker Workshop](https://sagemaker-workshop.com/)
- [MLOps Best Practices](https://ml-ops.org/)
- [SageMaker Examples](https://github.com/aws/amazon-sagemaker-examples)

---

## ⏱️ Time Budget

| Activity | Time | Priority |
|----------|------|----------|
| Setup & Configuration | 1 hour | High |
| Data Processing | 2 hours | High |
| Training Pipeline | 2 hours | High |
| Model Deployment | 2 hours | High |
| Monitoring Setup | 2 hours | Medium |
| CI/CD Understanding | 1 hour | Medium |
| Testing & Validation | 2 hours | High |
| Documentation Review | 2 hours | Low |

**Total: ~14 hours** (7 hours per day)

---

Good luck with your MLOps journey! 🚀
