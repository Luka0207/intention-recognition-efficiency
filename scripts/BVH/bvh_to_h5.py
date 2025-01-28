import os
import h5py
import numpy as np
from data.raw.settings import ONLINE_RAW_DATA_PATH, BVH_FILE_EXTENSION
from data.processed.settings import RAW_ONLINE_PROCESSED_DATA_PATH, HDF5_FILE_EXTENSION
from typing import List, Dict, Any

def read_bvh_file(file_path: str) -> List[str]:
    """
    Reads a BVH file and returns the content as a list of lines.

    Args:
        file_path (str): Path to the BVH file.

    Returns:
        list: List of lines from the BVH file.
    """
    with open(file_path, 'r') as bvh_file:
        lines = bvh_file.readlines()
    return [line.strip() for line in lines]

def process_bvh_lines(lines: List[str]) -> Dict[str, object]:
    """
    Processes lines from a BVH file to extract joint hierarchy and motion data.

    Args:
        lines (List[str]): List of lines from the BVH file.

    Returns:
        dict: Parsed BVH data with 'hierarchy', 'motion', and 'channels' keys.
    """
    hierarchy = []
    motion_data = []
    channels = []
    joint_stack = []
    in_motion_section = False
    order = []

    for line in lines:
        if not line:
            continue
        line = line.strip()
        
        if not in_motion_section:
            if line.startswith("ROOT") or line.startswith("JOINT"):
                # Extract joint name and add it to the hierarchy
                joint_name = line.split()[1]
                hierarchy.append({
                    "name": joint_name,
                    "parent": joint_stack[-1] if joint_stack else None,
                    "offset": None  # Placeholder for offset
                })
                order.append(joint_name)
                joint_stack.append(joint_name)
            elif line.startswith("End Site"):
                # Handle end site joints
                joint_name = f"{joint_stack[-1]}_End"
                hierarchy.append({
                    "name": joint_name,
                    "parent": joint_stack[-1],
                    "offset": None
                })
                joint_stack.append(joint_name)
            elif line.startswith("OFFSET"):
                # Update the offset of the last added joint
                offset_values = [float(v) for v in line.split()[1:]]
                hierarchy[-1]["offset"] = offset_values
            elif line.startswith("CHANNELS"):
                # Collect channel information
                channels.extend(line.split()[2:])
            elif line.startswith("}"):
                # Pop the last joint when exiting a scope
                if joint_stack:
                    joint_stack.pop()
            elif line.startswith("MOTION"):
                # Mark the start of the motion section
                in_motion_section = True
        else:
            # Process motion data
            if line.startswith("Frames:") or line.startswith("Frame Time:"):
                continue  # Skip motion section headers
            frame_values = [float(v) for v in line.split()]
            motion_data.append(frame_values)

    frame_lengths = [len(frame) for frame in motion_data]
    if len(set(frame_lengths)) > 1:
        raise ValueError(f"Inconsistent frame lengths detected: {set(frame_lengths)}")

    return {
        "hierarchy": hierarchy,
        "motion": np.array(motion_data),
        "channels": channels,
        "order": order
    }

def parse_bvh(file_path: str) -> Dict[str, object]:
    """
    Parse a BVH file to extract joint hierarchy and motion data.

    Args:
        file_path (str): Path to the BVH file.

    Returns:
        dict: Parsed BVH data with 'hierarchy' and 'motion' keys.
    """
    lines = read_bvh_file(file_path)
    return process_bvh_lines(lines)


def save_to_hdf5(parsed_data, hdf5_path):
    """
    Save parsed BVH data into an HDF5 file.

    Args:
        parsed_data (dict): Parsed BVH data with 'hierarchy' and 'motion'.
        hdf5_path (str): Path to the HDF5 file.
    """
    with h5py.File(hdf5_path, 'w') as hdf:
        # Save joint hierarchy
        hierarchy_group = hdf.create_group("hierarchy")
        for i, joint in enumerate(parsed_data["hierarchy"]):
            joint_group = hierarchy_group.create_group(f"joint_{i}")
            joint_group.attrs["name"] = joint["name"]
            joint_group.attrs["parent"] = joint["parent"] if joint["parent"] else "None"
            joint_group.attrs["offset"] = joint["offset"] if joint["offset"] else [0.0, 0.0, 0.0]  # Default to [0, 0, 0]

        # Save motion data
        hdf.create_dataset("motion_data", data=parsed_data["motion"])

        # Save channel names
        hdf.create_dataset("channels", data=np.bytes_(parsed_data["channels"]))

        # Save joint parser order
        hdf.create_dataset("order", data=np.bytes_(parsed_data["order"]))

def main():
    """
    Main function to process BVH files and convert them to HDF5.
    """
    # Ensure that raw and processed directories exist
    if not os.path.exists(ONLINE_RAW_DATA_PATH):
        raise FileNotFoundError(f"Raw data path does not exist: {ONLINE_RAW_DATA_PATH}")
    if not os.path.exists(RAW_ONLINE_PROCESSED_DATA_PATH):
        os.makedirs(RAW_ONLINE_PROCESSED_DATA_PATH)
    # Process each BVH file in the raw data folder
    for file_name in os.listdir(ONLINE_RAW_DATA_PATH):
        if file_name.endswith(BVH_FILE_EXTENSION):  # Only process BVH files
            raw_file_path = os.path.join(ONLINE_RAW_DATA_PATH, file_name)
            processed_file_path = os.path.join(RAW_ONLINE_PROCESSED_DATA_PATH, file_name.replace(BVH_FILE_EXTENSION, HDF5_FILE_EXTENSION))

            print(f"Processing {raw_file_path} -> {processed_file_path}")

            # Parse the BVH file
            parsed_bvh = parse_bvh(raw_file_path)

            # Save the parsed data to an HDF5 file
            save_to_hdf5(parsed_bvh, processed_file_path)

    print("Processing complete!")


if __name__ == "__main__":
    main()