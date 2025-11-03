"""
Drift Detection Module
Detect data drift and model performance degradation
"""

import boto3
import json
import numpy as np
import pandas as pd
from scipy import stats
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DriftDetector:
    """
    Detects various types of drift in data and model performance
    """
    
    def __init__(self, threshold=0.05):
        """
        Initialize drift detector
        
        Args:
            threshold: P-value threshold for statistical tests
        """
        self.threshold = threshold
        self.baseline_stats = {}
        self.drift_detected = False
        
    def set_baseline(self, baseline_data):
        """
        Set baseline statistics from training data
        
        Args:
            baseline_data: DataFrame with baseline data
        """
        logger.info("Setting baseline statistics...")
        
        self.baseline_stats = {
            'mean': baseline_data.mean().to_dict(),
            'std': baseline_data.std().to_dict(),
            'min': baseline_data.min().to_dict(),
            'max': baseline_data.max().to_dict(),
            'quantiles': {
                '25': baseline_data.quantile(0.25).to_dict(),
                '50': baseline_data.quantile(0.50).to_dict(),
                '75': baseline_data.quantile(0.75).to_dict()
            }
        }
        
        logger.info(f"Baseline set for {len(baseline_data.columns)} features")
        
    def kolmogorov_smirnov_test(self, baseline_data, current_data, feature):
        """
        Perform Kolmogorov-Smirnov test for distribution drift
        
        Returns:
            dict with test results
        """
        statistic, p_value = stats.ks_2samp(baseline_data[feature], current_data[feature])
        
        drift_detected = p_value < self.threshold
        
        return {
            'feature': feature,
            'test': 'Kolmogorov-Smirnov',
            'statistic': float(statistic),
            'p_value': float(p_value),
            'drift_detected': drift_detected,
            'threshold': self.threshold
        }
    
    def chi_square_test(self, baseline_data, current_data, feature, bins=10):
        """
        Perform Chi-Square test for categorical or binned numerical data
        
        Returns:
            dict with test results
        """
        # Bin the data
        baseline_binned = pd.cut(baseline_data[feature], bins=bins)
        current_binned = pd.cut(current_data[feature], bins=bins)
        
        # Get frequency distributions
        baseline_counts = baseline_binned.value_counts().sort_index()
        current_counts = current_binned.value_counts().sort_index()
        
        # Align indices
        all_bins = baseline_counts.index.union(current_counts.index)
        baseline_counts = baseline_counts.reindex(all_bins, fill_value=0)
        current_counts = current_counts.reindex(all_bins, fill_value=0)
        
        # Perform chi-square test
        statistic, p_value = stats.chisquare(
            f_obs=current_counts + 1,  # Add 1 to avoid zero frequencies
            f_exp=baseline_counts + 1
        )
        
        drift_detected = p_value < self.threshold
        
        return {
            'feature': feature,
            'test': 'Chi-Square',
            'statistic': float(statistic),
            'p_value': float(p_value),
            'drift_detected': drift_detected,
            'threshold': self.threshold
        }
    
    def population_stability_index(self, baseline_data, current_data, feature, bins=10):
        """
        Calculate Population Stability Index (PSI)
        PSI < 0.1: No significant change
        0.1 <= PSI < 0.2: Small change
        PSI >= 0.2: Significant change
        
        Returns:
            dict with PSI score
        """
        # Bin the data
        baseline_binned = pd.cut(baseline_data[feature], bins=bins)
        current_binned = pd.cut(current_data[feature], bins=bins)
        
        # Calculate proportions
        baseline_props = baseline_binned.value_counts(normalize=True).sort_index()
        current_props = current_binned.value_counts(normalize=True).sort_index()
        
        # Align indices
        all_bins = baseline_props.index.union(current_props.index)
        baseline_props = baseline_props.reindex(all_bins, fill_value=0.0001)  # Avoid log(0)
        current_props = current_props.reindex(all_bins, fill_value=0.0001)
        
        # Calculate PSI
        psi = np.sum((current_props - baseline_props) * np.log(current_props / baseline_props))
        
        # Interpret PSI
        if psi < 0.1:
            interpretation = "No significant change"
            drift_detected = False
        elif psi < 0.2:
            interpretation = "Small change"
            drift_detected = False
        else:
            interpretation = "Significant change (drift detected)"
            drift_detected = True
        
        return {
            'feature': feature,
            'test': 'PSI',
            'psi_score': float(psi),
            'interpretation': interpretation,
            'drift_detected': drift_detected
        }
    
    def detect_feature_drift(self, baseline_data, current_data):
        """
        Detect drift across all features
        
        Returns:
            Comprehensive drift report
        """
        logger.info("Detecting feature drift...")
        
        drift_report = {
            'summary': {
                'total_features': len(baseline_data.columns),
                'features_with_drift': 0,
                'drift_percentage': 0.0
            },
            'features': []
        }
        
        for feature in baseline_data.columns:
            logger.info(f"Testing feature: {feature}")
            
            # Perform multiple tests
            ks_test = self.kolmogorov_smirnov_test(baseline_data, current_data, feature)
            psi_test = self.population_stability_index(baseline_data, current_data, feature)
            
            # Combine results
            feature_drift = {
                'feature': feature,
                'tests': {
                    'ks_test': ks_test,
                    'psi': psi_test
                },
                'drift_detected': ks_test['drift_detected'] or psi_test['drift_detected']
            }
            
            drift_report['features'].append(feature_drift)
            
            if feature_drift['drift_detected']:
                drift_report['summary']['features_with_drift'] += 1
                logger.warning(f"Drift detected in feature: {feature}")
        
        # Calculate drift percentage
        drift_report['summary']['drift_percentage'] = (
            drift_report['summary']['features_with_drift'] / 
            drift_report['summary']['total_features'] * 100
        )
        
        self.drift_detected = drift_report['summary']['features_with_drift'] > 0
        
        logger.info(f"Drift detection complete. {drift_report['summary']['features_with_drift']} features with drift")
        
        return drift_report
    
    def detect_model_performance_drift(self, baseline_metrics, current_metrics):
        """
        Detect drift in model performance metrics
        
        Args:
            baseline_metrics: Dict of baseline performance metrics
            current_metrics: Dict of current performance metrics
        
        Returns:
            Performance drift report
        """
        logger.info("Detecting model performance drift...")
        
        drift_report = {
            'summary': {
                'degraded_metrics': [],
                'improved_metrics': [],
                'stable_metrics': []
            },
            'metrics': []
        }
        
        threshold = 0.05  # 5% change threshold
        
        for metric_name in baseline_metrics.keys():
            if metric_name not in current_metrics:
                continue
            
            baseline_value = baseline_metrics[metric_name]
            current_value = current_metrics[metric_name]
            
            # Calculate relative change
            relative_change = (current_value - baseline_value) / baseline_value if baseline_value != 0 else 0
            absolute_change = current_value - baseline_value
            
            # Determine drift status
            if relative_change < -threshold:
                status = 'degraded'
                drift_report['summary']['degraded_metrics'].append(metric_name)
            elif relative_change > threshold:
                status = 'improved'
                drift_report['summary']['improved_metrics'].append(metric_name)
            else:
                status = 'stable'
                drift_report['summary']['stable_metrics'].append(metric_name)
            
            metric_drift = {
                'metric': metric_name,
                'baseline_value': baseline_value,
                'current_value': current_value,
                'absolute_change': absolute_change,
                'relative_change': relative_change,
                'status': status
            }
            
            drift_report['metrics'].append(metric_drift)
            
            if status == 'degraded':
                logger.warning(f"Performance degradation detected in {metric_name}: {baseline_value:.4f} -> {current_value:.4f}")
        
        return drift_report
    
    def should_trigger_retraining(self, drift_report, performance_report=None):
        """
        Determine if retraining should be triggered based on drift
        
        Returns:
            bool, str - (should_retrain, reason)
        """
        reasons = []
        
        # Check feature drift
        if drift_report['summary']['drift_percentage'] > 20:
            reasons.append(f"Significant feature drift detected ({drift_report['summary']['drift_percentage']:.1f}%)")
        
        # Check performance drift
        if performance_report:
            if len(performance_report['summary']['degraded_metrics']) > 0:
                reasons.append(f"Performance degradation in {len(performance_report['summary']['degraded_metrics'])} metrics")
        
        should_retrain = len(reasons) > 0
        
        if should_retrain:
            logger.warning(f"Retraining recommended. Reasons: {', '.join(reasons)}")
        else:
            logger.info("No retraining needed at this time")
        
        return should_retrain, reasons


