import os
import shutil
import sys

def delete_pycache(path, exclude_dirs=None):
    """
    Traverses the directory tree starting at 'path' and deletes all
    directories named '__pycache__', excluding those specified in
    'exclude_dirs'.  Handles errors during directory removal and
    reports them to the user.

    Args:
        path (str): The path to start the traversal from.
        exclude_dirs (list, optional): A list of directory names to exclude
            from the deletion process.  Defaults to None.
    """
    # Ensure the path exists
    if not os.path.exists(path):
        print(f"Error: Path '{path}' does not exist.")
        sys.exit(1)

    if exclude_dirs is None:
        exclude_dirs = []

    # Normalize exclude_dirs to a set of clean names
    exclude_dirs = set(d.strip() for d in exclude_dirs) if exclude_dirs else set()

    for dirpath, dirnames, filenames in os.walk(path):
        # Skip traversal into excluded dirs
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

        if '__pycache__' in dirnames:
            pycache_path = os.path.join(dirpath, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                # print(f"Deleted: {pycache_path}")
            except OSError as e:
                print(f"Error deleting {pycache_path}: {e}")
    print("Finished processing.")




if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <path>")
        print("  <path> is the path to start the traversal from.")
        sys.exit(1)

    target_path = sys.argv[1]
    # Define the list of directories to exclude here
    exclude_dirs = ['env', 'venv', 'node_modules',"_gingerjs","site-packages"]  # Add your directories to exclude here
    delete_pycache(target_path, exclude_dirs)
