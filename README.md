# Image Renamer Tool

## Description
A Python script to rename image files (and their associated `.txt` caption files) in a folder, with options for copying/moving, sorting, and handling missing text files. This can be useful for renaming renumbered image files together with text description files of the same name, for example in a training image dataset.

## Features
- 🔄 **Rename** image files sequentially with customizable base name
- 📁 **Copy or Move** files to a new output folder
- 🔍 **Sort** files by name, creation time, or modification time
- ⚠️ **Warn** about missing corresponding `.txt` files
- 🧪 **Dry-run** mode to simulate operations safely
- 📈 **Progress tracking** and summary output

## Usage
```bash
python rename_images.py <folder> [options]
```

### Options
| Flag          | Description                          | Default |
|---------------|--------------------------------------|---------|
| `--base NAME` | Base name for renamed files          | `Image` |
| `--copy`      | Copy files instead of moving         | Off     |
| `--sort TYPE` | Sort by: `name`, `created`, `modified` | `modified` |
| `--reverse`   | Reverse sort order                   | Off     |
| `--dry-run`   | Simulate without modifying files     | Off     |
| `--quiet`     | Suppress progress output             | Off     |

### Supported Formats
- Images: `.jpg`, `.jpeg`, `.png`
- Text files: `.txt` with matching base name

## Examples
1. **Basic rename with default settings**
   ```bash
   python rename_images.py images_folder
   ```

2. **Copy sorted by name in reverse order**
   ```bash
   python rename_images.py images_folder --copy --sort name --reverse
   ```

3. **Test with dry-run simulation**
   ```bash
   python rename_images.py images_folder --dry-run
   ```

## Workflow
1. **Input**: Recursively finds all images in specified folder
2. **Processing**:
   - Creates output folder (`Renamed`/`Copied` with numeric suffix)
   - Sorts files by selected method
   - Preserves original sort order if `--reverse` not specified
3. **Output**:
   - Sequential numbering with leading zeros (e.g., `Image001.jpg`)
   - Maintains original file extensions
   - Handles associated `.txt` files alongside images

## Output Structure
```
source_folder/
├── Renamed/              # or Copied
│   ├── Image001.jpg
│   ├── Image001.txt      # optional
│   ├── Image002.jpg
│   └── ...
└── source images...      # original files
```

## Notes
- **Safety First**: Always verify with `--dry-run` before executing
- **Sorting**: 
  - `modified` = last edited time
  - `created` = file creation time (OS-dependent)
- **Missing Text Files**: Listed in final summary when detected
- **Output Location**: New folder created inside source directory

## Requirements
- Python 3.6+ (standard library only - no external dependencies)

## License
MIT License (see LICENSE file) - Feel free to modify and redistribute

---

> 🔍 Tip: Use `--quiet` with automation, but check output carefully as warnings may be suppressed.
