"""
SageMaker Pipeline Step - Track Experiment
This script is executed as a processing step to log experiment data to SageMaker Experiments
"""

import argparse
import json
import os
import sys
import logging
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.monitoring.experiment_tracker import ExperimentTracker

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def track_training_experiment(args):
    """
    Track training experiment in SageMaker Experiments
    
    Args:
        args: Command-line arguments with training metadata
    """
    logger.info("="*80)
    logger.info("TRACKING EXPERIMENT TO SAGEMAKER EXPERIMENTS")
    logger.info("="*80)
    
    # Load evaluation results
    logger.info(f"Loading evaluation results from: {args.evaluation_results}")
    with open(args.evaluation_results, 'r') as f:
        eval_results = json.load(f)
    
    logger.info(f"Evaluation results loaded: {eval_results}")
    
    # Initialize experiment tracker
    logger.info(f"Experiment name: {args.experiment_name}")
    logger.info(f"Training job name: {args.training_job_name}")
    
    tracker = ExperimentTracker(
        experiment_name=args.experiment_name,
        run_name=args.training_job_name
    )
    
    # Start run
    tracker.start_run()
    
    # Extract and log hyperparameters from training job name or evaluation results
    # Hyperparameters are already logged during training, but we can add metadata here
    if 'hyperparameters' in eval_results:
        logger.info("Logging hyperparameters...")
        tracker.log_parameters(eval_results['hyperparameters'])
    
    # Log evaluation metrics
    if 'metrics' in eval_results:
        logger.info("Logging evaluation metrics...")
        metrics = eval_results['metrics']
        
        # Log all metrics
        tracker.log_metrics(metrics)
        
        logger.info(f"Metrics logged:")
        for metric_name, metric_value in metrics.items():
            logger.info(f"  {metric_name}: {metric_value:.4f}")
    
    # Log model artifact
    logger.info(f"Logging model artifact: {args.model_artifact_uri}")
    tracker.log_artifact(args.model_artifact_uri, 'model')
    
    # Print experiment summary
    tracker.print_experiment_summary()
    
    # Save tracking confirmation
    output_dir = '/opt/ml/processing/output'
    os.makedirs(output_dir, exist_ok=True)
    
    tracking_summary = {
        'experiment_name': args.experiment_name,
        'run_name': args.training_job_name,
        'model_artifact': args.model_artifact_uri,
        'metrics': eval_results.get('metrics', {}),
        'timestamp': datetime.now().isoformat(),
        'status': 'success'
    }
    
    with open(os.path.join(output_dir, 'experiment_tracking.json'), 'w') as f:
        json.dump(tracking_summary, f, indent=2)
    
    logger.info("="*80)
    logger.info("✅ EXPERIMENT TRACKING COMPLETED SUCCESSFULLY")
    logger.info("="*80)
    logger.info(f"View in SageMaker Console:")
    logger.info(f"  SageMaker → Experiments → {args.experiment_name}")
    logger.info("="*80)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Track experiment in SageMaker Experiments')
    
    parser.add_argument(
        '--training-job-name',
        type=str,
        required=True,
        help='SageMaker training job name (used as run name)'
    )
    parser.add_argument(
        '--model-artifact-uri',
        type=str,
        required=True,
        help='S3 URI of trained model artifact'
    )
    parser.add_argument(
        '--evaluation-results',
        type=str,
        required=True,
        help='Path to evaluation_results.json file'
    )
    parser.add_argument(
        '--experiment-name',
        type=str,
        default='diabetes-classification-experiments',
        help='SageMaker Experiment name'
    )
    
    args = parser.parse_args()
    
    try:
        track_training_experiment(args)
    except Exception as e:
        logger.error(f"❌ Failed to track experiment: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
