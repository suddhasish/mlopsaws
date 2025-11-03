"""
Hyperparameter Configuration and Tuning Setup
"""

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class HyperparameterConfig:
    """
    Manages hyperparameter configurations for different scenarios
    """
    
    # Default hyperparameters
    DEFAULT_PARAMS = {
        'max_depth': 5,
        'eta': 0.2,
        'gamma': 4,
        'min_child_weight': 6,
        'subsample': 0.7,
        'colsample_bytree': 0.8,
        'objective': 'binary:logistic',
        'eval_metric': 'auc',
        'num_round': 100,
        'early_stopping_rounds': 10,
        'seed': 42
    }
    
    # Aggressive hyperparameters for faster training
    FAST_PARAMS = {
        'max_depth': 3,
        'eta': 0.3,
        'gamma': 0,
        'min_child_weight': 1,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'objective': 'binary:logistic',
        'eval_metric': 'auc',
        'num_round': 50,
        'early_stopping_rounds': 5,
        'seed': 42
    }
    
    # Conservative hyperparameters for better generalization
    CONSERVATIVE_PARAMS = {
        'max_depth': 3,
        'eta': 0.1,
        'gamma': 5,
        'min_child_weight': 10,
        'subsample': 0.6,
        'colsample_bytree': 0.6,
        'objective': 'binary:logistic',
        'eval_metric': 'auc',
        'num_round': 200,
        'early_stopping_rounds': 20,
        'seed': 42
    }
    
    @staticmethod
    def get_hyperparameters(config_type='default'):
        """Get hyperparameters based on configuration type"""
        if config_type == 'fast':
            return HyperparameterConfig.FAST_PARAMS.copy()
        elif config_type == 'conservative':
            return HyperparameterConfig.CONSERVATIVE_PARAMS.copy()
        else:
            return HyperparameterConfig.DEFAULT_PARAMS.copy()
    
    @staticmethod
    def get_hyperparameter_ranges():
        """
        Get hyperparameter ranges for SageMaker Hyperparameter Tuning
        """
        from sagemaker.tuner import (
            IntegerParameter,
            ContinuousParameter,
            CategoricalParameter
        )
        
        hyperparameter_ranges = {
            'max_depth': IntegerParameter(3, 10),
            'eta': ContinuousParameter(0.01, 0.5),
            'gamma': ContinuousParameter(0, 5),
            'min_child_weight': IntegerParameter(1, 10),
            'subsample': ContinuousParameter(0.5, 1.0),
            'colsample_bytree': ContinuousParameter(0.5, 1.0),
            'alpha': ContinuousParameter(0, 2),
            'lambda': ContinuousParameter(0, 2)
        }
        
        return hyperparameter_ranges
    
    @staticmethod
    def get_objective_metric():
        """
        Get objective metric configuration for hyperparameter tuning
        """
        objective_metric = {
            'Name': 'validation:auc',
            'Regex': 'validation-auc:([0-9\\.]+)'
        }
        
        return objective_metric
    
    @staticmethod
    def validate_hyperparameters(params):
        """Validate hyperparameter values"""
        logger.info("Validating hyperparameters...")
        
        issues = []
        
        # Check eta
        if 'eta' in params:
            if not 0 < params['eta'] <= 1:
                issues.append("eta should be between 0 and 1")
        
        # Check max_depth
        if 'max_depth' in params:
            if params['max_depth'] < 0:
                issues.append("max_depth should be positive")
        
        # Check subsample
        if 'subsample' in params:
            if not 0 < params['subsample'] <= 1:
                issues.append("subsample should be between 0 and 1")
        
        # Check colsample_bytree
        if 'colsample_bytree' in params:
            if not 0 < params['colsample_bytree'] <= 1:
                issues.append("colsample_bytree should be between 0 and 1")
        
        if issues:
            for issue in issues:
                logger.warning(f"Hyperparameter validation: {issue}")
            return False, issues
        
        logger.info("Hyperparameter validation passed")
        return True, []


class HyperparameterTuner:
    """
    Manages hyperparameter tuning jobs
    """
    
    def __init__(self, estimator, hyperparameter_ranges, objective_metric):
        self.estimator = estimator
        self.hyperparameter_ranges = hyperparameter_ranges
        self.objective_metric = objective_metric
        
    def create_tuner(self, max_jobs=10, max_parallel_jobs=2, strategy='Bayesian'):
        """
        Create SageMaker HyperparameterTuner
        """
        try:
            from sagemaker.tuner import HyperparameterTuner
            
            tuner = HyperparameterTuner(
                estimator=self.estimator,
                objective_metric_name=self.objective_metric['Name'],
                hyperparameter_ranges=self.hyperparameter_ranges,
                metric_definitions=[
                    {
                        'Name': self.objective_metric['Name'],
                        'Regex': self.objective_metric['Regex']
                    }
                ],
                max_jobs=max_jobs,
                max_parallel_jobs=max_parallel_jobs,
                strategy=strategy,
                objective_type='Maximize'
            )
            
            logger.info(f"HyperparameterTuner created with {max_jobs} max jobs")
            return tuner
            
        except ImportError:
            logger.error("SageMaker SDK not available")
            raise
    
    def get_best_hyperparameters(self, tuning_job_name):
        """
        Retrieve best hyperparameters from completed tuning job
        """
        try:
            import boto3
            
            sagemaker_client = boto3.client('sagemaker')
            
            response = sagemaker_client.describe_hyper_parameter_tuning_job(
                HyperParameterTuningJobName=tuning_job_name
            )
            
            best_training_job = response['BestTrainingJob']['TrainingJobName']
            
            training_job_response = sagemaker_client.describe_training_job(
                TrainingJobName=best_training_job
            )
            
            best_params = training_job_response['HyperParameters']
            
            logger.info(f"Best hyperparameters: {best_params}")
            return best_params
            
        except Exception as e:
            logger.error(f"Error retrieving best hyperparameters: {str(e)}")
            raise


# Example usage
if __name__ == '__main__':
    # Test hyperparameter configuration
    logger.info("Testing hyperparameter configuration...")
    
    # Get default params
    params = HyperparameterConfig.get_hyperparameters('default')
    logger.info(f"Default params: {params}")
    
    # Validate params
    valid, issues = HyperparameterConfig.validate_hyperparameters(params)
    logger.info(f"Validation result: {valid}")
    
    # Get hyperparameter ranges
    ranges = HyperparameterConfig.get_hyperparameter_ranges()
    logger.info(f"Hyperparameter ranges configured: {list(ranges.keys())}")
