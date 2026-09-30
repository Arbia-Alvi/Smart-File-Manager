# Smart File Manager Pro

Smart File Manager Pro is a Python-based file management tool that automatically scans files, organizes them into category folders, moves files safely, detects duplicate files using SHA-256 hashing, stores move history in SQLite, and provides an Undo system.

## Features

* File scanning
* Extension-based file categorization
* Automatic category folder creation
* Automatic file organization
* SHA-256 duplicate detection
* Duplicate detection using file extension, file size, and SHA-256 hash
* Safe/Dry Run mode
* Collision handling for existing filenames
* Undo system
* SQLite move history
* Logging system
* Error handling
* Command-line interface (CLI)
* Automated tests using pytest
* Custom categories and file organization rules

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
```

### 2. Open the project folder

```bash
cd Smart_File_Manager
```

### 3. Install pytest

Pytest is required for running the automated test suite.

```bash
py -m pip install pytest
```

## Usage

Smart File Manager Pro uses command-line commands.

### Scan and organize files

```bash
py src/scanner.py scan
```

This scans the files in the project folder, determines their categories, creates the required category folders, and moves the files safely.

### View move history

```bash
py src/scanner.py history
```

This displays the file move history stored in the SQLite database.

### Undo the last move

```bash
py src/scanner.py undo
```

This restores the most recently moved file to its original location.

## Project Structure

```text
Smart_File_Manager/
│
├── config/
│   └── categories.json
│
├── src/
│   └── scanner.py
│
├── tests/
│   └── test_scanner.py
│
├── README.md
├── .gitignore
├── file_history.db
└── file_manager.log
```

Category folders such as `Documents`, `Images`, `Music`, `Videos`, `Archives`, `Python`, and `Other` are created automatically when required.

## Testing

The project includes automated tests using pytest.

Run the complete test suite with:

```bash
py -m pytest
```

The tests cover important functionality such as:

* Unique filename generation
* Filename collision handling
* SHA-256 file hashing
* File category detection
* Safe/Dry Run mode
* File organization
* Collision handling during file organization
* Duplicate detection
* SQLite move history

## How It Works

1. The program scans files in the selected folder.
2. It checks each file's extension.
3. The extension is matched with the rules in `config/categories.json`.
4. The appropriate category folder is created automatically.
5. A unique destination filename is generated if a filename collision occurs.
6. The file is moved to its category folder.
7. Successful file moves are recorded in the SQLite history database.
8. Files inside the `Documents` folder are checked for potential duplicates.
9. Duplicate detection uses file extension, file size, and SHA-256 hash.
10. The Undo command can restore the most recent recorded move.

## Duplicate Detection

Smart File Manager Pro uses three checks when identifying duplicate files:

* File extension
* File size
* SHA-256 hash

Files are considered duplicates only when all three values match.

SHA-256 provides a content-based comparison, helping the program identify files with identical content even when their filenames are different.

## Safe/Dry Run Mode

Dry Run mode allows users to preview file operations without actually moving files.

When Dry Run mode is enabled, the program shows which files would be moved while keeping the original files in their current locations.

This helps users review planned file operations before performing them.

## Collision Handling

When a file with the same name already exists in the destination folder, the program does not overwrite the existing file.

Instead, it generates a unique filename.

For example:

```text
report.pdf
report_1.pdf
report_2.pdf
```

If both `report.pdf` and `report_1.pdf` already exist, the next file can be saved as `report_2.pdf`.

## Undo System

The Undo system allows the most recent recorded file move to be reversed.

When a file is successfully moved, its original path and new path are stored in the SQLite history database.

The Undo command uses this information to move the file back to its original location.

Example:

```bash
py src/scanner.py undo
```

## SQLite History

Smart File Manager Pro uses SQLite to store file move history.

The database stores information including:

* Move ID
* Original file path
* New file path
* Move time

This history is used by the History and Undo commands.

View the stored history with:

```bash
py src/scanner.py history
```

## Logging

The program uses Python's logging system to record important events.

The log file is:

```text
file_manager.log
```

Logging records events such as:

* File moves
* Undo operations
* File operation errors

## Error Handling

File operations are protected with error handling so that an individual file operation failure does not unnecessarily stop the entire program.

Errors are recorded in the log file for troubleshooting.

## Custom Categories

File categories are stored in:

```text
config/categories.json
```

This allows file extension rules to be customized without changing the main Python code.

Example:

```json
{
    ".jpg": "Images",
    ".pdf": "Documents",
    ".mp3": "Music",
    ".mp4": "Videos",
    ".zip": "Archives",
    ".py": "Python"
}
```

## Requirements

* Python 3
* Windows operating system
* pytest for running automated tests

## Future Improvements

Possible future improvements include:

* Graphical User Interface (GUI)
* More advanced custom organization rules
* Recursive scanning of subfolders
* More advanced duplicate management
* Configurable scan locations
* Additional CLI options
* Backup and restore functionality
* Improved reporting and statistics


## About This Project

Smart File Manager Pro is a Python learning and portfolio project focused on practical file organization, duplicate detection, safe file operations, SQLite history, command-line functionality, and automated testing with pytest.
 

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.



