import pytest
import xml.etree.ElementTree as ET
from data.Annotations.Anvil.AnvilFileHandler import AnvilFileHandler
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_anvil_file(tmp_path):
    """Creates a mock .anvil file for testing."""
    anvil_content = """
    <annotations>
        <track name="Meta-Action Label">
            <el index="1" start="0" end="1.5">
                <attribute name="type">[1] No action</attribute>
            </el>
            <el index="2" start="2" end="3.5">
                <attribute name="type">[2] Consult sheets</attribute>
            </el>
        </track>
    </annotations>
    """
    file_path = tmp_path / "test.anvil"
    file_path.write_text(anvil_content)
    return str(file_path)

@pytest.fixture
def mock_specs_file(tmp_path):
    """Creates a mock specs file for testing."""
    specs_content = """
    <specs>
        <valueset name="type_InternalValueType_1">
            <value-el color="#FFA500">[1] No action</value-el>
            <value-el color="#FFA500">[2] Consult sheets</value-el>
        </valueset>
    </specs>
    """
    specs_path = tmp_path / "test_specs.xml"
    specs_path.write_text(specs_content)
    return str(specs_path)

def test_load_file(mock_anvil_file):
    """Test the loading of the .anvil file."""
    handler = AnvilFileHandler(file_path=mock_anvil_file, specs_path=None)
    assert handler.tree is not None
    assert handler.root is not None

def test_load_specs(mock_anvil_file, mock_specs_file):
    """Test the loading of the specs file."""
    handler = AnvilFileHandler(file_path=mock_anvil_file, specs_path=mock_specs_file)
    assert handler.specs is not None

def test_get_action_label_mapping(mock_anvil_file, mock_specs_file):
    """Test the action label mapping generation."""
    handler = AnvilFileHandler(file_path=mock_anvil_file, specs_path=mock_specs_file)
    mapping = handler.get_action_label_mapping()
    assert mapping == {
        "[1] No action": "No action",
        "[2] Consult sheets": "Consult sheets",
    }

def test_store_track_contents(mock_anvil_file, mock_specs_file):
    """Test storing track contents."""
    handler = AnvilFileHandler(file_path=mock_anvil_file, specs_path=mock_specs_file)
    handler.store_track_contents("Meta-Action Label")
    assert "Meta-Action Label" in handler.track_contents
    assert len(handler.track_contents["Meta-Action Label"]) == 2
    assert handler.track_contents["Meta-Action Label"] == [
        {
            "index": "1",
            "start_time": "0",
            "end_time": "1.5",
            "type": "[1] No action",
        },
        {
            "index": "2",
            "start_time": "2",
            "end_time": "3.5",
            "type": "[2] Consult sheets",
        },
    ]

def test_edit_annotation(mock_anvil_file, mock_specs_file):
    """Test editing an annotation."""
    handler = AnvilFileHandler(file_path=mock_anvil_file, specs_path=mock_specs_file)
    result = handler.edit_annotation(annotation_id="1", new_content="Updated content")
    assert not result  # No annotation with ID "1" exists in the mock data

@patch("xml.etree.ElementTree.ElementTree.write")
def test_save_file(mock_write, mock_anvil_file, mock_specs_file):
    """Test saving the file."""
    handler = AnvilFileHandler(file_path=mock_anvil_file, specs_path=mock_specs_file)
    handler.save_file(output_path="output.anvil")
    mock_write.assert_called_once()
