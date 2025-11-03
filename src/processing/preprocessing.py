"""
Data Preprocessing Script for SageMaker Processing Job
This script handles data loading, cleaning, validation, and preprocessing
for the diabetes classification dataset.
"""

import argparse
import os
import logging
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DataPreprocessor:
    """
    Handles all data preprocessing operations including:
    - Data loading and validation
    - Missing value handling
    - Outlier detection and treatment
    - Feature scaling
    - Data splitting
    """
    
    def __init__(self, config=None):
        self.config = config or {}
        self.scaler = StandardScaler()
        self.feature_columns = None
        self.target_column = 'Outcome'
        
    def load_data(self, input_path):
        """Load data from CSV file"""
        logger.info(f"Loading data from {input_path}")
        
        # Column names for Pima Indians Diabetes dataset
        column_names = [
            'Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness',
            'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age', 'Outcome'
        ]
        
        try:
            df = pd.read_csv(input_path, names=column_names, header=None)
            logger.info(f"Data loaded successfully. Shape: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise
    
    def validate_data(self, df):
        """Perform data quality checks"""
        logger.info("Validating data quality...")
        
        validation_report = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'missing_values': {},
            'data_types': {},
            'duplicates': 0,
            'issues': []
        }
        
        # Check for missing values
        missing = df.isnull().sum()
        validation_report['missing_values'] = missing[missing > 0].to_dict()
        
        # Check data types
        validation_report['data_types'] = df.dtypes.astype(str).to_dict()
        
        # Check for duplicates
        duplicates = df.duplicated().sum()
        validation_report['duplicates'] = int(duplicates)
        
        # Check for zeros that might indicate missing values
        # In this dataset, zeros in certain columns are physiologically impossible
        zero_columns = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
        for col in zero_columns:
            zero_count = (df[col] == 0).sum()
            if zero_count > 0:
                validation_report['issues'].append(
                    f"{col}: {zero_count} zero values (likely missing)"
                )
        
        logger.info(f"Validation report: {json.dumps(validation_report, indent=2)}")
        return validation_report
    
    def handle_missing_values(self, df):
        """Handle missing values and zeros representing missing data"""
        logger.info("Handling missing values...")
        
        df_cleaned = df.copy()
        
        # Replace zeros with NaN for columns where zero is impossible
        zero_columns = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
        for col in zero_columns:
            df_cleaned[col] = df_cleaned[col].replace(0, np.nan)
        
        # Strategy: Replace with median (more robust to outliers)
        for col in zero_columns:
            median_value = df_cleaned[col].median()
            df_cleaned[col].fillna(median_value, inplace=True)
            logger.info(f"Filled {col} missing values with median: {median_value:.2f}")
        
        return df_cleaned
    
    def detect_outliers(self, df, columns, threshold=3):
        """Detect outliers using Z-score method"""
        logger.info("Detecting outliers...")
        
        outlier_report = {}
        for col in columns:
            z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
            outliers = z_scores > threshold
            outlier_count = outliers.sum()
            outlier_report[col] = int(outlier_count)
            
            if outlier_count > 0:
                logger.info(f"{col}: {outlier_count} outliers detected")
        
        return outlier_report
    
    def handle_outliers(self, df, method='cap', threshold=3):
        """Handle outliers by capping at threshold or removing"""
        logger.info(f"Handling outliers using method: {method}")
        
        df_cleaned = df.copy()
        numeric_columns = df_cleaned.select_dtypes(include=[np.number]).columns
        numeric_columns = [col for col in numeric_columns if col != self.target_column]
        
        if method == 'cap':
            for col in numeric_columns:
                mean = df_cleaned[col].mean()
                std = df_cleaned[col].std()
                lower_bound = mean - threshold * std
                upper_bound = mean + threshold * std
                
                df_cleaned[col] = df_cleaned[col].clip(lower=lower_bound, upper=upper_bound)
        
        elif method == 'remove':
            for col in numeric_columns:
                z_scores = np.abs((df_cleaned[col] - df_cleaned[col].mean()) / df_cleaned[col].std())
                df_cleaned = df_cleaned[z_scores < threshold]
        
        logger.info(f"Data shape after outlier handling: {df_cleaned.shape}")
        return df_cleaned
    
    def split_features_target(self, df):
        """Split dataframe into features and target"""
        X = df.drop(columns=[self.target_column])
        y = df[self.target_column]
        
        self.feature_columns = X.columns.tolist()
        logger.info(f"Features: {self.feature_columns}")
        
        return X, y
    
    def scale_features(self, X_train, X_val, X_test):
        """Scale features using StandardScaler"""
        logger.info("Scaling features...")
        
        # Fit scaler on training data only
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Convert back to DataFrame
        X_train_scaled = pd.DataFrame(X_train_scaled, columns=self.feature_columns)
        X_val_scaled = pd.DataFrame(X_val_scaled, columns=self.feature_columns)
        X_test_scaled = pd.DataFrame(X_test_scaled, columns=self.feature_columns)
        
        logger.info("Feature scaling completed")
        return X_train_scaled, X_val_scaled, X_test_scaled
    
    def prepare_data(self, df, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15, random_state=42):
        """Complete data preparation pipeline"""
        logger.info("Starting data preparation pipeline...")
        
        # Validate data
        validation_report = self.validate_data(df)
        
        # Handle missing values
        df_cleaned = self.handle_missing_values(df)
        
        # Detect and handle outliers
        outlier_report = self.detect_outliers(df_cleaned, df_cleaned.columns[:-1])
        df_cleaned = self.handle_outliers(df_cleaned, method='cap')
        
        # Split features and target
        X, y = self.split_features_target(df_cleaned)
        
        # Split data: first split to separate test set
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, test_size=test_ratio, random_state=random_state, stratify=y
        )
        
        # Split remaining data into train and validation
        val_size_adjusted = val_ratio / (train_ratio + val_ratio)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=val_size_adjusted, random_state=random_state, stratify=y_temp
        )
        
        logger.info(f"Data split - Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
        
        # Scale features
        X_train_scaled, X_val_scaled, X_test_scaled = self.scale_features(X_train, X_val, X_test)
        
        return {
            'X_train': X_train_scaled,
            'X_val': X_val_scaled,
            'X_test': X_test_scaled,
            'y_train': y_train,
            'y_val': y_val,
            'y_test': y_test,
            'validation_report': validation_report,
            'outlier_report': outlier_report
        }
    
    def save_processed_data(self, data_dict, output_path):
        """Save processed data to output directory"""
        logger.info(f"Saving processed data to {output_path}")
        
        os.makedirs(output_path, exist_ok=True)
        
        # Save train data (SageMaker XGBoost format: label in first column)
        train_data = pd.concat([
            data_dict['y_train'].reset_index(drop=True),
            data_dict['X_train'].reset_index(drop=True)
        ], axis=1)
        train_data.to_csv(os.path.join(output_path, 'train', 'train.csv'), index=False, header=False)
        
        # Save validation data
        val_data = pd.concat([
            data_dict['y_val'].reset_index(drop=True),
            data_dict['X_val'].reset_index(drop=True)
        ], axis=1)
        val_data.to_csv(os.path.join(output_path, 'validation', 'validation.csv'), index=False, header=False)
        
        # Save test data
        test_data = pd.concat([
            data_dict['y_test'].reset_index(drop=True),
            data_dict['X_test'].reset_index(drop=True)
        ], axis=1)
        test_data.to_csv(os.path.join(output_path, 'test', 'test.csv'), index=False, header=False)
        
        # Save scaler for inference
        joblib.dump(self.scaler, os.path.join(output_path, 'model', 'scaler.pkl'))
        
        # Save feature names
        feature_metadata = {
            'feature_columns': self.feature_columns,
            'target_column': self.target_column
        }
        with open(os.path.join(output_path, 'model', 'feature_metadata.json'), 'w') as f:
            json.dump(feature_metadata, f, indent=2)
        
        # Save validation reports
        reports = {
            'validation_report': data_dict['validation_report'],
            'outlier_report': data_dict['outlier_report']
        }
        with open(os.path.join(output_path, 'reports', 'data_quality_report.json'), 'w') as f:
            json.dump(reports, f, indent=2)
        
        logger.info("All processed data saved successfully")


def main():
    """Main execution function for SageMaker Processing Job"""
    parser = argparse.ArgumentParser()
    
    # SageMaker specific arguments
    parser.add_argument('--input-data', type=str, default='/opt/ml/processing/input')
    parser.add_argument('--output-data', type=str, default='/opt/ml/processing/output')
    
    # Data processing arguments
    parser.add_argument('--train-ratio', type=float, default=0.7)
    parser.add_argument('--val-ratio', type=float, default=0.15)
    parser.add_argument('--test-ratio', type=float, default=0.15)
    parser.add_argument('--random-state', type=int, default=42)
    
    args = parser.parse_args()
    
    logger.info("="*50)
    logger.info("Starting SageMaker Processing Job")
    logger.info("="*50)
    
    # Initialize preprocessor
    preprocessor = DataPreprocessor()
    
    # Find input file
    input_files = [f for f in os.listdir(args.input_data) if f.endswith('.csv')]
    if not input_files:
        raise ValueError(f"No CSV file found in {args.input_data}")
    
    input_file_path = os.path.join(args.input_data, input_files[0])
    
    # Load data
    df = preprocessor.load_data(input_file_path)
    
    # Prepare data
    processed_data = preprocessor.prepare_data(
        df,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio,
        random_state=args.random_state
    )
    
    # Create output directories
    for subdir in ['train', 'validation', 'test', 'model', 'reports']:
        os.makedirs(os.path.join(args.output_data, subdir), exist_ok=True)
    
    # Save processed data
    preprocessor.save_processed_data(processed_data, args.output_data)
    
    logger.info("="*50)
    logger.info("Processing Job Completed Successfully")
    logger.info("="*50)


if __name__ == '__main__':
    main()
