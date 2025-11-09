#!/usr/bin/env python3
"""
Model Evaluation Module
Comprehensive evaluation metrics and model assessment for diabetes classification
"""

import os
import json
import logging
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
    roc_curve,
    precision_recall_curve,
)

# Set matplotlib backend for headless environments (SageMaker)
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ModelEvaluator:
    """
    Comprehensive model evaluation and metrics calculation
    """

    def __init__(self, model, threshold=0.5):
        self.model = model
        self.threshold = threshold
        self.metrics = {}

    def predict(self, X):
        """Generate predictions"""
        if isinstance(X, pd.DataFrame):
            X = X.values

        dmatrix = xgb.DMatrix(X)
        predictions_proba = self.model.predict(dmatrix)
        predictions = (predictions_proba >= self.threshold).astype(int)

        return predictions, predictions_proba

    def calculate_classification_metrics(self, y_true, y_pred, y_pred_proba):
        """Calculate all classification metrics"""
        logger.info("Calculating classification metrics...")

        metrics = {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision": float(precision_score(y_true, y_pred, zero_division=0)),
            "recall": float(recall_score(y_true, y_pred, zero_division=0)),
            "f1_score": float(f1_score(y_true, y_pred, zero_division=0)),
            "roc_auc": float(roc_auc_score(y_true, y_pred_proba)),
        }

        # Calculate specificity
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        metrics["specificity"] = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
        metrics["sensitivity"] = metrics["recall"]  # Same as recall

        # Matthews Correlation Coefficient
        mcc_numerator = (tp * tn) - (fp * fn)
        mcc_denominator = np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
        metrics["mcc"] = (
            float(mcc_numerator / mcc_denominator) if mcc_denominator > 0 else 0.0
        )

        logger.info(f"Metrics calculated: {json.dumps(metrics, indent=2)}")

        return metrics

    def generate_confusion_matrix(self, y_true, y_pred):
        """Generate confusion matrix"""
        logger.info("Generating confusion matrix...")

        cm = confusion_matrix(y_true, y_pred)

        cm_dict = {
            "confusion_matrix": cm.tolist(),
            "true_negatives": int(cm[0, 0]),
            "false_positives": int(cm[0, 1]),
            "false_negatives": int(cm[1, 0]),
            "true_positives": int(cm[1, 1]),
        }

        return cm_dict

    def plot_confusion_matrix(self, y_true, y_pred, output_path=None):
        """Plot confusion matrix heatmap using matplotlib"""
        cm = confusion_matrix(y_true, y_pred)

        fig, ax = plt.subplots(figsize=(8, 6))
        im = ax.imshow(cm, interpolation="nearest", cmap="Blues")
        ax.figure.colorbar(im, ax=ax)

        # Set ticks and labels
        ax.set(
            xticks=np.arange(cm.shape[1]),
            yticks=np.arange(cm.shape[0]),
            xticklabels=["No Diabetes", "Diabetes"],
            yticklabels=["No Diabetes", "Diabetes"],
            ylabel="True Label",
            xlabel="Predicted Label",
            title="Confusion Matrix",
        )

        # Rotate the tick labels and set their alignment
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

        # Loop over data dimensions and create text annotations
        thresh = cm.max() / 2.0
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                ax.text(
                    j,
                    i,
                    format(cm[i, j], "d"),
                    ha="center",
                    va="center",
                    color="white" if cm[i, j] > thresh else "black",
                )

        fig.tight_layout()

        if output_path:
            plt.savefig(output_path, bbox_inches="tight", dpi=300)
            logger.info(f"Confusion matrix plot saved to {output_path}")

        plt.close()

    def plot_roc_curve(self, y_true, y_pred_proba, output_path=None):
        """Plot ROC curve"""
        fpr, tpr, thresholds = roc_curve(y_true, y_pred_proba)
        roc_auc = roc_auc_score(y_true, y_pred_proba)

        plt.figure(figsize=(8, 6))
        plt.plot(
            fpr, tpr, color="darkorange", lw=2, label=f"ROC curve (AUC = {roc_auc:.3f})"
        )
        plt.plot([0, 1], [0, 1], color="navy", lw=2, linestyle="--", label="Random")
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.title("Receiver Operating Characteristic (ROC) Curve")
        plt.legend(loc="lower right")
        plt.grid(alpha=0.3)

        if output_path:
            plt.savefig(output_path, bbox_inches="tight", dpi=300)
            logger.info(f"ROC curve plot saved to {output_path}")

        plt.close()

        return {
            "fpr": fpr.tolist(),
            "tpr": tpr.tolist(),
            "thresholds": thresholds.tolist(),
        }

    def plot_precision_recall_curve(self, y_true, y_pred_proba, output_path=None):
        """Plot Precision-Recall curve"""
        precision, recall, thresholds = precision_recall_curve(y_true, y_pred_proba)

        plt.figure(figsize=(8, 6))
        plt.plot(recall, precision, color="blue", lw=2)
        plt.xlabel("Recall")
        plt.ylabel("Precision")
        plt.title("Precision-Recall Curve")
        plt.grid(alpha=0.3)

        if output_path:
            plt.savefig(output_path, bbox_inches="tight", dpi=300)
            logger.info(f"Precision-Recall curve plot saved to {output_path}")

        plt.close()

        return {"precision": precision.tolist(), "recall": recall.tolist()}

    def generate_classification_report(self, y_true, y_pred):
        """Generate detailed classification report"""
        report = classification_report(
            y_true, y_pred, target_names=["No Diabetes", "Diabetes"], output_dict=True
        )

        logger.info(f"Classification Report:\n{classification_report(y_true, y_pred)}")

        return report

    def evaluate(self, X, y, output_dir=None):
        """
        Comprehensive evaluation pipeline
        """
        logger.info("=" * 50)
        logger.info("Starting Model Evaluation")
        logger.info("=" * 50)

        # Generate predictions
        y_pred, y_pred_proba = self.predict(X)

        # Calculate metrics
        metrics = self.calculate_classification_metrics(y, y_pred, y_pred_proba)

        # Confusion matrix
        cm_dict = self.generate_confusion_matrix(y, y_pred)

        # Classification report
        class_report = self.generate_classification_report(y, y_pred)

        # Combine all results
        evaluation_results = {
            "metrics": metrics,
            "confusion_matrix": cm_dict,
            "classification_report": class_report,
            "sample_size": len(y),
            "threshold": self.threshold,
        }

        # Generate plots if output directory provided
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

            # Plot confusion matrix
            self.plot_confusion_matrix(
                y, y_pred, output_path=os.path.join(output_dir, "confusion_matrix.png")
            )

            # Plot ROC curve
            roc_data = self.plot_roc_curve(
                y, y_pred_proba, output_path=os.path.join(output_dir, "roc_curve.png")
            )
            evaluation_results["roc_curve"] = roc_data

            # Plot Precision-Recall curve
            pr_data = self.plot_precision_recall_curve(
                y,
                y_pred_proba,
                output_path=os.path.join(output_dir, "precision_recall_curve.png"),
            )
            evaluation_results["precision_recall_curve"] = pr_data

            # Save evaluation results
            with open(os.path.join(output_dir, "evaluation_results.json"), "w") as f:
                # Convert numpy types to native Python types for JSON serialization
                results_serializable = self._make_json_serializable(evaluation_results)
                json.dump(results_serializable, f, indent=2)

            logger.info(f"Evaluation results saved to {output_dir}")

        self.metrics = metrics

        logger.info("=" * 50)
        logger.info("Evaluation Complete")
        logger.info("=" * 50)

        return evaluation_results

    def _make_json_serializable(self, obj):
        """Convert numpy types to native Python types"""
        if isinstance(obj, dict):
            return {
                key: self._make_json_serializable(value) for key, value in obj.items()
            }
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj

    def check_approval_criteria(self, min_accuracy=0.75, min_f1=0.70, min_roc_auc=0.80):
        """
        Check if model meets approval criteria
        """
        logger.info("Checking model approval criteria...")

        approval_status = {
            "approved": False,
            "criteria": {
                "min_accuracy": min_accuracy,
                "min_f1": min_f1,
                "min_roc_auc": min_roc_auc,
            },
            "actual_metrics": self.metrics,
            "checks": {},
        }

        # Check each criterion
        accuracy_check = self.metrics.get("accuracy", 0) >= min_accuracy
        f1_check = self.metrics.get("f1_score", 0) >= min_f1
        roc_auc_check = self.metrics.get("roc_auc", 0) >= min_roc_auc

        approval_status["checks"] = {
            "accuracy": accuracy_check,
            "f1_score": f1_check,
            "roc_auc": roc_auc_check,
        }

        # Overall approval
        approval_status["approved"] = all([accuracy_check, f1_check, roc_auc_check])

        if approval_status["approved"]:
            logger.info("✓ Model APPROVED - All criteria met")
        else:
            logger.warning("✗ Model REJECTED - Some criteria not met")
            for metric, passed in approval_status["checks"].items():
                if not passed:
                    logger.warning(
                        f"  - {metric}: {self.metrics.get(metric, 0):.4f} (required: {approval_status['criteria'][f'min_{metric}']})"
                    )

        return approval_status


