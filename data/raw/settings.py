import os

# Base directory for the skeletal dataset
BASE_DATASET_PATH = "D:\\Datasets\\InHARD\\Dataset\\01-InHARD"

# Paths for raw data
ONLINE_RAW_DATA_PATH = os.path.join(BASE_DATASET_PATH, "Online\\Skeleton")
SEGMENTED_RAW_DATA_PATH = os.path.join(BASE_DATASET_PATH, "Segmented")

# Optional: Additional configuration for dataset structure
HDF5_FILE_EXTENSION = ".h5"
BVH_FILE_EXTENSION = ".bvh"

# Validation: Ensure that the paths exist
if not os.path.exists(BASE_DATASET_PATH):
    raise FileNotFoundError(f"Base dataset path does not exist: {BASE_DATASET_PATH}")
if not os.path.exists(ONLINE_RAW_DATA_PATH):
    raise FileNotFoundError(f"Raw data path does not exist: {ONLINE_RAW_DATA_PATH}")

# Print settings if run directly (for debugging purposes)
if __name__ == "__main__":
    print("Settings file loaded successfully.")
    print(f"BASE_DATASET_PATH: {BASE_DATASET_PATH}")
    print(f"ONLINE_RAW_DATA_PATH: {ONLINE_RAW_DATA_PATH}")
    print(f"Supported HDF5 File Extension: {HDF5_FILE_EXTENSION}")
    print(f"Supported BVH File Extension: {BVH_FILE_EXTENSION}")