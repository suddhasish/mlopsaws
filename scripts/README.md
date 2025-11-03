# 🔧 Automation Scripts

This directory contains automation scripts to streamline the MLOps setup and validation process.

## 📁 Scripts

### `validate-setup.ps1`
**Purpose:** Validates complete MLOps environment setup before running pipelines

**Usage:**
```powershell
.\scripts\validate-setup.ps1 -Environment dev
```

**What it checks:**
- ✅ Config.yaml exists and has no placeholder values
- ✅ Data directories created
- ✅ Python virtual environment exists
- ✅ AWS credentials configured
- ✅ Terraform infrastructure deployed
- ✅ Python dependencies installed
- ✅ Required Python files present
- ✅ requirements.txt exists

**Output:**
- Green ✅ - Check passed
- Yellow ⚠️ - Warning (can proceed)
- Red ❌ - Error (must fix)

**When to run:**
- After infrastructure deployment
- Before running ML pipeline
- When troubleshooting setup issues

---

## 🔗 Related Scripts

### `infrastructure/scripts/update-config.ps1`
**Purpose:** Auto-updates `config/config.yaml` from Terraform outputs

**Usage:**
```powershell
.\infrastructure\scripts\update-config.ps1 -Environment dev
```

**What it does:**
- Extracts Terraform output values
- Replaces placeholder values in config.yaml
- Updates: AWS Account ID, S3 bucket, SageMaker role, Model Registry, SNS topics
- Shows summary of updated values

**When to run:**
- Automatically called by `deploy-infrastructure.ps1`
- Manually if config.yaml needs updating after Terraform changes

---

### `infrastructure/scripts/deploy-infrastructure.ps1`
**Purpose:** One-command infrastructure deployment

**Usage:**
```powershell
.\infrastructure\scripts\deploy-infrastructure.ps1 -Environment dev -Action all
```

**What it does:**
- Initializes Terraform
- Creates execution plan
- Deploys AWS infrastructure
- **Automatically calls update-config.ps1**
- Shows next steps

---

## 🎯 Recommended Workflow

```powershell
# 1. Deploy infrastructure (includes auto-config)
cd infrastructure\scripts
.\deploy-infrastructure.ps1 -Environment dev -Action all

# 2. Validate setup
cd ..\..
.\scripts\validate-setup.ps1

# 3. If validation passes, run ML pipeline
python pipelines\training_pipeline.py --environment dev --execute
```

---

## 💡 Troubleshooting

**Issue:** "Config.yaml contains placeholder values"
```powershell
# Solution: Run update-config script
.\infrastructure\scripts\update-config.ps1 -Environment dev
```

**Issue:** "AWS credentials not configured"
```powershell
# Solution: Configure AWS CLI
aws configure --profile mlops-dev
```

**Issue:** "Terraform infrastructure not deployed"
```powershell
# Solution: Deploy infrastructure
cd infrastructure\scripts
.\deploy-infrastructure.ps1 -Environment dev -Action all
```

**Issue:** "Python dependencies missing"
```powershell
# Solution: Install dependencies
pip install -r requirements.txt
```

---

## 📚 Documentation

For complete setup instructions, see:
- **END_TO_END_SETUP_GUIDE.md** - Complete walkthrough
- **FINAL_VALIDATION.md** - Verification report
- **infrastructure/docs/DEPLOYMENT_GUIDE.md** - Infrastructure details

---

**Last Updated:** November 4, 2025  
**Scripts:** 3 automation scripts  
**Purpose:** Zero-manual-step MLOps deployment
