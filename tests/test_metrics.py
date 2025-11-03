"""
Unit tests for evaluation metrics
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.evaluation.metrics import (
    business_metric_cost,
    youden_index,
    calculate_optimal_threshold,
    expected_calibration_error
)


class TestCustomMetrics:
    """Test cases for custom evaluation metrics"""
    
    @pytest.fixture
    def sample_predictions(self):
        """Create sample predictions"""
        y_true = np.array([0, 0, 1, 1, 0, 1, 0, 1, 1, 0])
        y_pred = np.array([0, 0, 1, 1, 0, 0, 0, 1, 1, 1])
        y_pred_proba = np.array([0.1, 0.2, 0.8, 0.9, 0.3, 0.4, 0.2, 0.85, 0.75, 0.6])
        
        return y_true, y_pred, y_pred_proba
    
    def test_business_cost(self, sample_predictions):
        """Test business cost metric"""
        y_true, y_pred, _ = sample_predictions
        
        cost = business_metric_cost(y_true, y_pred, fp_cost=100, fn_cost=500)
        
        assert cost >= 0
        assert isinstance(cost, (int, float))
    
    def test_youden_index(self, sample_predictions):
        """Test Youden's Index"""
        y_true, y_pred, _ = sample_predictions
        
        youden = youden_index(y_true, y_pred)
        
        assert -1 <= youden <= 1
        assert isinstance(youden, float)
    
    def test_optimal_threshold(self, sample_predictions):
        """Test optimal threshold calculation"""
        y_true, _, y_pred_proba = sample_predictions
        
        threshold = calculate_optimal_threshold(y_true, y_pred_proba, metric='f1')
        
        assert 0 <= threshold <= 1
        assert isinstance(threshold, float)
    
    def test_calibration_error(self, sample_predictions):
        """Test expected calibration error"""
        y_true, _, y_pred_proba = sample_predictions
        
        ece = expected_calibration_error(y_true, y_pred_proba)
        
        assert 0 <= ece <= 1
        assert isinstance(ece, float)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
