import pytest
import numpy as np
from BVH.bvh_to_h5 import read_bvh_file, process_bvh_lines, parse_bvh, save_to_hdf5
import h5py

# Sample BVH content for testing
SAMPLE_BVH_CONTENT = \
"""ROOT Hips
{
    OFFSET 0.00 0.00 0.00
    CHANNELS 6 Xposition Yposition Zposition Zrotation Xrotation Yrotation
    JOINT Spine
    {
        OFFSET 0.00 10.00 0.00
        CHANNELS 3 Xposition Yposition Zposition Zrotation Xrotation Yrotation
        End Site
        {
            OFFSET 0.00 5.00 0.00
        }
    }
}
MOTION
Frames: 2
Frame Time: 0.033
0.0 0.0 0.0 0.0 0.0 0.0
10.0 20.0 30.0 5.0 15.0 25.0

"""

@pytest.fixture
def mock_bvh_file(tmp_path):
    """
    Create a mock BVH file in a temporary directory.
    """
    mock_file = tmp_path / "test.bvh"
    mock_file.write_text(SAMPLE_BVH_CONTENT)
    return mock_file

def test_read_bvh_file(mock_bvh_file):
    """
    Test the `read_bvh_file` function to ensure it reads file content correctly.
    """
    lines = read_bvh_file(str(mock_bvh_file))
    assert len(lines) == len(SAMPLE_BVH_CONTENT.splitlines()), "Number of lines should match the sample content"
    assert lines[0] == "ROOT Hips", "First line should match the expected content"
    assert lines[-1] == "", "Last line should match the expected content"

def test_process_bvh_lines():
    """
    Test the `process_bvh_lines` function to ensure it processes lines correctly.
    """
    lines = SAMPLE_BVH_CONTENT.splitlines()
    result = process_bvh_lines(lines)
    
    # Expected hierarchy
    expected_hierarchy = [
        {"name": "Hips", "parent": None, "offset": [0.0, 0.0, 0.0]},
        {"name": "Spine", "parent": "Hips", "offset": [0.0, 10.0, 0.0]},
        {"name": "Spine_End", "parent": "Spine", "offset": [0.0, 5.0, 0.0]}
    ]
    
    # Expected channels
    expected_channels = [
        "Xposition", "Yposition", "Zposition", "Zrotation", "Xrotation", "Yrotation",
        "Xposition", "Yposition", "Zposition", "Zrotation", "Xrotation", "Yrotation"
    ]
    
    # Expected motion
    expected_motion = np.array([
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [10.0, 20.0, 30.0, 5.0, 15.0, 25.0]
    ])
    
    assert result["hierarchy"] == expected_hierarchy, "Hierarchy should match expected structure"
    assert result["channels"] == expected_channels, "Channels should match expected structure"
    np.testing.assert_array_equal(result["motion"], expected_motion, "Motion data should match expected structure")

def test_parse_bvh(mock_bvh_file):
    """
    Test the `parse_bvh` function to ensure it integrates reading and processing correctly.
    """
    result = parse_bvh(str(mock_bvh_file))
    
    # Expected hierarchy
    expected_hierarchy = [
        {"name": "Hips", "parent": None, "offset": [0.0, 0.0, 0.0]},
        {"name": "Spine", "parent": "Hips", "offset": [0.0, 10.0, 0.0]},
        {"name": "Spine_End", "parent": "Spine", "offset": [0.0, 5.0, 0.0]}
    ]
    
    # Expected channels
    expected_channels = [
        "Xposition", "Yposition", "Zposition", "Zrotation", "Xrotation", "Yrotation",
        "Xposition", "Yposition", "Zposition", "Zrotation", "Xrotation", "Yrotation"
    ]
    
    # Expected motion
    expected_motion = np.array([
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [10.0, 20.0, 30.0, 5.0, 15.0, 25.0]
    ])
    
    assert result["hierarchy"] == expected_hierarchy, "Hierarchy should match expected structure"
    assert result["channels"] == expected_channels, "Channels should match expected structure"
    np.testing.assert_array_equal(result["motion"], expected_motion, "Motion data should match expected structure")


@pytest.fixture
def mock_parsed_data():
    """
    Fixture that provides mock parsed BVH data.
    """
    return {
        "hierarchy": [
            {"name": "Hips", "parent": None, "offset": [0.0, 0.0, 0.0]},
            {"name": "Spine", "parent": "Hips", "offset": [0.0, 10.0, 0.0]},
            {"name": "Neck", "parent": "Spine", "offset": [0.0, 5.0, 0.0]}
        ],
        "motion": np.array([
            [0.0, 0.0, 0.0, 0.0],
            [10.0, 10.0, 10.0, 10.0]
        ]),
        "channels": ["Xposition", "Yposition", "Zposition", "Xrotation"]
    }

@pytest.fixture
def temp_hdf5_file(tmp_path):
    """
    Fixture that creates a temporary HDF5 file.
    """
    return tmp_path / "test_output.h5"

def test_save_to_hdf5(mock_parsed_data, temp_hdf5_file):
    """
    Test the save_to_hdf5 function to ensure data is correctly written to an HDF5 file.
    """
    # Save mock parsed data to the HDF5 file
    save_to_hdf5(mock_parsed_data, temp_hdf5_file)

    # Open the HDF5 file and verify its contents
    with h5py.File(temp_hdf5_file, 'r') as hdf:
        # Verify hierarchy group
        assert "hierarchy" in hdf, "Hierarchy group missing in HDF5 file"
        hierarchy_group = hdf["hierarchy"]

        for i, joint in enumerate(mock_parsed_data["hierarchy"]):
            joint_group = hierarchy_group[f"joint_{i}"]
            assert joint_group.attrs["name"] == joint["name"], f"Joint name mismatch for joint_{i}"
            assert joint_group.attrs["parent"] == (joint["parent"] if joint["parent"] else "None"), f"Parent mismatch for joint_{i}"
            np.testing.assert_array_equal(joint_group.attrs["offset"], joint["offset"]), f"Offset mismatch for joint_{i}"

        # Verify motion data
        assert "motion_data" in hdf, "Motion data missing in HDF5 file"
        np.testing.assert_array_equal(hdf["motion_data"][:], mock_parsed_data["motion"])

        # Verify channels
        assert "channels" in hdf, "Channels dataset missing in HDF5 file"
        assert list(hdf["channels"][:]) == [np.bytes_(ch) for ch in mock_parsed_data["channels"]]