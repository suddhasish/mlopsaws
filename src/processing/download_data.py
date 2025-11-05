"""
Data Download Script
Downloads the Pima Indians Diabetes dataset
"""

import os
import logging
import urllib.request
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def download_diabetes_dataset(output_dir="data/raw"):
    """
    Download the Pima Indians Diabetes dataset
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Dataset URL
    url = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv"
    output_path = os.path.join(output_dir, "diabetes.csv")

    logger.info(f"Downloading dataset from {url}")

    try:
        # Download the file
        urllib.request.urlretrieve(url, output_path)
        logger.info(f"Dataset downloaded successfully to {output_path}")

        # Verify the download
        df = pd.read_csv(output_path, header=None)
        logger.info(f"Dataset shape: {df.shape}")
        logger.info(f"First few rows:\n{df.head()}")

        return output_path

    except Exception as e:
        logger.error(f"Error downloading dataset: {str(e)}")
        raise


if __name__ == "__main__":
    download_diabetes_dataset()
