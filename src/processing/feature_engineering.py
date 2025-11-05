"""
Feature Engineering Module
Handles feature transformations and Feature Store integration
"""

import logging
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
import joblib
import json

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class FeatureEngineer:
    """
    Feature engineering operations including:
    - Feature creation
    - Feature selection
    - Feature transformation
    - Feature Store integration (optional)
    """

    def __init__(self):
        self.scaler = StandardScaler()
        self.pca = None
        self.feature_importance = {}

    def create_derived_features(self, df):
        """Create new features from existing ones"""
        logger.info("Creating derived features...")

        df_enhanced = df.copy()

        # BMI Categories
        df_enhanced["BMI_Category"] = pd.cut(
            df_enhanced["BMI"],
            bins=[0, 18.5, 25, 30, 100],
            labels=[0, 1, 2, 3],  # Underweight, Normal, Overweight, Obese
        ).astype(float)

        # Age Groups
        df_enhanced["Age_Group"] = pd.cut(
            df_enhanced["Age"],
            bins=[0, 30, 40, 50, 100],
            labels=[0, 1, 2, 3],  # Young, Middle-aged, Senior, Elderly
        ).astype(float)

        # Glucose Level Categories (based on medical standards)
        df_enhanced["Glucose_Level"] = pd.cut(
            df_enhanced["Glucose"],
            bins=[0, 100, 125, 200],
            labels=[0, 1, 2],  # Normal, Prediabetic, Diabetic
        ).astype(float)

        # Blood Pressure Categories
        df_enhanced["BP_Category"] = pd.cut(
            df_enhanced["BloodPressure"],
            bins=[0, 80, 90, 120, 200],
            labels=[0, 1, 2, 3],  # Normal, Elevated, High, Very High
        ).astype(float)

        # Interaction features
        df_enhanced["BMI_Age_Interaction"] = df_enhanced["BMI"] * df_enhanced["Age"]
        df_enhanced["Glucose_BMI_Interaction"] = (
            df_enhanced["Glucose"] * df_enhanced["BMI"]
        )
        df_enhanced["Insulin_Glucose_Ratio"] = df_enhanced["Insulin"] / (
            df_enhanced["Glucose"] + 1
        )

        # Polynomial features for key variables
        df_enhanced["BMI_Squared"] = df_enhanced["BMI"] ** 2
        df_enhanced["Age_Squared"] = df_enhanced["Age"] ** 2
        df_enhanced["Glucose_Squared"] = df_enhanced["Glucose"] ** 2

        logger.info(
            f"Created {len(df_enhanced.columns) - len(df.columns)} new features"
        )
        logger.info(f"Total features: {len(df_enhanced.columns)}")

        return df_enhanced

    def select_features_by_correlation(self, X, y, threshold=0.1):
        """Select features based on correlation with target"""
        logger.info(f"Selecting features with correlation > {threshold}")

        # Calculate correlation with target
        correlations = pd.DataFrame(X).corrwith(pd.Series(y)).abs()
        selected_features = correlations[correlations > threshold].index.tolist()

        logger.info(
            f"Selected {len(selected_features)} features out of {len(X.columns)}"
        )
        logger.info(f"Selected features: {selected_features}")

        return selected_features

    def apply_pca(self, X_train, X_val, X_test, n_components=0.95):
        """Apply PCA for dimensionality reduction"""
        logger.info(f"Applying PCA with {n_components} variance retention...")

        self.pca = PCA(n_components=n_components)

        X_train_pca = self.pca.fit_transform(X_train)
        X_val_pca = self.pca.transform(X_val)
        X_test_pca = self.pca.transform(X_test)

        logger.info(f"PCA components: {self.pca.n_components_}")
        logger.info(
            f"Explained variance: {sum(self.pca.explained_variance_ratio_):.4f}"
        )

        # Convert back to DataFrame
        pca_columns = [f"PC{i+1}" for i in range(self.pca.n_components_)]
        X_train_pca = pd.DataFrame(X_train_pca, columns=pca_columns)
        X_val_pca = pd.DataFrame(X_val_pca, columns=pca_columns)
        X_test_pca = pd.DataFrame(X_test_pca, columns=pca_columns)

        return X_train_pca, X_val_pca, X_test_pca

    def normalize_features(self, X_train, X_val, X_test, method="standard"):
        """Normalize features using specified method"""
        logger.info(f"Normalizing features using {method} scaling...")

        if method == "standard":
            scaler = StandardScaler()
        elif method == "minmax":
            scaler = MinMaxScaler()
        else:
            raise ValueError(f"Unknown scaling method: {method}")

        X_train_scaled = scaler.fit_transform(X_train)
        X_val_scaled = scaler.transform(X_val)
        X_test_scaled = scaler.transform(X_test)

        # Convert back to DataFrame
        X_train_scaled = pd.DataFrame(X_train_scaled, columns=X_train.columns)
        X_val_scaled = pd.DataFrame(X_val_scaled, columns=X_val.columns)
        X_test_scaled = pd.DataFrame(X_test_scaled, columns=X_test.columns)

        self.scaler = scaler

        return X_train_scaled, X_val_scaled, X_test_scaled

    def get_feature_statistics(self, df):
        """Calculate feature statistics for monitoring"""
        logger.info("Calculating feature statistics...")

        stats = {
            "mean": df.mean().to_dict(),
            "std": df.std().to_dict(),
            "min": df.min().to_dict(),
            "max": df.max().to_dict(),
            "median": df.median().to_dict(),
            "q25": df.quantile(0.25).to_dict(),
            "q75": df.quantile(0.75).to_dict(),
        }

        return stats

    def save_feature_artifacts(self, output_dir):
        """Save feature engineering artifacts"""
        logger.info(f"Saving feature artifacts to {output_dir}")

        import os

        os.makedirs(output_dir, exist_ok=True)

        # Save scaler
        if self.scaler:
            joblib.dump(self.scaler, os.path.join(output_dir, "scaler.pkl"))

        # Save PCA
        if self.pca:
            joblib.dump(self.pca, os.path.join(output_dir, "pca.pkl"))

        # Save feature importance
        if self.feature_importance:
            with open(os.path.join(output_dir, "feature_importance.json"), "w") as f:
                json.dump(self.feature_importance, f, indent=2)

        logger.info("Feature artifacts saved successfully")


