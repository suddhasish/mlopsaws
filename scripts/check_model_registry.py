"""
Check Model Registry Status
Quickly check what models exist in the Model Registry and their approval status
"""

import boto3
import sys
from datetime import datetime


def check_model_registry(
    model_package_group_name="diabetes-classifier-model-group", region="us-east-1"
):
    """Check Model Registry for models"""

    client = boto3.client("sagemaker", region_name=region)

    print(f"\n{'='*80}")
    print(f"Checking Model Registry: {model_package_group_name}")
    print(f"{'='*80}\n")

    try:
        # Check if model package group exists
        try:
            response = client.describe_model_package_group(
                ModelPackageGroupName=model_package_group_name
            )
            print(f"✓ Model Package Group exists")
            print(f"  Created: {response['CreationTime']}")
            print(f"  ARN: {response['ModelPackageGroupArn']}\n")
        except client.exceptions.ResourceNotFound:
            print(f"✗ Model Package Group '{model_package_group_name}' does not exist!")
            print(f"  Run the training pipeline first to create it.\n")
            return

        # List all model packages
        print(f"Listing all model packages...\n")

        response = client.list_model_packages(
            ModelPackageGroupName=model_package_group_name,
            SortBy="CreationTime",
            SortOrder="Descending",
            MaxResults=10,
        )

        if not response["ModelPackageSummaryList"]:
            print("✗ No models found in Model Registry!")
            print("\nPossible reasons:")
            print("  1. Training pipeline hasn't been executed yet")
            print(
                "  2. Models didn't meet quality thresholds (check evaluation metrics)"
            )
            print("  3. Pipeline failed during model registration step")
            print("\nNext steps:")
            print("  - Run: python pipelines/training_pipeline.py --execute")
            print("  - Check SageMaker Console > Pipelines for execution status")
            print("  - Review evaluation step metrics in pipeline execution")
            return

        print(f"Found {len(response['ModelPackageSummaryList'])} model(s):\n")
        print(f"{'#':<4} {'Status':<20} {'Version':<10} {'Created':<20}")
        print(f"{'-'*80}")

        approved_count = 0
        pending_count = 0
        rejected_count = 0

        for i, pkg in enumerate(response["ModelPackageSummaryList"], 1):
            status = pkg.get("ModelApprovalStatus", "Unknown")
            version = pkg.get("ModelPackageVersion", "N/A")
            created = pkg["CreationTime"].strftime("%Y-%m-%d %H:%M:%S")

            status_icon = {
                "Approved": "✓",
                "PendingManualApproval": "⏳",
                "Rejected": "✗",
            }.get(status, "?")

            print(f"{i:<4} {status_icon} {status:<18} {version:<10} {created:<20}")

            if status == "Approved":
                approved_count += 1
            elif status == "PendingManualApproval":
                pending_count += 1
            elif status == "Rejected":
                rejected_count += 1

            # Get detailed info
            try:
                details = client.describe_model_package(
                    ModelPackageName=pkg["ModelPackageArn"]
                )

                # Print metrics if available
                if "ModelMetrics" in details:
                    print(f"     ARN: {pkg['ModelPackageArn']}")
                    if "ModelQuality" in details.get("ModelMetrics", {}):
                        print(f"     Metrics available in Model Registry")
            except Exception:
                pass  # Silently skip if can't get details

        print(f"\n{'='*80}")
        print(f"Summary:")
        print(f"  ✓ Approved: {approved_count}")
        print(f"  ⏳ Pending: {pending_count}")
        print(f"  ✗ Rejected: {rejected_count}")
        print(f"  Total: {len(response['ModelPackageSummaryList'])}")
        print(f"{'='*80}\n")

        # Provide actionable next steps
        if approved_count > 0:
            print("✓ You can deploy approved models:")
            print(
                "  python src/deployment/deploy.py --config config/config.yaml --endpoint-name diabetes-classifier\n"
            )
        elif pending_count > 0:
            print("⏳ You have pending models. To approve them:")
            print("  1. Go to SageMaker Console > Model Registry")
            print(f"  2. Select model package group: {model_package_group_name}")
            print("  3. Click on a model version")
            print("  4. Click 'Update status' and select 'Approve'\n")
            print("  Or use AWS CLI:")
            for pkg in response["ModelPackageSummaryList"]:
                if pkg.get("ModelApprovalStatus") == "PendingManualApproval":
                    print(
                        f"  aws sagemaker update-model-package --model-package-arn {pkg['ModelPackageArn']} --model-approval-status Approved"
                    )
                    break
        else:
            print("No models available for deployment.")
            print("Check the training pipeline execution and evaluation metrics.\n")

    except Exception as e:
        print(f"✗ Error: {str(e)}\n")
        return 1

    return 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Check Model Registry Status")
    parser.add_argument(
        "--model-package-group",
        type=str,
        default="diabetes-classifier-model-group",
        help="Model package group name",
    )
    parser.add_argument("--region", type=str, default="us-east-1", help="AWS region")

    args = parser.parse_args()

    sys.exit(check_model_registry(args.model_package_group, args.region))
