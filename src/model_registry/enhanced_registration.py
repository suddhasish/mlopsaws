"""
Enhanced Model Registration with Production-Grade Metadata
Tracks git commit, data version, and comprehensive lineage
"""

import os
import json
import boto3
import subprocess
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedModelRegistry:
    """Production-grade model registration with full metadata tracking"""
    
    def __init__(self, region: str = "us-east-1"):
        self.sm_client = boto3.client('sagemaker', region_name=region)
    
    def get_git_commit_sha(self) -> str:
        """Get current git commit SHA"""
        try:
            sha = subprocess.check_output(
                ['git', 'rev-parse', 'HEAD'], 
                stderr=subprocess.STDOUT
            ).decode('utf-8').strip()
            return sha
        except Exception as e:
            logger.warning(f"Could not get git SHA: {e}")
            return os.getenv('GITHUB_SHA', 'unknown')
    
    def get_git_branch(self) -> str:
        """Get current git branch"""
        try:
            branch = subprocess.check_output(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                stderr=subprocess.STDOUT
            ).decode('utf-8').strip()
            return branch
        except Exception:
            return os.getenv('GITHUB_REF_NAME', 'unknown')
    
    def register_model(
        self,
        model_package_group_name: str,
        model_data_url: str,
        image_uri: str,
        metrics: Dict[str, float],
        training_job_name: str,
        model_version: str,
        data_version: str,
        feature_schema: Dict[str, Any],
        approval_status: str = "PendingManualApproval"
    ) -> str:
        """
        Register model with comprehensive metadata
        
        Args:
            model_package_group_name: Registry group name
            model_data_url: S3 path to model.tar.gz
            image_uri: Container image URI
            metrics: Evaluation metrics dict
            training_job_name: SageMaker training job name
            model_version: Semantic version (e.g., "1.2.3")
            data_version: Dataset version identifier
            feature_schema: Expected input features
            approval_status: Initial status
        
        Returns:
            model_package_arn: ARN of registered model
        """
        
        # Get git metadata
        git_sha = self.get_git_commit_sha()
        git_branch = self.get_git_branch()
        
        logger.info(f"Registering model version {model_version}")
        logger.info(f"Git commit: {git_sha}")
        logger.info(f"Git branch: {git_branch}")
        logger.info(f"Data version: {data_version}")
        
        # Prepare metadata
        customer_metadata = {
            # Version info
            "model_version": model_version,
            "data_version": data_version,
            "git_commit_sha": git_sha,
            "git_branch": git_branch,
            
            # Training info
            "training_job_name": training_job_name,
            "registration_timestamp": datetime.utcnow().isoformat(),
            "registered_by": os.getenv('GITHUB_ACTOR', os.getenv('USER', 'unknown')),
            
            # Metrics
            "accuracy": str(metrics.get("accuracy", 0)),
            "precision": str(metrics.get("precision", 0)),
            "recall": str(metrics.get("recall", 0)),
            "f1_score": str(metrics.get("f1_score", 0)),
            "roc_auc": str(metrics.get("roc_auc", 0)),
            
            # Schema info
            "feature_count": str(len(feature_schema.get("features", []))),
            "feature_names": json.dumps(feature_schema.get("features", [])),
            "input_format": feature_schema.get("format", "csv"),
            "output_format": "json"
        }
        
        # Create model package
        response = self.sm_client.create_model_package(
            ModelPackageGroupName=model_package_group_name,
            ModelPackageDescription=f"Diabetes classifier {model_version} - Git: {git_sha[:7]}",
            ModelApprovalStatus=approval_status,
            
            InferenceSpecification={
                "Containers": [{
                    "Image": image_uri,
                    "ModelDataUrl": model_data_url
                }],
                "SupportedContentTypes": ["text/csv", "application/json"],
                "SupportedResponseMIMETypes": ["application/json"]
            },
            
            CustomerMetadataProperties=customer_metadata,
            
            Tags=[
                {"Key": "ModelVersion", "Value": model_version},
                {"Key": "GitCommit", "Value": git_sha},
                {"Key": "GitBranch", "Value": git_branch},
                {"Key": "DataVersion", "Value": data_version},
                {"Key": "Project", "Value": "diabetes-classifier"},
                {"Key": "Environment", "Value": "registered"},
                {"Key": "Accuracy", "Value": str(metrics.get("accuracy", 0))}
            ]
        )
        
        model_package_arn = response["ModelPackageArn"]
        logger.info(f"✓ Model registered successfully: {model_package_arn}")
        
        return model_package_arn
    
    def update_approval_status(
        self,
        model_package_arn: str,
        new_status: str,
        environment: str = None
    ):
        """
        Update model approval status
        
        Statuses: PendingManualApproval → Approved → Production
        """
        logger.info(f"Updating model status to: {new_status}")
        
        self.sm_client.update_model_package(
            ModelPackageArn=model_package_arn,
            ModelApprovalStatus=new_status
        )
        
        # Add approval tags
        tags = [
            {"Key": "ApprovalStatus", "Value": new_status},
            {"Key": "ApprovalDate", "Value": datetime.utcnow().isoformat()}
        ]
        
        if environment:
            tags.append({"Key": "DeployedEnvironment", "Value": environment})
        
        self.sm_client.add_tags(
            ResourceArn=model_package_arn,
            Tags=tags
        )
        
        logger.info(f"✓ Model status updated to {new_status}")
    
    def get_model_metadata(self, model_package_arn: str) -> Dict[str, Any]:
        """Get full metadata for a registered model"""
        
        response = self.sm_client.describe_model_package(
            ModelPackageName=model_package_arn
        )
        
        metadata = response.get("CustomerMetadataProperties", {})
        
        return {
            "model_package_arn": model_package_arn,
            "version": metadata.get("model_version"),
            "git_commit": metadata.get("git_commit_sha"),
            "git_branch": metadata.get("git_branch"),
            "data_version": metadata.get("data_version"),
            "training_job": metadata.get("training_job_name"),
            "registered_by": metadata.get("registered_by"),
            "registration_date": metadata.get("registration_timestamp"),
            "approval_status": response.get("ModelApprovalStatus"),
            "metrics": {
                "accuracy": float(metadata.get("accuracy", 0)),
                "precision": float(metadata.get("precision", 0)),
                "recall": float(metadata.get("recall", 0)),
                "f1_score": float(metadata.get("f1_score", 0)),
                "roc_auc": float(metadata.get("roc_auc", 0))
            }
        }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced model registration')
    parser.add_argument('--model-package-group', required=True, help='Model package group name')
    parser.add_argument('--model-data-url', required=True, help='S3 path to model.tar.gz')
    parser.add_argument('--image-uri', required=True, help='Container image URI')
    parser.add_argument('--metrics-file', required=True, help='Path to evaluation_results.json')
    parser.add_argument('--training-job-name', required=True, help='Training job name')
    parser.add_argument('--model-version', required=True, help='Model version (e.g., 1.0.0)')
    parser.add_argument('--data-version', default='v1.0', help='Data version')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    
    args = parser.parse_args()
    
    # Load metrics
    with open(args.metrics_file, 'r') as f:
        evaluation_data = json.load(f)
        metrics = evaluation_data['metrics']
    
    # Feature schema
    feature_schema = {
        "features": [
            "Pregnancies", "Glucose", "BloodPressure", "SkinThickness",
            "Insulin", "BMI", "DiabetesPedigreeFunction", "Age"
        ],
        "format": "csv"
    }
    
    # Register model
    registry = EnhancedModelRegistry(region=args.region)
    
    model_arn = registry.register_model(
        model_package_group_name=args.model_package_group,
        model_data_url=args.model_data_url,
        image_uri=args.image_uri,
        metrics=metrics,
        training_job_name=args.training_job_name,
        model_version=args.model_version,
        data_version=args.data_version,
        feature_schema=feature_schema
    )
    
    print(f"\n✓ Model registered: {model_arn}")
    print(f"Version: {args.model_version}")
    print(f"Status: PendingManualApproval")
