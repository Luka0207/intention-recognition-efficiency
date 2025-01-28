import numpy as np
import plotly.graph_objects as go
from typing import Dict, List, Optional

"""UNNECESSARY_JOINTS = [RightHandThumb1,
                      RightHandThumb2,
                      RightHandThumb3]"""

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
        self.order = hdf5_data["order"]
        self.joint_map = {joint['name']:joint for joint in self.hierarchy}
        self.root_joint = self.hierarchy[0]["name"]
        self.joint_channel_map = self._build_joint_channel_map()
        self._update_hierarchy_with_motion()
        self.world_motion = self.compute_world_skeleton_for_frames()

    def _update_hierarchy_with_motion(self):
        for joint in self.joint_map:
            self.joint_map[joint]['world_motion'] = {'X': [], 'Y': [], 'Z': [], 'Ry': [], 'Rx': [], 'Rz': []}
            for frame in range(len(self.motion)):
                if not "_End" in joint:
                    XIndex = self.joint_channel_map[joint]['Xposition']
                    YIndex = self.joint_channel_map[joint]['Yposition']
                    ZIndex = self.joint_channel_map[joint]['Zposition']
                    RXIndex = self.joint_channel_map[joint]['Xrotation']
                    RYIndex = self.joint_channel_map[joint]['Yrotation']
                    RZIndex = self.joint_channel_map[joint]['Zrotation']
                    self.joint_map[joint]['world_motion']['X'].append(self.motion[frame][XIndex])
                    self.joint_map[joint]['world_motion']['Y'].append(self.motion[frame][YIndex])
                    self.joint_map[joint]['world_motion']['Z'].append(self.motion[frame][ZIndex])
                    self.joint_map[joint]['world_motion']['Rx'].append(self.motion[frame][RXIndex])
                    self.joint_map[joint]['world_motion']['Ry'].append(self.motion[frame][RYIndex])
                    self.joint_map[joint]['world_motion']['Rz'].append(self.motion[frame][RZIndex])

    def _update_hierarchy_with_world_positions(self):
        """
        Updates the hierarchy with the world positions of each joint.
        Adds a 'world_position' key to each joint in the hierarchy.
        """
        def compute_world_position(joint_name, joint_map):
            """
            Recursively compute the world position of a joint by summing offsets
            up to the root joint.

            Args:
                joint_name (str): The name of the joint to compute.
                joint_map (dict): A dictionary mapping joint names to their data.

            Returns:
                np.ndarray: The world position of the joint as [X, Y, Z].
            """
            joint = joint_map[joint_name]
            offset = np.array(joint["offset"])
            parent_name = joint["parent"]

            # If no parent, this is the root joint
            if parent_name is None:
                return offset

            # Recursively compute the parent's world position and add the current offset
            return compute_world_position(parent_name, joint_map) + offset
        
        # Build a mapping from joint name to joint information
        self.joint_map = {joint["name"]: joint for joint in self.hierarchy}

        # Update the hierarchy with world positions
        for joint in self.hierarchy:
            joint["world_position"] = compute_world_position(joint["name"], self.joint_map)

    def transformation_matrix_yxz(self, theta_y, theta_x, theta_z, translation):
        """
        Compute the 4x4 transformation matrix for YXZ Euler angles and a translation vector.
        :param theta_y: Rotation around the Y-axis in degrees
        :param theta_x: Rotation around the X-axis in degrees
        :param theta_z: Rotation around the Z-axis in degrees
        :param translation: Translation vector [t_x, t_y, t_z]
        :return: 4x4 transformation matrix
        """
        # Get the 3x3 rotation matrix
        R = self.rotation_matrix_yxz(theta_y, theta_x, theta_z)
        
        # Create the 4x4 transformation matrix
        T = np.eye(4)  # Start with an identity matrix
        T[:3, :3] = R  # Set the rotation part
        T[:3, 3] = translation  # Set the translation part
        
        return T
    
    def rotation_matrix_yxz(self, theta_y, theta_x, theta_z):
        """
        Compute the rotation matrix for YXZ Euler angles.
        :param theta_y: Rotation around the Y-axis in degrees
        :param theta_x: Rotation around the X-axis in degrees
        :param theta_z: Rotation around the Z-axis in degrees
        :return: 3x3 rotation matrix
        """
        # Convert angles from degrees to radians
        theta_y = np.radians(theta_y)
        theta_x = np.radians(theta_x)
        theta_z = np.radians(theta_z)

        # Rotation around Y-axis
        R_y = np.array([
            [np.cos(theta_y), 0, np.sin(theta_y)],
            [0, 1, 0],
            [-np.sin(theta_y), 0, np.cos(theta_y)]
        ])

        # Rotation around X-axis
        R_x = np.array([
            [1, 0, 0],
            [0, np.cos(theta_x), -np.sin(theta_x)],
            [0, np.sin(theta_x), np.cos(theta_x)]
        ])

        # Rotation around Z-axis
        R_z = np.array([
            [np.cos(theta_z), -np.sin(theta_z), 0],
            [np.sin(theta_z), np.cos(theta_z), 0],
            [0, 0, 1]
        ])

        # Combine the rotations in YXZ order
        R_yxz = R_y @ R_x @ R_z

        return R_yxz
    
    def compute_world_skeleton_for_frames(self):
        """
        Updates the hierarchy with the world positions of each joint.
        Adds a 'world_position' key to each joint in the hierarchy.
        """
        def compute_world_position(joint_name, joint_map, frame):
            """
            Recursively compute the world position of a joint by summing offsets
            up to the root joint.

            Args:
                joint_name (str): The name of the joint to compute.
                joint_map (dict): A dictionary mapping joint names to their data.

            Returns:
                np.ndarray: The world position of the joint as [X, Y, Z].
            """
            
            joint_names.append(joint_name)
            joint = self.joint_map[joint_name]
            translationX = np.array(joint['world_motion']["X"][frame])
            translationY = np.array(joint['world_motion']["Y"][frame])
            translationZ = np.array(joint['world_motion']["Z"][frame])
            rotationY = np.array(joint['world_motion']["Ry"][frame])
            rotationX = np.array(joint['world_motion']["Rx"][frame])
            rotationZ = np.array(joint['world_motion']["Rz"][frame])
            parent_name = joint["parent"]
            translation = np.array([translationX, translationY, translationZ])
            local_transform = self.transformation_matrix_yxz(rotationY, rotationX, rotationZ, translation)

            # If no parent, this is the root joint
            if parent_name is None:
                return local_transform

            # Recursively compute the parent's world position and add the current offset
            return compute_world_position(parent_name, joint_map, frame) @ local_transform

        # Update the hierarchy with world positions
        position_lists = []
        for frame in range(len(self.motion)):
            positions = {}
            for joint in self.hierarchy:
                joint_names = []
                if not "_End" in joint['name']:
                    new_world_transform = compute_world_position(joint["name"], self.joint_map, frame)
                    offset_homog = np.array([*joint['offset'], 1])
                    if joint['name'] == self.root_joint:
                        new_positions = new_world_transform @ np.array([0, 0, 0, 1])
                    else:
                        new_positions = new_world_transform @ offset_homog
                    positions[joint['name']] = new_positions[:3]
            position_list = []
            for joint in self.order:
                position_list = np.append(position_list, positions[joint])
            position_lists.append(position_list)
        return position_lists

    def _update_skeleton_with_framewise_world_positions(self):
        """
        Updates the motion data with the world positions of each joint for every frame.
        Adds a 'world_position' key to each joint in the hierarchy.
        """
        def compute_world_position(joint_name, joint_map, frame):
            """
            Recursively compute the world position of a joint by summing offsets
            up to the root joint.

            Args:
                joint_name (str): The name of the joint to compute.
                joint_map (dict): A dictionary mapping joint names to their data.

            Returns:
                np.ndarray: The world position of the joint as [X, Y, Z].
            """
            joint = joint_map[joint_name]
            Xindex = self.joint_channel_map[joint_name]['Xposition']
            Yindex = self.joint_channel_map[joint_name]['Yposition']
            Zindex = self.joint_channel_map[joint_name]['Zposition']
            XRindex = self.joint_channel_map[joint_name]['Xrotation']
            YRindex = self.joint_channel_map[joint_name]['Yrotation']
            ZRindex = self.joint_channel_map[joint_name]['Zrotation']
            positions = np.array([self.motion[frame][Xindex],
                                  self.motion[frame][Yindex],
                                  self.motion[frame][Zindex]])
            localT = self.transformation_matrix_yxz(self.motion[frame][YRindex],
                                               self.motion[frame][XRindex],
                                               self.motion[frame][ZRindex],
                                               positions)
            parent_name = joint["parent"]
            offset = joint['offset']
            offset_homogeneous = np.array([*offset, 1])

            # If no parent, this is the root joint
            if parent_name is None:
                return localT
            
            
            return compute_world_position(parent_name, joint_map, frame) @localT
               


            #world_transform = np.array(T) @ np.array(offset)
            #print(world_transform)

            #world_position_homogenous = world_transform @ offset_homogeneous

            # Recursively compute the parent's world position and add the current offset
            #return world_position_homogenous
        
        # Build a mapping from joint name to joint information
        self.joint_map = {joint["name"]: joint for joint in self.hierarchy}

        # Update the hierarchy with world positions
        for frame in range(len(self.motion)):
            for joint in self.hierarchy:
                if not "_End" in joint["name"]:
                    Xindex = self.joint_channel_map[joint['name']]['Xposition']
                    Yindex = self.joint_channel_map[joint['name']]['Yposition']
                    Zindex = self.joint_channel_map[joint['name']]['Zposition']
                    world_motion_transform = compute_world_position(joint["name"], self.joint_map, frame)
                    #world_position = world_motion_transform[:3]
                    offset = joint['offset']
                    offset_homogeneous = np.array([*offset, 1])
                    world_position = world_motion_transform @ offset_homogeneous
                    world_position = world_position[:3]
                    self.world_motion[frame][Xindex] = world_position[0]
                    self.world_motion[frame][Yindex] = world_position[1]
                    self.world_motion[frame][Zindex] = world_position[2]

    def _build_joint_channel_map(self) -> Dict[str, Dict[str, int]]:
        """
        Builds a map of joint names to their channel indices in the motion data.

        Returns:
            dict: A dictionary where keys are joint names and values are
                  dictionaries with keys 'Xposition', 'Yposition', 'Zposition',
                  'Yrotation', 'Xrotation', and 'Zrotation'.
        """
        joint_channel_map = {}
        current_index = 0

        for joint in self.order:
            joint_name = joint
            if not "_End" in joint_name:
                joint_channel_map[joint_name] = {}

                for channel in ["Xposition", "Yposition", "Zposition", "Yrotation", "Xrotation", "Zrotation"]:
                    if current_index < len(self.channels) and self.channels[current_index] == channel:
                        joint_channel_map[joint_name][channel] = current_index
                        current_index += 1

        return joint_channel_map
    
    def get_joint_channel_map(self) -> Dict[str, Dict[str, int]]:
        """
        Retrieve the mapping of joint names to their channel indices.

        Returns:
            dict: Joint channel map.
        """
        return self.joint_channel_map

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

        if frame < 0 or frame >= len(self.world_motion):
            print(f"Frame {frame} is out of range.")
            return None

        channels = self.joint_channel_map[joint_name]
        return [
            self.world_motion[frame, channels.get("Xposition", -1)],
            self.world_motion[frame, channels.get("Yposition", -1)],
            self.world_motion[frame, channels.get("Zposition", -1)],
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
    
    def _compute_world_positions(self) -> np.ndarray:
        """
        Computes the world positions of all joints for all frames.

        Returns:
            np.ndarray: A NumPy array of shape (frames, joints, 3) representing
                        the world positions of all joints.
        """
        num_frames = len(self.motion)
        num_joints = len(self.hierarchy)

        # Initialize a matrix to store world positions (frames x joints x 3)
        world_positions = np.zeros((num_frames, num_joints, 3))

        def compute_joint_world_position(joint_name, frame):
            """
            Recursively compute the world position of a joint.

            Args:
                joint_name (str): The name of the joint.
                frame (int): The frame index.

            Returns:
                np.ndarray: The world position of the joint as [X, Y, Z].
            """
            joint = next(j for j in self.hierarchy if j["name"] == joint_name)
            parent_name = joint["parent"]
            offset = np.array(joint["offset"])

            # Get local position from motion data
            channels = self.joint_channel_map[joint_name]
            local_position = np.array([
                self.motion[frame, channels.get("Xposition", -1)],
                self.motion[frame, channels.get("Yposition", -1)],
                self.motion[frame, channels.get("Zposition", -1)],
            ]) if "Xposition" in channels else np.zeros(3)

            # If there's no parent, this is the root joint
            if parent_name is None:
                return local_position + offset

            # Recursively compute the parent's world position
            parent_world_position = compute_joint_world_position(parent_name, frame)

            # Combine parent's world position, joint offset, and local position
            return parent_world_position + offset + local_position

        # Compute world positions for all joints and frames
        for frame in range(num_frames):
            for i, joint in enumerate(self.hierarchy):
                world_positions[frame, i, :] = compute_joint_world_position(joint["name"], frame)

        return world_positions

    def get_joint_world_position(self, joint_name: str, frame: int) -> Optional[np.ndarray]:
        """
        Retrieve the world position of a specific joint for a given frame.

        Args:
            joint_name (str): The name of the joint.
            frame (int): The frame index.

        Returns:
            np.ndarray: The world position as [X, Y, Z], or None if the joint is not found.
        """
        if joint_name not in self.joint_channel_map:
            print(f"Joint '{joint_name}' not found in the hierarchy.")
            return None

        if frame < 0 or frame >= len(self.motion):
            print(f"Frame {frame} is out of range.")
            return None

        joint_index = next(i for i, j in enumerate(self.hierarchy) if j["name"] == joint_name)
        return self.world_positions[frame, joint_index]

    def compute_relative_positions(self):
        """
        Updates motion data to make all joint positions relative to the current root joint.
        Adjusts for the BVH hierarchical structure.
        """
        # Compute world positions for all frames and joints relative to the root
        root_name = self.root_joint
        for frame in range(len(self.motion)):
            # Get the world position of the root joint for the current frame
            root_world_position = self.get_world_position(root_name, frame)

            # Update all joint positions to be relative to the root
            for joint_name in self.joint_channel_map.keys():
                world_position = self.get_world_position(joint_name, frame)
                relative_position = world_position - root_world_position

                # Update motion data for the joint
                channels = self.joint_channel_map[joint_name]
                for i, axis in enumerate(["Xposition", "Yposition", "Zposition"]):
                    if axis in channels:
                        self.motion[frame, channels[axis]] = relative_position[i]

    def plot_hierarchy_3d(self) -> "go.Figure":
        """
        Creates a 3D scatter plot of a skeleton's hierarchy using Plotly.
        Uses the offsets to determine joint positions by retracing parents to the root.

        Args:
            hierarchy (list): A list of dictionaries, where each dictionary contains:
                            - 'name': Name of the joint.
                            - 'parent': Name of the parent joint (or None for root).
                            - 'offset': List or array of [x, y, z] offsets.

        Returns:
            plotly.graph_objects.Figure: A Plotly 3D scatter plot figure.
        """
        import plotly.graph_objects as go
        import numpy as np

        def compute_world_position(joint_name, joint_map):
            """
            Recursively compute the world position of a joint by summing offsets
            up to the root joint.

            Args:
                joint_name (str): The name of the joint to compute.
                joint_map (dict): A dictionary mapping joint names to their data.

            Returns:
                np.ndarray: The world position of the joint as [X, Y, Z].
            """
            joint = joint_map[joint_name]
            offset = np.array(joint["offset"])
            parent_name = joint["parent"]

            # If no parent, this is the root joint
            if parent_name is None:
                return offset

            # Recursively compute the parent's world position and add the current offset
            return compute_world_position(parent_name, joint_map) + offset

        # Create a map for easier lookup of joint data
        joint_map = {joint["name"]: joint for joint in self.hierarchy}

        # Compute world positions for all joints
        joint_positions = {}
        joint_names = []
        for joint_name in joint_map.keys():
            joint_positions[joint_name] = joint_map[joint_name]['world_position']
            joint_names.append(joint_name)

        # Split positions into X, Y, Z coordinates
        joint_positions_array = np.array(list(joint_positions.values()))
        x, y, z = joint_positions_array[:, 0], joint_positions_array[:, 1], joint_positions_array[:, 2]

        # Create 3D scatter plot for joints
        scatter = go.Scatter3d(
            x=x, y=y, z=z,
            mode="markers",
            marker=dict(size=5, color="blue")
        )

        # Create connections between joints based on the hierarchy
        connection_lines = []
        for joint in self.hierarchy:
            parent_name = joint["parent"]
            if parent_name is not None:  # If the joint has a parent, draw a line
                joint_index = joint_names.index(joint["name"])
                parent_index = joint_names.index(parent_name)
                connection_lines.append(
                    go.Scatter3d(
                        x=[x[joint_index], x[parent_index]],
                        y=[y[joint_index], y[parent_index]],
                        z=[z[joint_index], z[parent_index]],
                        mode="lines",
                        line=dict(color="gray", width=2),
                        showlegend=False
                    )
                )

        # Combine scatter plot and connection lines
        fig = go.Figure(data=[scatter] + connection_lines)

        # Set layout for better visualization
        fig.update_layout(
            scene=dict(
                xaxis_title="X",
                yaxis_title="Y",
                zaxis_title="Z",
                aspectmode="data"
            ),
            title="3D Skeleton Hierarchy"
        )

        return fig
