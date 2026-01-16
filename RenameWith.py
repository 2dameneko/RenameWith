#v3 Added move-pairs mode
import os
import sys
import shutil
import argparse
from collections import defaultdict

def create_output_folder(base_dir, folder_base):
    """Create a unique output folder with the given base name."""
    count = 0
    while True:
        suffix = str(count) if count > 0 else ""
        new_dir = os.path.join(base_dir, f'{folder_base}{suffix}')
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
            return new_dir
        count += 1

def get_sort_key(file_info, sort_method):
    """Return the appropriate sort key based on method."""
    path = file_info['img_path']
    if sort_method == "name":
        return os.path.basename(path)
    elif sort_method == "created":
        return os.path.getctime(path)
    elif sort_method == "modified":
        return os.path.getmtime(path)
    raise ValueError(f"Unknown sort method: {sort_method}")

def main():
    parser = argparse.ArgumentParser(description="Rename image files and corresponding .txt files or move pairs without renaming.")
    parser.add_argument("folder", help="Folder containing image files")
    parser.add_argument("--base", default="Image", help="Base name for renaming (default: Image)")
    parser.add_argument("--copy", action="store_true", help="Copy instead of move files")
    parser.add_argument("--sort", choices=["name", "created", "modified"], default="modified", 
                        help="Sort files by name, creation time, or modification time")
    parser.add_argument("--reverse", action="store_true", help="Reverse sort order")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without modifying files")
    parser.add_argument("--quiet", action="store_true", help="Suppress output except errors")
    parser.add_argument("--move-pairs", action="store_true", help="Move image-txt pairs without renaming (leaves unpaired files)")
    args = parser.parse_args()

    if not os.path.isdir(args.folder):
        print(f"Error: Folder '{args.folder}' does not exist.")
        sys.exit(1)

    # Handle move-pairs mode separately
    if args.move_pairs:
        process_move_pairs_mode(args)
    else:
        process_rename_mode(args)

def process_rename_mode(args):
    """Original mode: Rename and move/copy files with sequential numbering"""
    # Collect all image files (recursively) and match .txt files
    valid_extensions = {'.jpg', '.jpeg', '.png'}
    file_list = []

    for root, _, files in os.walk(args.folder):
        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            if ext in valid_extensions:
                img_path = os.path.join(root, filename)
                base_name = os.path.splitext(filename)[0]
                txt_path = os.path.join(root, f"{base_name}.txt")
                
                file_list.append({
                    'img_path': img_path,
                    'txt_exists': os.path.isfile(txt_path),
                    'txt_path': txt_path,
                    'filename': filename
                })

    if not file_list:
        if not args.quiet:
            print("No image files found.")
        sys.exit(0)

    # Sort files
    sorted_files = sorted(file_list, key=lambda x: get_sort_key(x, args.sort), reverse=args.reverse)

    # Create output folder
    if not args.dry_run:
        folder_base = "Copied" if args.copy else "Renamed"
        output_dir = create_output_folder(args.folder, folder_base)
    else:
        output_dir = os.path.join(args.folder, "Output (dry-run)")

    # Determine number of digits
    total_files = len(sorted_files)
    digits = len(str(total_files))

    # Process files
    missing_txt = []
    processed = 0

    if not args.quiet:
        print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Processing {total_files} files:")
        print(f"Sort method: {args.sort}{' (reversed)' if args.reverse else ''}")
        print(f"Copy mode: {'On' if args.copy else 'Off'}")
        print(f"Base name: {args.base}\n")

    for idx, file_info in enumerate(sorted_files, 1):
        img_path = file_info['img_path']
        filename = file_info['filename']
        base_name, ext = os.path.splitext(filename)
        
        new_name = f"{args.base}{idx:0{digits}d}"
        new_img_name = f"{new_name}{ext}"
        new_img_path = os.path.join(output_dir, new_img_name)

        # Update progress
        processed += 1
        percent = (processed / total_files) * 100
        if not args.quiet:
            print(f"\rProcessing: {processed}/{total_files} ({percent:.1f}%)", end='', flush=True)

        # Handle image file
        try:
            if not args.dry_run:
                if args.copy:
                    shutil.copy2(img_path, new_img_path)
                else:
                    shutil.move(img_path, new_img_path)
        except Exception as e:
            if not args.quiet:
                print(f"\nError processing {filename}: {e}")
            continue

        # Handle .txt file
        if file_info['txt_exists']:
            new_txt_path = os.path.join(output_dir, f"{new_name}.txt")
            try:
                if not args.dry_run:
                    if args.copy:
                        shutil.copy2(file_info['txt_path'], new_txt_path)
                    else:
                        shutil.move(file_info['txt_path'], new_txt_path)
            except Exception as e:
                if not args.quiet:
                    print(f"\nError processing {file_info['txt_path']}: {e}")
        else:
            missing_txt.append(base_name)
            if not args.quiet:
                print(f"\nWarning: {filename} has no corresponding {base_name}.txt")

    # Final summary
    if not args.quiet:
        print("\n\nSummary:")
        print(f"Base name used: {args.base}")
        print(f"Total files processed: {total_files}")
        print(f"Missing .txt files: {len(missing_txt)}")
        if missing_txt:
            print("Images without matching .txt files:")
            for name in missing_txt:
                print(f"  {name}")
        if args.dry_run:
            print("Note: This was a dry run. No files were changed.")

