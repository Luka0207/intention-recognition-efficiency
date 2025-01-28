# Anvil File Handler

`AnvilFileHandler` is a Python class for handling `.anvil` files and their associated XML-based annotation specs. It provides methods to load, parse, manipulate, and save `.anvil` files, making it easier to work with annotations and track data.

## Features

- **Load `.anvil` Files**: Parse and load `.anvil` XML content.
- **Load Specs Files**: Load annotation specs for action label mappings.
- **Store Track Contents**: Extract and store track information from `.anvil` files.
- **Action Label Mapping**: Generate mappings from raw action labels to descriptive names based on specs.
- **Edit Annotations**: Modify specific annotations by ID.
- **Save Files**: Save updated `.anvil` files with modified or processed annotations.

## Usage

### Initialization
```python
from anvil_file_handler import AnvilFileHandler

handler = AnvilFileHandler(
    file_path="path/to/your/file.anvil",
    specs_path="path/to/your/specs.xml"
)
```

### Methods

#### 1. `load_file()`
Loads the `.anvil` file and parses its XML content.
```python
handler.load_file()
```

#### 2. `load_specs()`
Loads the annotation specs XML file.
```python
handler.load_specs()
```

#### 3. `get_action_label_mapping()`
Generates a dictionary mapping action labels to descriptions.
```python
mapping = handler.get_action_label_mapping()
```

#### 4. `store_track_contents(track_name: str)`
Extracts and stores the contents of a specified track.
```python
handler.store_track_contents("Action Label")
```

#### 5. `display_action_label()`
Prints the contents of the "Action Label" track.
```python
handler.display_action_label()
```

#### 6. `edit_annotation(annotation_id: str, new_content: str)`
Edits a specific annotation by its ID.
```python
success = handler.edit_annotation("1", "New Content")
```

#### 7. `save_file(output_path: str)`
Saves the current state of the XML tree to a file.
```python
handler.save_file("path/to/output/file.anvil")
```

## Testing

This project includes a test suite written with `pytest`. To run the tests:

1. Install `pytest`:
   ```bash
   pip install pytest
   ```

2. Run the tests:
   ```bash
   pytest
   ```

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Acknowledgments

- **Python XML Library**: For providing robust XML parsing tools.
- **Pytest**: For simplifying the testing process.

---

Feel free to customize this `README.md` to suit your specific project needs.
