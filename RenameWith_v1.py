#v1 ds
import os
import sys
import shutil
import argparse
from datetime import datetime

def parse_args():
    parser = argparse.ArgumentParser(description="Media file organizer")
    parser.add_argument("folder", help="Source directory path")
    parser.add_argument("-b", "--base", default="Image", help="Base filename pattern")
    parser.add_argument("--dry-run", action="store_true", help="Simulate operations without making changes")
    parser.add_argument("--sort", choices=["name", "created", "modified"], default="modified",
                      help="Sorting method (default: modified time)")
    parser.add_argument("--reverse", action="store_true", help="Reverse sort order")
    parser.add_argument("--copy", action="store_true", 
                      help="Non-destructive mode: copy files instead of moving")
    return parser.parse_args()

def get_sort_key(img_path, sort_method):
    if sort_method == "name":
        return os.path.basename(img_path)
    elif sort_method == "created":
        return os.path.getctime(img_path)
    elif sort_method == "modified":
        return os.path.getmtime(img_path)
    raise ValueError(f"Unknown sort method: {sort_method}")

def main():
    args = parse_args()
    
    if not os.path.isdir(args.folder):
        print(f"Error: Folder '{args.folder}' does not exist.")
        sys.exit(1)

    # Collect files recursively with full paths
    image_extensions = ('.jpg', '.jpeg', '.png')
    file_list = []
    for root, _, files in os.walk(args.folder):
        for filename in files:
            if os.path.splitext(filename)[1].lower() in image_extensions:
                img_path = os.path.join(root, filename)
                base_name = os.path.splitext(filename)[0]
                txt_file = base_name + '.txt'
                txt_path = os.path.join(root, txt_file)
                
                file_list.append({
                    "sort_key": get_sort_key(img_path, args.sort),
                    "img_path": img_path,
                    "txt_exists": os.path.isfile(txt_path),
                    "txt_path": txt_path,
                    "original_name": filename
                })

    # Sort files
    sorted_files = sorted(file_list, 
                         key=lambda x: x["sort_key"], 
                         reverse=args.reverse)

    # Create destination folder
    dest_subfolder = "Copied" if args.copy else "Renamed"
    counter = 0
    dest_path = None
    while not dest_path:
        current_name = dest_subfolder + ('' if counter == 0 else f'.{counter}')
        test_path = os.path.join(args.folder, current_name)
        if not os.path.exists(test_path):
            dest_path = test_path
            if not args.dry_run:
                os.makedirs(dest_path)
            break
        counter += 1

    total_files = len(sorted_files)
    digits = len(str(total_files))
    txt_missing = 0
    processed = 0

    operation = "Copying" if args.copy else "Moving"
    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}{operation} {total_files} files:")
    print(f"Sort method: {args.sort}{' (reversed)' if args.reverse else ''}")
    print(f"Base name: {args.base}")
    print(f"Destination: {dest_path}\n")

    for index, file_info in enumerate(sorted_files):
        processed += 1
        number = index + 1
        new_base = f"{args.base}{number:0{digits}d}"
        img_path = file_info["img_path"]
        original_name = file_info["original_name"]
        
        # Progress feedback
        progress = (processed / total_files) * 100
        print(f"\rProcessing: {processed}/{total_files} ({progress:.1f}%)", end='', flush=True)

        # Process image file
        img_ext = os.path.splitext(original_name)[1]
        dest_img = os.path.join(dest_path, f"{new_base}{img_ext}")
        
        if not args.dry_run:
            if args.copy:
                shutil.copy2(img_path, dest_img)
            else:
                shutil.move(img_path, dest_img)

        # Process text file
        if file_info["txt_exists"]:
            txt_path = file_info["txt_path"]
            dest_txt = os.path.join(dest_path, f"{new_base}.txt")
            
            if os.path.exists(txt_path):
                if not args.dry_run:
                    if args.copy:
                        shutil.copy2(txt_path, dest_txt)
                    else:
                        shutil.move(txt_path, dest_txt)
            else:
                print(f"\nWarning: {original_name} expected corresponding TXT file but it's missing")
                txt_missing += 1
        else:
            print(f"\nWarning: {original_name} has no corresponding TXT file")
            txt_missing += 1

    # Final summary
    print("\n\nSummary:")
    print(f"Total processed: {total_files}")
    print(f"Missing text files: {txt_missing}")
    print(f"Sort method: {args.sort}{' (reversed)' if args.reverse else ''}")
    print(f"Output format: {args.base}{'#'*digits}")
    if args.dry_run:
        print("DRY RUN MODE - No files were actually changed")
    else:
        action = "copied" if args.copy else "moved"
        print(f"Files {action} to: {dest_path}")
    if args.copy:
        print("Original files remain in source directory")

if __name__ == "__main__":
    main()