import h5py
import numpy as np
from typing import List, Dict, Optional

def read_hdf5_file(hdf5_path: str) -> Dict[str, object]:
    """
    Reads data from an HDF5 file and returns it in a structured format.

    Args:
        hdf5_path (str): Path to the HDF5 file.

    Returns:
        dict: A dictionary containing:
            - 'hierarchy': List[Dict[str, object]] with joint data.
            - 'motion': np.ndarray representing motion data.
            - 'channels': List[str] of channel names.
    """
    with h5py.File(hdf5_path, 'r') as hdf:
        # Read hierarchy
        hierarchy_group = hdf["hierarchy"]
        hierarchy: List[Dict[str, object]] = []
        for joint_name in hierarchy_group:
            joint_group = hierarchy_group[joint_name]
            hierarchy.append({
                "name": str(joint_group.attrs["name"]),
                "parent": str(joint_group.attrs["parent"]) if joint_group.attrs["parent"] != "None" else None,
                "offset": joint_group.attrs["offset"].tolist()  # Convert NumPy array to list
            })

        # Read motion data
        motion_data: np.ndarray = hdf["motion_data"][:]

        # Read channels
        channels: List[str] = [ch.decode("utf-8") for ch in hdf["channels"][:]]

        # Read channels
        order: List[str] = [ch.decode("utf-8") for ch in hdf["order"][:]]

        # Read world motion data
        world_motion_data: np.ndarray = hdf["motion_data"][:]

    return {
        "hierarchy": hierarchy,
        "motion": motion_data,
        "channels": channels,
        "order": order,
        "world_motion": world_motion_data
    }
