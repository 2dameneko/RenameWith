#v2 qw
import os
import sys
import shutil
import argparse

def create_output_folder(base_dir, copy_mode):
    """Create a unique output folder named 'Renamed.x' or 'Copied.x'."""
    folder_type = "Copied" if copy_mode else "Renamed"
    count = 0
    while True:
        new_dir = os.path.join(base_dir, f'{folder_type}{count if count else ""}')
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
    parser = argparse.ArgumentParser(description="Rename image files and corresponding .txt files.")
    parser.add_argument("folder", help="Folder containing image files")
    parser.add_argument("--base", default="Image", help="Base name for renaming (default: Image)")
    parser.add_argument("--copy", action="store_true", help="Copy instead of move files")
    parser.add_argument("--sort", choices=["name", "created", "modified"], default="modified", 
                        help="Sort files by name, creation time, or modification time")
    parser.add_argument("--reverse", action="store_true", help="Reverse sort order")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without modifying files")
    parser.add_argument("--quiet", action="store_true", help="Suppress output except errors")
    args = parser.parse_args()

    if not os.path.isdir(args.folder):
        print(f"Error: Folder '{args.folder}' does not exist.")
        sys.exit(1)

    # Step 1: Collect all image files (recursively) and match .txt files
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
        print("No image files found.")
        sys.exit(0)

    # Step 2: Sort files
    sorted_files = sorted(file_list, key=lambda x: get_sort_key(x, args.sort), reverse=args.reverse)

    # Step 3: Create output folder
    if not args.dry_run:
        output_dir = create_output_folder(args.folder, args.copy)
    else:
        output_dir = os.path.join(args.folder, "Output (dry-run)")

    # Step 4: Determine number of digits
    total_files = len(sorted_files)
    digits = len(str(total_files))

    # Step 5: Process files
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

    # Step 6: Final summary
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

if __name__ == "__main__":
    main()