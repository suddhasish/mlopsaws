"""
Quick script to add model metadata tracking to existing training pipeline
Adds git commit SHA, data version, and semantic versioning
"""

import os
import subprocess
from datetime import datetime


def get_git_commit_sha():
    """Get current git commit SHA"""
    try:
        sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.STDOUT
        ).decode("utf-8").strip()
        return sha
    except Exception:
        # Fallback to environment variable (GitHub Actions)
        return os.environ.get("GITHUB_SHA", "unknown")


def get_model_version():
    """
    Generate semantic version from git tags or environment
    Format: MAJOR.MINOR.PATCH
    """
    # Try to get from git tags
    try:
        # Get latest tag
        latest_tag = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"],
            stderr=subprocess.STDOUT
        ).decode("utf-8").strip()
        
        if latest_tag.startswith("v"):
            latest_tag = latest_tag[1:]
        
        return latest_tag
    except Exception:
        pass
    
    # Fallback: use date-based versioning
    date_str = datetime.utcnow().strftime("%Y.%m.%d")
    return f"{date_str}"


def get_data_version():
    """
    Get data version from environment or config
    """
    # Check environment variable first
    data_version = os.environ.get("DATA_VERSION")
    
    if not data_version:
        # Try to read from data version file
        version_file = "data/.version"
        if os.path.exists(version_file):
            with open(version_file, "r") as f:
                data_version = f.read().strip()
        else:
            # Default to date
            data_version = datetime.utcnow().strftime("v%Y%m%d")
    
    return data_version


def create_model_metadata():
    """
    Create comprehensive model metadata dictionary
    """
    metadata = {
        "model_version": get_model_version(),
        "git_commit_sha": get_git_commit_sha(),
        "data_version": get_data_version(),
        "training_date": datetime.utcnow().isoformat(),
        "environment": os.environ.get("ENVIRONMENT", "dev"),
        "trained_by": os.environ.get("GITHUB_ACTOR", os.environ.get("USER", "unknown")),
    }
    
    return metadata


# Example usage in training pipeline
if __name__ == "__main__":
    metadata = create_model_metadata()
    
    print("\n" + "="*60)
    print("MODEL METADATA")
    print("="*60)
    for key, value in metadata.items():
        print(f"{key:20s}: {value}")
    print("="*60 + "\n")