class FeatureStoreManager:
    """
    Manages Feature Store operations (optional)
    Integrates with SageMaker Feature Store for feature versioning and reuse
    """

    def __init__(self, feature_group_name, role, region="us-east-1"):
        self.feature_group_name = feature_group_name
        self.role = role
        self.region = region
        self.feature_group = None

    def create_feature_group(
        self, feature_definitions, record_identifier, event_time_feature
    ):
        """Create a feature group in SageMaker Feature Store"""
        try:
            import boto3
            import sagemaker
            from sagemaker.feature_store.feature_group import FeatureGroup

            logger.info(f"Creating feature group: {self.feature_group_name}")

            sagemaker_session = sagemaker.Session()

            self.feature_group = FeatureGroup(
                name=self.feature_group_name, sagemaker_session=sagemaker_session
            )

            self.feature_group.load_feature_definitions(data_frame=feature_definitions)

            # Create feature group
            self.feature_group.create(
                s3_uri=f"s3://{sagemaker_session.default_bucket()}/feature-store",
                record_identifier_name=record_identifier,
                event_time_feature_name=event_time_feature,
                role_arn=self.role,
                enable_online_store=True,
            )

            logger.info("Feature group created successfully")

        except ImportError:
            logger.warning(
                "SageMaker SDK not available. Feature Store integration skipped."
            )
        except Exception as e:
            logger.error(f"Error creating feature group: {str(e)}")
            raise

    def ingest_features(self, df):
        """Ingest features into Feature Store"""
        try:
            if self.feature_group:
                self.feature_group.ingest(data_frame=df, max_workers=3, wait=True)
                logger.info(f"Ingested {len(df)} records to feature store")
        except Exception as e:
            logger.error(f"Error ingesting features: {str(e)}")
            raise

    def get_features(self, record_ids):
        """Retrieve features from Feature Store"""
        try:
            if self.feature_group:
                records = []
                for record_id in record_ids:
                    record = self.feature_group.get_record(
                        record_identifier_value_as_string=str(record_id)
                    )
                    records.append(record)
                return records
        except Exception as e:
            logger.error(f"Error retrieving features: {str(e)}")
            raise


# Example usage
if __name__ == "__main__":
    # This is for testing purposes
    from sklearn.datasets import load_diabetes

    # Load sample data
    logger.info("Testing feature engineering module...")

    # Create sample dataframe
    data = load_diabetes(as_frame=True)
    df = data.frame

    # Initialize feature engineer
    fe = FeatureEngineer()

    # Test feature statistics
    stats = fe.get_feature_statistics(df)
    logger.info(f"Feature statistics calculated: {len(stats)} metrics")

    logger.info("Feature engineering module test completed")
