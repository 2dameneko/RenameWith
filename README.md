# Image Renamer Tool

## Description
A Python script to rename image files (and their associated `.txt` caption files) in a folder, with options for copying/moving, sorting, and handling missing text files. This can be useful for renaming renumbered image files together with text description files of the same name, for example in a training image dataset.

## Features
- ? **Rename** image files sequentially with customizable base name
- ? **Copy or Move** files to a new output folder
- ? **Move Pairs** without renaming to preserve original filenames
- ? **Sort** files by name, creation time, or modification time
- ? **Warn** about missing corresponding `.txt` files
- ? **Dry-run** mode to simulate operations safely
- ? **Progress tracking** and summary output

## Usage
```bash
python rename_images.py <folder> [options]
```

### Options
| Flag            | Description                          | Default |
|-----------------|--------------------------------------|---------|
| `--base NAME`   | Base name for renamed files          | `Image` |
| `--copy`        | Copy files instead of moving         | Off     |
| `--sort TYPE`   | Sort by: `name`, `created`, `modified` | `modified` |
| `--reverse`     | Reverse sort order                   | Off     |
| `--dry-run`     | Simulate without modifying files     | Off     |
| `--quiet`       | Suppress progress output             | Off     |
| `--move-pairs`  | Move matching image-txt pairs without renaming | Off |

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

4. **Move image-txt pairs without renaming**
   ```bash
   python rename_images.py images_folder --move-pairs
   ```

5. **Copy image-txt pairs without renaming**
   ```bash
   python rename_images.py images_folder --move-pairs --copy
   ```

## Workflow
1. **Standard Mode** (when `--move-pairs` not used):
   - Recursively finds all images in specified folder
   - Creates output folder (`Renamed`/`Copied` with numeric suffix)
   - Sorts files by selected method
   - Applies sequential numbering with leading zeros (e.g., `Image001.jpg`)
   - Processes associated `.txt` files alongside images

2. **Move-Pairs Mode** (when `--move-pairs` is used):
   - Identifies image-txt pairs with matching base names
   - Creates output folder (`MovedPairs`/`CopiedPairs` with numeric suffix)
   - Moves/copies only complete pairs to the output folder
   - Preserves original filenames
   - Leaves unpaired files in their original locations
   - Skips pairs that would cause filename conflicts

## Output Structure
### Standard Mode
```
source_folder/
├── Renamed/              # or Copied
│   ├── Image001.jpg
│   ├── Image001.txt      # optional
│   ├── Image002.jpg
│   └── ...
└── source images...      # original files
```

### Move-Pairs Mode
```
source_folder/
+-- MovedPairs/           # or CopiedPairs
�   +-- original_name1.jpg
�   +-- original_name1.txt
�   +-- another_image.jpg
�   +-- another_image.txt
�   L-- ...
L-- unpaired images...    # images without matching .txt
L-- unpaired texts...     # .txt files without matching images
```

## Notes
- **Safety First**: Always verify with `--dry-run` before executing
- **Sorting**: 
  - `modified` = last edited time
  - `created` = file creation time (OS-dependent)
- **Missing Text Files**: Listed in final summary when detected in standard mode
- **Output Location**: New folder created inside source directory
- **Duplicate Filenames**: In move-pairs mode, pairs that would cause duplicate filenames in the target folder are skipped
- **Unpaired Files**: In move-pairs mode, files without matching pairs remain in their original locations

## Requirements
- Python 3.6+ (standard library only - no external dependencies)

## License
[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)
