# Processed data folder

# Skeleton

The `Skeleton` class provides tools for manipulating and analyzing skeletal motion data, specifically parsed from BVH files. It supports hierarchical structures, motion data transformations, and changing the root joint of the skeleton.

---

## Features

- Parse and manage joint hierarchy and motion data.
- Compute joint positions relative to the root joint.
- Change the root joint dynamically while preserving motion consistency.
- Retrieve both position and rotation data for joints.

---

## Installation

Ensure you have Python installed along with the required dependencies. You can install the required packages using:

```bash
pip install numpy pytest h5py
```

---

## Usage

### 1. Initializing the Skeleton Class

You can initialize the `Skeleton` class with parsed HDF5 data containing joint hierarchy, motion data, and channels:

```python
from skeleton import Skeleton

# Load parsed HDF5 data (mock example shown)
hdf5_data = {
    "hierarchy": [
        {"name": "Hips", "parent": None, "offset": [0.0, 0.0, 0.0]},
        {"name": "Spine", "parent": "Hips", "offset": [0.0, 10.0, 0.0]},
        {"name": "Neck", "parent": "Spine", "offset": [0.0, 5.0, 0.0]},
    ],
    "motion": np.array([
        [0.0, 0.0, 0.0, 10.0, 10.0, 10.0, 20.0, 20.0, 20.0],  # Frame 0
        [1.0, 1.0, 1.0, 11.0, 11.0, 11.0, 21.0, 21.0, 21.0],  # Frame 1
    ]),
    "channels": ["Xposition", "Yposition", "Zposition", "Xrotation", "Yrotation", "Zrotation"] * 3,
}

skeleton = Skeleton(hdf5_data)
```

---

### 2. Compute Relative Positions

The `compute_relative_positions()` method transforms all joint positions to be relative to the root joint for every frame.

```python
skeleton.compute_relative_positions()
```

#### **Mathematical Explanation**

For each joint \( i \) and frame \( f \), the relative position is calculated as:

\[
\mathbf{P}_i^\text{rel}(f) = \mathbf{P}_i^\text{world}(f) - \mathbf{P}_\text{root}^\text{world}(f)
\]

Where:
- \( \mathbf{P}_i^\text{world}(f) = \begin{bmatrix} X_i^\text{world}(f), Y_i^\text{world}(f), Z_i^\text{world}(f) \end{bmatrix} \) is the world position of joint \( i \) at frame \( f \).
- \( \mathbf{P}_\text{root}^\text{world}(f) \) is the world position of the root joint at frame \( f \).

The result is a new position:

\[
\mathbf{P}_i^\text{rel}(f) = \begin{bmatrix} X_i^\text{rel}(f), Y_i^\text{rel}(f), Z_i^\text{rel}(f) \end{bmatrix}
\]

For all joints and frames:

\[
\mathbf{M}^\text{rel} = \mathbf{M} - \mathbf{R}
\]

Where:
- \( \mathbf{M} \) is the motion matrix of all joints and frames.
- \( \mathbf{R} \) is a repeated matrix of the root joint's world position.

---

### 3. Change the Root Joint

You can dynamically change the root joint using the `set_new_root()` method. The method updates:
1. The hierarchy (adjusts parent-child relationships).
2. The motion data (transforms positions relative to the new root).

Example:

```python
skeleton.set_new_root("Spine")
```

---

### 4. Query Joint Data

Retrieve the position or rotation of any joint for a specific frame:

```python
# Get joint position
position = skeleton.get_joint_position("Neck", frame=0)
print(f"Position of 'Neck': {position}")

# Get joint rotation
rotation = skeleton.get_joint_rotation("Neck", frame=0)
print(f"Rotation of 'Neck': {rotation}")
```

---

## Example Use Case

Below is a complete example demonstrating the main features:

```python
from skeleton import Skeleton
import numpy as np

# Mock data
hdf5_data = {
    "hierarchy": [
        {"name": "Hips", "parent": None, "offset": [0.0, 0.0, 0.0]},
        {"name": "Spine", "parent": "Hips", "offset": [0.0, 10.0, 0.0]},
        {"name": "Neck", "parent": "Spine", "offset": [0.0, 5.0, 0.0]},
    ],
    "motion": np.array([
        [0.0, 0.0, 0.0, 10.0, 10.0, 10.0, 20.0, 20.0, 20.0],
        [1.0, 1.0, 1.0, 11.0, 11.0, 11.0, 21.0, 21.0, 21.0],
    ]),
    "channels": ["Xposition", "Yposition", "Zposition", "Xrotation", "Yrotation", "Zrotation"] * 3,
}

# Initialize the Skeleton
skeleton = Skeleton(hdf5_data)

# Compute relative positions
skeleton.compute_relative_positions()

# Change root joint
skeleton.set_new_root("Spine")

# Query joint data
print(skeleton.get_joint_position("Neck", frame=0))
print(skeleton.get_joint_rotation("Neck", frame=0))
```

---

## Tests

Comprehensive tests are provided to ensure the functionality of the `Skeleton` class. Run the tests using `pytest`:

```bash
pytest test_skeleton.py
```

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request if you'd like to improve this project.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