# SageMaker evaluation script
if __name__ == "__main__":
    import argparse
    import joblib

    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", type=str, default="/opt/ml/processing/model")
    parser.add_argument("--test-data", type=str, default="/opt/ml/processing/test")
    parser.add_argument(
        "--output-dir", type=str, default="/opt/ml/processing/evaluation"
    )
    parser.add_argument("--threshold", type=float, default=0.5)

    args = parser.parse_args()

    logger.info("Loading model...")
    model_path = os.path.join(args.model_dir, "xgboost-model")
    booster = xgb.Booster()
    booster.load_model(model_path)

    logger.info("Loading test data...")
    test_df = pd.read_csv(os.path.join(args.test_data, "test.csv"), header=None)
    y_test = test_df.iloc[:, 0]
    X_test = test_df.iloc[:, 1:]

    logger.info(f"Test data shape: {X_test.shape}")

    # Evaluate model
    evaluator = ModelEvaluator(booster, threshold=args.threshold)
    results = evaluator.evaluate(X_test, y_test, output_dir=args.output_dir)

    # Check approval
    approval = evaluator.check_approval_criteria()

    # Save approval status
    with open(os.path.join(args.output_dir, "approval_status.json"), "w") as f:
        json.dump(approval, f, indent=2)

    logger.info("Evaluation completed successfully")
