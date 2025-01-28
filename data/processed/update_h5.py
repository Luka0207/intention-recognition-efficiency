import h5py
import numpy as np
from typing import List, Dict, Optional, Any

def update_hdf5_file(file_path: str, dataset_name: str, new_data: Any, mode: str = 'a') -> None:
    """
    Updates an HDF5 file by adding or modifying a dataset.

    Parameters:
        file_path (str): Path to the HDF5 file.
        dataset_name (str): Name of the dataset to update or create.
        new_data (Any): Data to write to the dataset.
        mode (str): File mode ('a' to append, 'r+' for read/write). Default is 'a'.

    Returns:
        None
    """
    try:
        # Open the HDF5 file in the specified mode
        with h5py.File(file_path, mode) as hdf_file:
            if dataset_name in hdf_file:
                # If the dataset already exists, update it
                print(f"Dataset '{dataset_name}' exists. Updating...")
                del hdf_file[dataset_name]  # Delete the existing dataset
                hdf_file.create_dataset(dataset_name, data=new_data)
            else:
                # Create a new dataset if it doesn't exist
                print(f"Dataset '{dataset_name}' does not exist. Creating...")
                hdf_file.create_dataset(dataset_name, data=new_data)

            print(f"Dataset '{dataset_name}' has been updated/created successfully.")
            hdf_file.close()

    except Exception as e:
        print(f"An error occurred: {e}")
