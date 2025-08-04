import argparse
import glob
import os
import shutil


def export_package_code_to_txt(package_path, output_file):
    """
    Export all code from a specified Python package to a single text file.

    Parameters:
    - package_path (str): The path to the Python package.
    - output_file (str): The path to the output text file.
    """
    # Ensure the output directory exists
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Normalize the package path for consistent comparison
    package_path = os.path.abspath(package_path)

    # Use glob to iterate through all .py files in the package path
    python_files = glob.glob(os.path.join(package_path, '**', '*.py'), recursive=True)

    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Write tree structure at the beginning
        outfile.write("--- Package Tree ---\n")
        write_tree_structure(package_path, outfile)
        outfile.write("\n\n")

        for file_path in python_files:
            # Read each file's content and write to the output file
            with open(file_path, 'r', encoding='utf-8') as infile:
                # Calculate relative path from package_path for reference
                relative_path = os.path.relpath(file_path, package_path)
                # Prefix each file's content with its relative path for reference
                outfile.write(f"--- {relative_path} ---\n")
                shutil.copyfileobj(infile, outfile)
                # Separate contents of different files with blank lines
                outfile.write("\n\n")


def write_tree_structure(package_path, outfile):
    """
    Write a tree structure of the package to the output file.

    Parameters:
    - package_path (str): The path to the Python package.
    - outfile (file): The output file object.
    """
    # Get all Python files
    python_files = glob.glob(os.path.join(package_path, '**', '*.py'), recursive=True)

    # Create a set of all directories
    dirs = set()
    for file_path in python_files:
        relative_dir = os.path.dirname(os.path.relpath(file_path, package_path))
        dirs.add(relative_dir)
        # Add all parent directories
        while relative_dir:
            relative_dir = os.path.dirname(relative_dir)
            dirs.add(relative_dir)

    # Remove empty string (root directory representation)
    dirs.discard('')

    # Sort directories
    sorted_dirs = sorted(dirs)

    # Write root directory
    outfile.write(f"{os.path.basename(package_path)}/\n")

    # Write all directories and files
    all_items = []
    for dir_path in sorted_dirs:
        all_items.append((dir_path, True))  # True for directory

    for file_path in python_files:
        relative_path = os.path.relpath(file_path, package_path)
        all_items.append((relative_path, False))  # False for file

    # Sort all items
    all_items.sort(key=lambda x: x[0])

    # Write tree
    for item_path, is_dir in all_items:
        parts = item_path.split(os.sep)
        indent = "│   " * (len(parts) - 1)

        if is_dir:
            outfile.write(f"{indent}├── {parts[-1]}/\n")
        else:
            outfile.write(f"{indent}├── {parts[-1]}\n")


def main():
    # Create argument parser
    parser = argparse.ArgumentParser(description="Export all Python code from a package to a text file.")
    parser.add_argument("package_path", help="Path to the Python package.")
    parser.add_argument("output_file", help="Path to the output text file.")

    args = parser.parse_args()

    export_package_code_to_txt(args.package_path, args.output_file)
    print("Export completed.")


if __name__ == "__main__":
    main()
