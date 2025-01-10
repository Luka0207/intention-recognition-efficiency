import os




# Base directory for the skeletal dataset
BASE_DATASET_PATH = "D:\\Datasets\\InHARDProcessedRaw"

# Paths for processed data
RAW_PROCESSED_DATA_PATH = os.path.join(BASE_DATASET_PATH, "ProcessedRaw")
RAW_ONLINE_PROCESSED_DATA_PATH = os.path.join(RAW_PROCESSED_DATA_PATH, "Online")

# Optional: Additional configuration for dataset structure
HDF5_FILE_EXTENSION = ".h5"

# Validation: Ensure that the paths exist
if not os.path.exists(BASE_DATASET_PATH):
    raise FileNotFoundError(f"Base dataset path does not exist: {BASE_DATASET_PATH}")
if not os.path.exists(RAW_PROCESSED_DATA_PATH):
    raise FileNotFoundError(f"Processed data path does not exist: {RAW_PROCESSED_DATA_PATH}")
if not os.path.exists(RAW_ONLINE_PROCESSED_DATA_PATH):
    raise FileNotFoundError(f"Processed data path does not exist: {RAW_ONLINE_PROCESSED_DATA_PATH}")

# Print settings if run directly (for debugging purposes)
if __name__ == "__main__":
    print("Settings file loaded successfully.")
    print(f"BASE_DATASET_PATH: {BASE_DATASET_PATH}")
    print(f"RAW_PROCESSED_DATA_PATH: {RAW_PROCESSED_DATA_PATH}")
    print(f"RAW_ONLINE_PROCESSED_DATA_PATH: {RAW_ONLINE_PROCESSED_DATA_PATH}")
    print(f"Supported HDF5 File Extension: {HDF5_FILE_EXTENSION}")
    print(f"Supported BVH File Extension: {BVH_FILE_EXTENSION}")