import numpy as np
import pytest
from data.processed.Skeleton import Skeleton

@pytest.fixture
def mock_hdf5_data():
    """
    Fixture for mock HDF5 data.
    """
    return {
        "hierarchy": [
            {"name": "Hips", "parent": None, "offset": [0.0, 0.0, 0.0]},
            {"name": "Spine", "parent": "Hips", "offset": [0.0, 10.0, 0.0]},
            {"name": "Neck", "parent": "Spine", "offset": [0.0, 5.0, 0.0]}
        ],
        "motion": np.array([
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 10.0, 10.0, 10.0, 0.0, 0.0, 0.0, 20.0, 20.0, 20.0, 0.0, 0.0, 0.0],
            [1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 11.0, 11.0, 11.0, 0.0, 0.0, 0.0, 21.0, 21.0, 21.0, 0.0, 0.0, 0.0]
        ]),
        "channels": ["Xposition", "Yposition", "Zposition", "Xrotation", "Yrotation", "Zrotation"] * 3
    }

def test_initial_root(mock_hdf5_data):
    skeleton = Skeleton(mock_hdf5_data)
    assert skeleton.root_joint == "Hips"
    assert skeleton.get_joint_position("Hips", 0) == [0.0, 0.0, 0.0]

def test_set_new_root(mock_hdf5_data):
    skeleton = Skeleton(mock_hdf5_data)
    skeleton.set_new_root("Spine")
    assert skeleton.root_joint == "Spine"
    assert skeleton.hierarchy[0]["parent"] == "Spine"

def test_relative_positions(mock_hdf5_data):
    skeleton = Skeleton(mock_hdf5_data)
    skeleton.compute_relative_positions()
    hips_position = skeleton.get_joint_position("Hips", 0)
    assert hips_position == [0.0, 0.0, 0.0]

def test_joint_rotation(mock_hdf5_data):
    skeleton = Skeleton(mock_hdf5_data)
    rotation = skeleton.get_joint_rotation("Hips", 0)
    assert rotation == [0.0, 0.0, 0.0]  # Assuming rotation values in mock data

def test_compute_relative_positions(mock_hdf5_data):
    """
    Test compute_relative_positions to ensure joint positions are correctly
    transformed relative to the root joint.
    """
    skeleton = Skeleton(mock_hdf5_data)

    # Perform the relative position transformation
    skeleton.compute_relative_positions()

    # Frame 0: Expect root joint (Hips) to be [0, 0, 0], and other joints relative to it
    expected_frame_0 = {
        "Hips": [0.0, 0.0, 0.0],
        "Spine": [10.0, 10.0, 10.0],  # Relative to Hips
        "Neck": [20.0, 20.0, 20.0]   # Relative to Hips
    }

    # Frame 1: Root joint (Hips) becomes [0, 0, 0], adjust others
    expected_frame_1 = {
        "Hips": [0.0, 0.0, 0.0],
        "Spine": [10.0, 10.0, 10.0],  # Relative to Hips
        "Neck": [20.0, 20.0, 20.0]   # Relative to Hips
    }

    # Check frame 0
    for joint_name, expected_position in expected_frame_0.items():
        actual_position = skeleton.get_joint_position(joint_name, frame=0)
        np.testing.assert_allclose(actual_position, expected_position, rtol=1e-5)

    # Check frame 1
    for joint_name, expected_position in expected_frame_1.items():
        actual_position = skeleton.get_joint_position(joint_name, frame=1)
        np.testing.assert_allclose(actual_position, expected_position, rtol=1e-5)

