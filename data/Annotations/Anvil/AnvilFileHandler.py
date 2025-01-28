import xml.etree.ElementTree as ET
from typing import List, Optional, Dict, Union

class AnvilFileHandler:
    def __init__(self, file_path: str, specs_path: Optional[str] = None):
        self.file_path = file_path
        self.specs_path = specs_path
        self.tree: Optional[ET.ElementTree] = None
        self.root: Optional[ET.Element] = None
        self.specs: Optional[ET.ElementTree] = None
        self.action_type_mapping: Dict[str, str] = {}
        self.track_contents: Dict[str, List[Dict[str, str]]] = {}

        self.load_file()
        if self.specs_path:
            self.load_specs()
            self.action_type_mapping = self.get_action_label_mapping()

        # Populate track contents for predefined tracks during initialization
        predefined_tracks = ["Meta-Action Label"]
        for track_name in predefined_tracks:
            self.store_track_contents(track_name)

    def load_file(self) -> None:
        """Loads the .anvil file and parses its XML content."""
        try:
            self.tree = ET.parse(self.file_path)
            self.root = self.tree.getroot()
            print(f"File '{self.file_path}' loaded successfully.")
        except Exception as e:
            print(f"Error loading file: {e}")

    def load_specs(self) -> None:
        """Loads the annotation specs XML file."""
        if not self.specs_path:
            print("No specs file provided.")
            return

        try:
            self.specs = ET.parse(self.specs_path)
            print(f"Specs file '{self.specs_path}' loaded successfully.")
        except Exception as e:
            print(f"Error loading specs file: {e}")

    def get_action_label_mapping(self) -> Dict[str, str]:
        """Returns a dictionary mapping raw action labels to descriptions from the specs."""
        if not self.specs:
            print("Specs not loaded. Please load the specs file first.")
            return {}

        action_type_mapping = {}
        for value_set in self.specs.findall(".//valueset[@name='type_InternalValueType_1']/value-el"):
            raw_description = value_set.text.strip()
            description = " ".join(raw_description.split(" ")[1:])  # Strip number and extract description
            action_type_mapping[raw_description] = description
        return action_type_mapping

    def store_track_contents(self, track_name: str) -> None:
        """Stores the contents of a specified track into a dictionary."""
        if not self.root:
            print("File not loaded. Please load the file first.")
            return

        track = self.root.find(f".//track[@name='{track_name}']")
        if not track:
            print(f"No track named '{track_name}' found in the file.")
            return

        track_contents = []
        for el in track.findall(".//el"):
            track_contents.append({
                "index": el.get("index", "No Index"),
                "start_time": el.get("start", "No Start"),
                "end_time": el.get("end", "No End"),
                "type": el.find("attribute[@name='type']").text if el.find("attribute[@name='type']") is not None else "Unknown Type"
            })

        self.track_contents[track_name] = track_contents
        print(f"Contents of track '{track_name}' stored successfully.")

    def get_track_data(self, track_name: str) -> Optional[List[Dict[str, Union[str, None]]]]:
        """Returns the contents of a specified track.

        Args:
            track_name (str): The name of the track to retrieve data from.

        Returns:
            Optional[List[Dict[str, Union[str, None]]]]: A list of dictionaries containing track data, or None if the track is not found.
        """
        if track_name in self.track_contents:
            return self.track_contents[track_name]

        print(f"Track '{track_name}' not found.")
        return None

    def display_action_label(self) -> None:
        """Displays the content of the 'Action Label' track."""
        track_contents = self.track_contents.get("Action Label", [])
        if not track_contents:
            print("No contents found for 'Action Label' track.")
            return

        print("Contents of 'Action Label' track:")
        for entry in track_contents:
            action_description = self.action_type_mapping.get(entry["type"], "Unknown Action")
            print(f"Index: {entry['index']}, Start: {entry['start_time']}, End: {entry['end_time']}, Action: {action_description}")

    def process_annotations(self) -> None:
        """Placeholder method for processing annotations.
        Implement your custom annotation processing logic here.
        """
        pass

    def edit_annotation(self, annotation_id: str, new_content: str) -> bool:
        """Edits the content of a specific annotation by its ID.

        Args:
            annotation_id (str): The ID of the annotation to edit.
            new_content (str): The new content to assign to the annotation.

        Returns:
            bool: True if the annotation was edited successfully, False otherwise.
        """
        if not self.root:
            print("File not loaded. Please load the file first.")
            return False

        annotation = self.root.find(f".//annotation[@id='{annotation_id}']")
        if annotation is not None:
            content_element = annotation.find('content')
            if content_element is not None:
                content_element.text = new_content
                print(f"Annotation {annotation_id} updated successfully.")
                return True
        print(f"Annotation {annotation_id} not found.")
        return False

    def save_file(self, output_path: str) -> None:
        """Saves the current state of the XML tree to a new file."""
        if not self.tree:
            print("No file loaded to save.")
            return

        try:
            self.process_annotations()  # Process annotations before saving
            self.tree.write(output_path, encoding='utf-8', xml_declaration=True)
            print(f"File saved successfully to '{output_path}'.")
        except Exception as e:
            print(f"Error saving file: {e}")