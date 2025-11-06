"""
Custom Metrics Module
Additional evaluation metrics and utilities
"""

import numpy as np
from sklearn.metrics import make_scorer
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def business_metric_cost(y_true, y_pred, fp_cost=100, fn_cost=500):
    """
    Calculate business cost metric
    False Positive (FP): Unnecessary treatment cost
    False Negative (FN): Missed diagnosis cost (much higher)

    Args:
        y_true: True labels
        y_pred: Predicted labels
        fp_cost: Cost of false positive
        fn_cost: Cost of false negative

    Returns:
        Total business cost (as Python int)
    """
    from sklearn.metrics import confusion_matrix

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

    total_cost = int((fp * fp_cost) + (fn * fn_cost))

    logger.info(
        f"Business Cost - FP: {fp} (${fp*fp_cost}), FN: {fn} (${fn*fn_cost}), Total: ${total_cost}"
    )

    return total_cost


def youden_index(y_true, y_pred):
    """
    Calculate Youden's Index (Sensitivity + Specificity - 1)
    Range: [-1, 1], higher is better
    """
    from sklearn.metrics import confusion_matrix

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0

    youden = sensitivity + specificity - 1

    return youden


def diagnostic_odds_ratio(y_true, y_pred):
    """
    Calculate Diagnostic Odds Ratio (DOR)
    DOR = (TP/FN) / (FP/TN)
    Higher values indicate better test performance
    """
    from sklearn.metrics import confusion_matrix

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

    if fn == 0 or tn == 0:
        return float("inf")

    dor = (tp / fn) / (fp / tn) if fp > 0 else float("inf")

    return dor


def net_benefit(y_true, y_pred_proba, threshold=0.5):
    """
    Calculate Net Benefit for decision curve analysis
    Net Benefit = (TP/N) - (FP/N) * (pt/(1-pt))
    where pt is the threshold probability
    """
    y_pred = (y_pred_proba >= threshold).astype(int)

    from sklearn.metrics import confusion_matrix

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

    n = len(y_true)

    net_benefit = (tp / n) - (fp / n) * (threshold / (1 - threshold))

    return net_benefit


def calculate_optimal_threshold(y_true, y_pred_proba, metric="youden"):
    """
    Find optimal classification threshold based on metric

    Args:
        y_true: True labels
        y_pred_proba: Predicted probabilities
        metric: 'youden', 'f1', or 'cost'

    Returns:
        Optimal threshold value
    """
    from sklearn.metrics import f1_score

    thresholds = np.arange(0.1, 0.9, 0.01)
    best_threshold = 0.5
    best_score = -float("inf")

    for threshold in thresholds:
        y_pred = (y_pred_proba >= threshold).astype(int)

        if metric == "youden":
            score = youden_index(y_true, y_pred)
        elif metric == "f1":
            score = f1_score(y_true, y_pred)
        elif metric == "cost":
            score = -business_metric_cost(
                y_true, y_pred
            )  # Negative because we minimize cost
        else:
            raise ValueError(f"Unknown metric: {metric}")

        if score > best_score:
            best_score = score
            best_threshold = threshold

    logger.info(
        f"Optimal threshold ({metric}): {best_threshold:.3f} with score: {best_score:.4f}"
    )

    return best_threshold


def calibration_curve(y_true, y_pred_proba, n_bins=10):
    """
    Calculate calibration curve for probability calibration assessment

    Returns:
        Dictionary with fraction of positives and mean predicted values
    """
    from sklearn.calibration import calibration_curve as sklearn_calibration_curve

    fraction_of_positives, mean_predicted_value = sklearn_calibration_curve(
        y_true, y_pred_proba, n_bins=n_bins
    )

    return {
        "fraction_of_positives": fraction_of_positives.tolist(),
        "mean_predicted_value": mean_predicted_value.tolist(),
    }


def expected_calibration_error(y_true, y_pred_proba, n_bins=10):
    """
    Calculate Expected Calibration Error (ECE)
    Lower values indicate better calibration
    """
    from sklearn.calibration import calibration_curve as sklearn_calibration_curve

    fraction_of_positives, mean_predicted_value = sklearn_calibration_curve(
        y_true, y_pred_proba, n_bins=n_bins
    )

    ece = np.abs(fraction_of_positives - mean_predicted_value).mean()

    logger.info(f"Expected Calibration Error: {ece:.4f}")

    return float(ece)


class MetricTracker:
    """
    Track metrics over time for monitoring model performance
    """

    def __init__(self):
        self.history = []

    def add_metrics(self, metrics, timestamp=None):
        """Add metrics snapshot"""
        import datetime

        if timestamp is None:
            timestamp = datetime.datetime.now().isoformat()

        self.history.append({"timestamp": timestamp, "metrics": metrics})

    def get_metric_trend(self, metric_name):
        """Get trend for specific metric"""
        values = [h["metrics"].get(metric_name, None) for h in self.history]
        timestamps = [h["timestamp"] for h in self.history]

        return {"timestamps": timestamps, "values": values}

    def detect_degradation(self, metric_name, threshold=0.05):
        """
        Detect if metric has degraded beyond threshold
        Compares latest value to baseline (first value)
        """
        if len(self.history) < 2:
            return False

        baseline = self.history[0]["metrics"].get(metric_name, 0)
        latest = self.history[-1]["metrics"].get(metric_name, 0)

        degradation = baseline - latest

        if degradation > threshold:
            logger.warning(
                f"Metric degradation detected for {metric_name}: {degradation:.4f}"
            )
            return True

        return False


# Custom scorers for cross-validation
business_cost_scorer = make_scorer(business_metric_cost, greater_is_better=False)
youden_scorer = make_scorer(youden_index)


if __name__ == "__main__":
    # Test metrics
    logger.info("Testing custom metrics...")

    # Sample data
    y_true = np.array([0, 0, 1, 1, 0, 1, 0, 1, 1, 0])
    y_pred = np.array([0, 0, 1, 1, 0, 0, 0, 1, 1, 1])
    y_pred_proba = np.array([0.1, 0.2, 0.8, 0.9, 0.3, 0.4, 0.2, 0.85, 0.75, 0.6])

    # Test Youden's Index
    youden = youden_index(y_true, y_pred)
    logger.info(f"Youden's Index: {youden:.4f}")

    # Test business cost
    cost = business_metric_cost(y_true, y_pred)
    logger.info(f"Business Cost: ${cost}")

    # Test optimal threshold
    optimal_thresh = calculate_optimal_threshold(y_true, y_pred_proba, metric="youden")

    # Test calibration
    ece = expected_calibration_error(y_true, y_pred_proba)

    logger.info("Custom metrics testing completed")
