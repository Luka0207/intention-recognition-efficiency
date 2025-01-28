import os

# Base directory for the skeletal dataset
ANVIL_BASE_DATASET_PATH = "D:\\Datasets\\InHARD\\Dataset\\01-InHARD\\Online\\Labels"

# Paths for processed data
ANNOTATION_SPECS_DIR = os.path.join(ANVIL_BASE_DATASET_PATH, "Annotation_specs")
ANNOTATION_SPECS = os.path.join(ANNOTATION_SPECS_DIR, "Annotation_specs.xml")

# Optional: Additional configuration for dataset structure
ANVIL_FILE_EXTENSION = ".anvil"

# Validation: Ensure that the paths exist
if not os.path.exists(ANVIL_BASE_DATASET_PATH):
    raise FileNotFoundError(f"Base dataset path does not exist: {ANVIL_BASE_DATASET_PATH}")
if not os.path.exists(ANNOTATION_SPECS_DIR):
    raise FileNotFoundError(f"Processed data path does not exist: {ANNOTATION_SPECS_DIR}")
if not os.path.exists(ANNOTATION_SPECS):
    raise FileNotFoundError(f"Processed data path does not exist: {ANNOTATION_SPECS}")

# Print settings if run directly (for debugging purposes)
if __name__ == "__main__":
    print("Settings file loaded successfully.")
    print(f"ANVIL_BASE_DATASET_PATH: {ANVIL_BASE_DATASET_PATH}")
    print(f"ANVIL_BASE_DATASET_PATH: {ANNOTATION_SPECS_DIR}")
    print(f"ANNOTATION_SPECS: {ANNOTATION_SPECS}")
    print(f"Supported anvil File Extension: {ANVIL_FILE_EXTENSION}")