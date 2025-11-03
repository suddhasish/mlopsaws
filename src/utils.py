"""
Utility functions for the MLOps project
"""

import os
import json
import yaml
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_config(config_path='config/config.yaml'):
    """Load configuration from YAML file"""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def save_json(data, filepath):
    """Save data as JSON file"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    logger.info(f"Saved JSON to {filepath}")


def load_json(filepath):
    """Load data from JSON file"""
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data


def get_timestamp():
    """Get current timestamp as string"""
    return datetime.now().strftime('%Y-%m-%d-%H-%M-%S')


def get_s3_uri(bucket, key):
    """Construct S3 URI"""
    return f"s3://{bucket}/{key}"


def parse_s3_uri(s3_uri):
    """Parse S3 URI into bucket and key"""
    if not s3_uri.startswith('s3://'):
        raise ValueError(f"Invalid S3 URI: {s3_uri}")
    
    parts = s3_uri[5:].split('/', 1)
    bucket = parts[0]
    key = parts[1] if len(parts) > 1 else ''
    
    return bucket, key


def create_experiment_name(base_name='diabetes-classification'):
    """Create unique experiment name with timestamp"""
    timestamp = get_timestamp()
    return f"{base_name}-{timestamp}"


class MetricsLogger:
    """Logger for tracking metrics"""
    
    def __init__(self, log_file='metrics.json'):
        self.log_file = log_file
        self.metrics = []
    
    def log(self, metrics, step=None, timestamp=None):
        """Log metrics"""
        if timestamp is None:
            timestamp = get_timestamp()
        
        entry = {
            'timestamp': timestamp,
            'step': step,
            'metrics': metrics
        }
        
        self.metrics.append(entry)
        
        # Save to file
        save_json(self.metrics, self.log_file)
    
    def get_latest(self):
        """Get latest metrics"""
        if self.metrics:
            return self.metrics[-1]
        return None
    
    def get_all(self):
        """Get all metrics"""
        return self.metrics


if __name__ == '__main__':
    # Test utilities
    logger.info("Testing utilities...")
    
    # Test timestamp
    timestamp = get_timestamp()
    logger.info(f"Timestamp: {timestamp}")
    
    # Test S3 URI
    uri = get_s3_uri('my-bucket', 'my-key/file.txt')
    logger.info(f"S3 URI: {uri}")
    
    bucket, key = parse_s3_uri(uri)
    logger.info(f"Parsed - Bucket: {bucket}, Key: {key}")
    
    # Test experiment name
    exp_name = create_experiment_name()
    logger.info(f"Experiment name: {exp_name}")
    
    logger.info("Utilities test completed")