def main():
    """Test drift detection"""
    logger.info("Testing drift detection...")
    
    # Create sample baseline data
    np.random.seed(42)
    baseline = pd.DataFrame({
        'feature1': np.random.normal(100, 15, 1000),
        'feature2': np.random.normal(50, 10, 1000),
        'feature3': np.random.exponential(2, 1000)
    })
    
    # Create drifted data (shifted distribution)
    current = pd.DataFrame({
        'feature1': np.random.normal(105, 15, 1000),  # Slight drift
        'feature2': np.random.normal(50, 10, 1000),   # No drift
        'feature3': np.random.exponential(3, 1000)    # Significant drift
    })
    
    # Detect drift
    detector = DriftDetector(threshold=0.05)
    drift_report = detector.detect_feature_drift(baseline, current)
    
    logger.info(json.dumps(drift_report['summary'], indent=2))
    
    # Test performance drift
    baseline_metrics = {'accuracy': 0.80, 'f1_score': 0.75, 'roc_auc': 0.85}
    current_metrics = {'accuracy': 0.72, 'f1_score': 0.70, 'roc_auc': 0.83}
    
    perf_report = detector.detect_model_performance_drift(baseline_metrics, current_metrics)
    logger.info(json.dumps(perf_report['summary'], indent=2))
    
    # Check if retraining needed
    should_retrain, reasons = detector.should_trigger_retraining(drift_report, perf_report)
    logger.info(f"Should retrain: {should_retrain}")
    if reasons:
        logger.info(f"Reasons: {', '.join(reasons)}")


if __name__ == '__main__':
    main()