def process_move_pairs_mode(args):
    """New mode: Move image-txt pairs without renaming"""
    valid_extensions = {'.jpg', '.jpeg', '.png'}
    
    # Collect files by directory
    images_by_dir = defaultdict(dict)  # dir_path -> {base_name: (ext, full_path)}
    txts_by_dir = defaultdict(dict)    # dir_path -> {base_name: full_path}
    
    # First pass: collect all image and text files
    for root, _, files in os.walk(args.folder):
        for filename in files:
            full_path = os.path.join(root, filename)
            base_name, ext = os.path.splitext(filename)
            ext_lower = ext.lower()
            
            if ext_lower in valid_extensions:
                images_by_dir[root][base_name] = (ext, full_path)
            elif ext_lower == '.txt':
                txts_by_dir[root][base_name] = full_path
    
    # Identify pairs and unpaired files
    pairs = []          # List of (img_path, txt_path)
    unpaired_images = []  # Images without matching txt
    unpaired_txts = []    # Txt files without matching image
    
    # Check for pairs in each directory
    for dir_path, images in images_by_dir.items():
        txts_in_dir = txts_by_dir.get(dir_path, {})
        
        for base_name, (ext, img_path) in images.items():
            if base_name in txts_in_dir:
                txt_path = txts_in_dir[base_name]
                pairs.append((img_path, txt_path))
                # Remove matched txt to avoid duplicate processing
                del txts_in_dir[base_name]
            else:
                unpaired_images.append(img_path)
        
        # Remaining txts in this directory are unpaired
        for base_name, txt_path in txts_in_dir.items():
            unpaired_txts.append(txt_path)
    
    # Handle directories that only have txt files (no images)
    for dir_path, txts in txts_by_dir.items():
        if dir_path not in images_by_dir:
            for base_name, txt_path in txts.items():
                unpaired_txts.append(txt_path)
    
    total_pairs = len(pairs)
    if total_pairs == 0:
        if not args.quiet:
            print("No image-txt pairs found.")
        sys.exit(0)
    
    # Check for duplicate filenames in target directory
    target_filenames = set()
    valid_pairs = []
    duplicate_pairs = []
    
    for img_path, txt_path in pairs:
        img_filename = os.path.basename(img_path)
        txt_filename = os.path.basename(txt_path)
        
        if img_filename in target_filenames or txt_filename in target_filenames:
            duplicate_pairs.append((img_path, txt_path))
        else:
            valid_pairs.append((img_path, txt_path))
            target_filenames.add(img_filename)
            target_filenames.add(txt_filename)
    
    # Create output folder
    if not args.dry_run:
        folder_base = "CopiedPairs" if args.copy else "MovedPairs"
        output_dir = create_output_folder(args.folder, folder_base)
    else:
        output_dir = os.path.join(args.folder, "Output (dry-run)")
    
    # Process valid pairs
    processed = 0
    total_valid = len(valid_pairs)
    
    if not args.quiet:
        print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Moving {total_valid} image-txt pairs without renaming:")
        print(f"Mode: {'Copy' if args.copy else 'Move'}")
        print(f"Output folder: {output_dir}\n")
    
    for img_path, txt_path in valid_pairs:
        img_filename = os.path.basename(img_path)
        txt_filename = os.path.basename(txt_path)
        new_img_path = os.path.join(output_dir, img_filename)
        new_txt_path = os.path.join(output_dir, txt_filename)
        
        processed += 1
        percent = (processed / total_valid) * 100
        if not args.quiet:
            print(f"\rProcessing: {processed}/{total_valid} ({percent:.1f}%)", end='', flush=True)
        
        try:
            if not args.dry_run:
                if args.copy:
                    shutil.copy2(img_path, new_img_path)
                    shutil.copy2(txt_path, new_txt_path)
                else:
                    shutil.move(img_path, new_img_path)
                    shutil.move(txt_path, new_txt_path)
        except Exception as e:
            if not args.quiet:
                print(f"\nError processing pair ({img_filename}, {txt_filename}): {e}")
    
    # Final summary
    if not args.quiet:
        print("\n\nSummary:")
        print(f"Total image-txt pairs found: {total_pairs}")
        print(f"Successfully processed pairs: {len(valid_pairs)}")
        print(f"Skipped due to duplicate filenames: {len(duplicate_pairs)}")
        print(f"Unpaired image files left behind: {len(unpaired_images)}")
        print(f"Unpaired text files left behind: {len(unpaired_txts)}")
        
        if duplicate_pairs:
            print("\nPairs skipped due to duplicate filenames:")
            for img_path, txt_path in duplicate_pairs:
                print(f"  Image: {os.path.basename(img_path)}")
                print(f"  Text:  {os.path.basename(txt_path)}")
        
        if args.dry_run:
            print("\nNote: This was a dry run. No files were changed.")

if __name__ == "__main__":
    main()