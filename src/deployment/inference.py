"""
Custom Inference Handler
Handles prediction requests for the diabetes classification model
"""

import json
import os
import logging
import numpy as np
import pandas as pd
import xgboost as xgb
import joblib

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def model_fn(model_dir):
    """
    Load the model for inference
    This function is called once when the endpoint is initialized
    
    Args:
        model_dir: Directory where model artifacts are stored
    
    Returns:
        Loaded model object
    """
    logger.info(f"Loading model from {model_dir}")
    
    try:
        # Load XGBoost model
        model_path = os.path.join(model_dir, 'xgboost-model')
        booster = xgb.Booster()
        booster.load_model(model_path)
        
        # Load scaler if available
        scaler_path = os.path.join(model_dir, 'scaler.pkl')
        if os.path.exists(scaler_path):
            scaler = joblib.load(scaler_path)
            logger.info("Scaler loaded successfully")
        else:
            scaler = None
            logger.warning("No scaler found, skipping scaling")
        
        # Load feature metadata
        metadata_path = os.path.join(model_dir, 'feature_metadata.json')
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                feature_metadata = json.load(f)
            logger.info(f"Feature metadata loaded: {feature_metadata}")
        else:
            feature_metadata = None
        
        logger.info("Model loaded successfully")
        
        return {
            'model': booster,
            'scaler': scaler,
            'metadata': feature_metadata
        }
        
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise


def input_fn(request_body, request_content_type):
    """
    Deserialize and prepare the input data for prediction
    
    Args:
        request_body: The request payload
        request_content_type: Content type of the request
    
    Returns:
        Prepared input data
    """
    logger.info(f"Processing input with content type: {request_content_type}")
    
    try:
        if request_content_type == 'application/json':
            # Parse JSON input
            data = json.loads(request_body)
            
            # Handle different JSON formats
            if isinstance(data, dict):
                if 'instances' in data:
                    # Format: {"instances": [[...], [...]]}
                    input_data = np.array(data['instances'])
                elif 'features' in data:
                    # Format: {"features": [...]}
                    input_data = np.array([data['features']])
                else:
                    # Assume the dict itself contains features
                    input_data = np.array([list(data.values())])
            elif isinstance(data, list):
                # Format: [[...], [...]]
                input_data = np.array(data)
            else:
                raise ValueError(f"Unsupported JSON format: {type(data)}")
                
        elif request_content_type == 'text/csv':
            # Parse CSV input
            from io import StringIO
            input_data = pd.read_csv(StringIO(request_body), header=None).values
            
        else:
            raise ValueError(f"Unsupported content type: {request_content_type}")
        
        logger.info(f"Input data shape: {input_data.shape}")
        return input_data
        
    except Exception as e:
        logger.error(f"Error processing input: {str(e)}")
        raise


def predict_fn(input_data, model_dict):
    """
    Make predictions on the input data
    
    Args:
        input_data: Preprocessed input data
        model_dict: Dictionary containing model and other artifacts
    
    Returns:
        Predictions
    """
    logger.info("Making predictions...")
    
    try:
        model = model_dict['model']
        scaler = model_dict.get('scaler')
        
        # Apply scaling if scaler is available
        if scaler is not None:
            input_data = scaler.transform(input_data)
            logger.info("Input data scaled")
        
        # Create DMatrix for XGBoost
        dmatrix = xgb.DMatrix(input_data)
        
        # Make predictions (probabilities)
        predictions_proba = model.predict(dmatrix)
        
        # Convert to class predictions (threshold = 0.5)
        predictions_class = (predictions_proba >= 0.5).astype(int)
        
        logger.info(f"Predictions made for {len(predictions_proba)} samples")
        
        return {
            'predictions': predictions_class.tolist(),
            'probabilities': predictions_proba.tolist()
        }
        
    except Exception as e:
        logger.error(f"Error making predictions: {str(e)}")
        raise


def output_fn(predictions, response_content_type):
    """
    Serialize the predictions for the response
    
    Args:
        predictions: Model predictions
        response_content_type: Desired response content type
    
    Returns:
        Serialized predictions
    """
    logger.info(f"Formatting output with content type: {response_content_type}")
    
    try:
        if response_content_type == 'application/json':
            # Add interpretation
            predictions_with_labels = []
            for pred, prob in zip(predictions['predictions'], predictions['probabilities']):
                predictions_with_labels.append({
                    'prediction': int(pred),
                    'label': 'Diabetes' if pred == 1 else 'No Diabetes',
                    'probability': float(prob),
                    'confidence': float(prob) if pred == 1 else float(1 - prob)
                })
            
            response = {
                'predictions': predictions_with_labels,
                'model_version': '1.0',
                'timestamp': str(pd.Timestamp.now())
            }
            
            return json.dumps(response)
            
        elif response_content_type == 'text/csv':
            # Return CSV format
            output = []
            for pred, prob in zip(predictions['predictions'], predictions['probabilities']):
                output.append(f"{pred},{prob}")
            return '\n'.join(output)
            
        else:
            raise ValueError(f"Unsupported response content type: {response_content_type}")
            
    except Exception as e:
        logger.error(f"Error formatting output: {str(e)}")
        raise


# For local testing
if __name__ == '__main__':
    # Test the inference functions
    logger.info("Testing inference handler...")
    
    # Sample input
    sample_input = json.dumps({
        "instances": [
            [6, 148, 72, 35, 0, 33.6, 0.627, 50],
            [1, 85, 66, 29, 0, 26.6, 0.351, 31]
        ]
    })
    
    # Test input_fn
    input_data = input_fn(sample_input, 'application/json')
    logger.info(f"Processed input shape: {input_data.shape}")
    
    logger.info("Inference handler test completed")
