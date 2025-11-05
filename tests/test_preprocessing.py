"""
Unit tests for preprocessing module
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.processing.preprocessing import DataPreprocessor


class TestDataPreprocessor:
    """Test cases for DataPreprocessor class"""

    @pytest.fixture
    def sample_data(self):
        """Create sample diabetes dataset"""
        np.random.seed(42)
        data = {
            "Pregnancies": np.random.randint(0, 15, 100),
            "Glucose": np.random.randint(0, 200, 100),
            "BloodPressure": np.random.randint(0, 120, 100),
            "SkinThickness": np.random.randint(0, 100, 100),
            "Insulin": np.random.randint(0, 850, 100),
            "BMI": np.random.uniform(0, 70, 100),
            "DiabetesPedigreeFunction": np.random.uniform(0, 2.5, 100),
            "Age": np.random.randint(21, 90, 100),
            "Outcome": np.random.randint(0, 2, 100),
        }
        return pd.DataFrame(data)

    @pytest.fixture
    def preprocessor(self):
        """Create preprocessor instance"""
        return DataPreprocessor()

    def test_validate_data(self, preprocessor, sample_data):
        """Test data validation"""
        report = preprocessor.validate_data(sample_data)

        assert "total_rows" in report
        assert "total_columns" in report
        assert report["total_rows"] == 100
        assert report["total_columns"] == 9

    def test_handle_missing_values(self, preprocessor, sample_data):
        """Test missing value handling"""
        # Introduce some zeros (representing missing values)
        sample_data.loc[0:5, "Glucose"] = 0

        cleaned_data = preprocessor.handle_missing_values(sample_data)

        # Check that zeros in Glucose are replaced
        assert (cleaned_data["Glucose"] == 0).sum() == 0

    def test_split_features_target(self, preprocessor, sample_data):
        """Test feature-target split"""
        X, y = preprocessor.split_features_target(sample_data)

        assert len(X.columns) == 8  # All features except Outcome
        assert "Outcome" not in X.columns
        assert len(y) == 100
        assert preprocessor.target_column == "Outcome"

    def test_detect_outliers(self, preprocessor, sample_data):
        """Test outlier detection"""
        columns = sample_data.columns[:-1]  # Exclude target
        outlier_report = preprocessor.detect_outliers(sample_data, columns)

        assert isinstance(outlier_report, dict)
        assert len(outlier_report) == len(columns)

    def test_prepare_data(self, preprocessor, sample_data):
        """Test complete data preparation pipeline"""
        result = preprocessor.prepare_data(sample_data)

        # Check all required keys
        assert "X_train" in result
        assert "X_val" in result
        assert "X_test" in result
        assert "y_train" in result
        assert "y_val" in result
        assert "y_test" in result

        # Check data split ratios
        total_samples = (
            len(result["X_train"]) + len(result["X_val"]) + len(result["X_test"])
        )
        assert total_samples == len(sample_data)

        # Check that features are scaled
        assert (
            result["X_train"].mean().abs().max() < 5
        )  # Should be close to 0 after scaling


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
