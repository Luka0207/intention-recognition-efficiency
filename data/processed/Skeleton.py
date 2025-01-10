import numpy as np
from typing import Dict, List, Optional


class Skeleton:
    """
    Represents a skeleton with joints, motion data, and channels.
    Allows querying, transforming, and changing the root joint.
    """

    def __init__(self, hdf5_data: Dict[str, object]):
        """
        Initializes the Skeleton instance using parsed HDF5 data.

        Args:
            hdf5_data (dict): Parsed HDF5 data with keys:
                - 'hierarchy': List of joint information.
                - 'motion': Motion data as a NumPy array.
                - 'channels': List of channel names.
        """
        self.hierarchy = hdf5_data["hierarchy"]
        self.motion = hdf5_data["motion"].copy()  # Copy to avoid modifying the original
        self.channels = hdf5_data["channels"]

        # Identify the root joint (assume the first joint is the root)
        self.root_joint = self.hierarchy[0]["name"]

        # Build a mapping from joint name to its channel indices
        self.joint_channel_map = self._build_joint_channel_map()

    def _build_joint_channel_map(self) -> Dict[str, Dict[str, int]]:
        """
        Builds a map of joint names to their channel indices in the motion data.

        Returns:
            dict: A dictionary where keys are joint names and values are
                  dictionaries with keys 'Xposition', 'Yposition', 'Zposition',
                  'Xrotation', 'Yrotation', and 'Zrotation'.
        """
        joint_channel_map = {}
        current_index = 0

        for joint in self.hierarchy:
            joint_name = joint["name"]
            joint_channel_map[joint_name] = {}

            for channel in ["Xposition", "Yposition", "Zposition", "Xrotation", "Yrotation", "Zrotation"]:
                if current_index < len(self.channels) and self.channels[current_index] == channel:
                    joint_channel_map[joint_name][channel] = current_index
                    current_index += 1

        return joint_channel_map

    def set_new_root(self, new_root: str):
        """
        Changes the root joint to a new joint and updates the hierarchy and motion data.

        Args:
            new_root (str): The name of the new root joint.
        """
        if new_root == self.root_joint:
            print(f"{new_root} is already the root joint.")
            return

        # Step 1: Find the new root joint and validate
        new_root_index = None
        for i, joint in enumerate(self.hierarchy):
            if joint["name"] == new_root:
                new_root_index = i
                break

        if new_root_index is None:
            raise ValueError(f"Joint '{new_root}' not found in the hierarchy.")

        # Step 2: Transform motion data to make the new root the reference
        root_channels = self.joint_channel_map[self.root_joint]
        new_root_channels = self.joint_channel_map[new_root]

        for frame in range(len(self.motion)):
            # Calculate the new root's world position
            new_root_position = [
                self.motion[frame, new_root_channels["Xposition"]],
                self.motion[frame, new_root_channels["Yposition"]],
                self.motion[frame, new_root_channels["Zposition"]],
            ]

            # Subtract the new root's position from all joints
            for joint_name, channels in self.joint_channel_map.items():
                for i, axis in enumerate(["Xposition", "Yposition", "Zposition"]):
                    self.motion[frame, channels[axis]] -= new_root_position[i]

        # Step 3: Update the hierarchy
        old_root_name = self.root_joint
        self.root_joint = new_root

        # Adjust parent-child relationships
        for joint in self.hierarchy:
            if joint["name"] == old_root_name:
                joint["parent"] = new_root  # Old root becomes a child of the new root
            elif joint["name"] == new_root:
                joint["parent"] = None  # New root has no parent

    def get_joint_position(self, joint_name: str, frame: int) -> Optional[List[float]]:
        """
        Retrieves the position of a specific joint for a given frame.

        Args:
            joint_name (str): The name of the joint.
            frame (int): The frame number.

        Returns:
            Optional[List[float]]: The joint position as [X, Y, Z] or None if joint not found.
        """
        if joint_name not in self.joint_channel_map:
            print(f"Joint '{joint_name}' not found in the hierarchy.")
            return None

        if frame < 0 or frame >= len(self.motion):
            print(f"Frame {frame} is out of range.")
            return None

        channels = self.joint_channel_map[joint_name]
        return [
            self.motion[frame, channels.get("Xposition", -1)],
            self.motion[frame, channels.get("Yposition", -1)],
            self.motion[frame, channels.get("Zposition", -1)],
        ]

    def get_joint_rotation(self, joint_name: str, frame: int) -> Optional[List[float]]:
        """
        Retrieves the rotation of a specific joint for a given frame.

        Args:
            joint_name (str): The name of the joint.
            frame (int): The frame number.

        Returns:
            Optional[List[float]]: The joint rotation as [Xrotation, Yrotation, Zrotation] or None if joint not found.
        """
        if joint_name not in self.joint_channel_map:
            print(f"Joint '{joint_name}' not found in the hierarchy.")
            return None

        if frame < 0 or frame >= len(self.motion):
            print(f"Frame {frame} is out of range.")
            return None

        channels = self.joint_channel_map[joint_name]
        return [
            self.motion[frame, channels.get("Xrotation", -1)],
            self.motion[frame, channels.get("Yrotation", -1)],
            self.motion[frame, channels.get("Zrotation", -1)],
        ]

    def compute_relative_positions(self):
        """
        Updates motion data to make all joint positions relative to the current root joint.
        """
        root_channels = self.joint_channel_map[self.root_joint]
        for frame in range(len(self.motion)):
            root_position = [
                self.motion[frame, root_channels["Xposition"]],
                self.motion[frame, root_channels["Yposition"]],
                self.motion[frame, root_channels["Zposition"]],
            ]

            # Subtract root position from all joints
            for joint_name, channels in self.joint_channel_map.items():
                for i, axis in enumerate(["Xposition", "Yposition", "Zposition"]):
                    self.motion[frame, channels[axis]] -= root_position[i]
