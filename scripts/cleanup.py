#!/usr/bin/env python3
"""
Clean up script for removing unwanted cache and temporary files.

This script recursively removes Python cache files, pytest cache, and other temporary files
from the project directory.
"""

import os
import shutil
from pathlib import Path
from typing import List, Set

# Directories and files to delete
TARGETS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".coverage",
    "htmlcov",
    ".ipynb_checkpoints",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".Python",
    "build/",
    "develop-eggs/",
    "dist/",
    "downloads/",
    "eggs/",
    ".eggs/",
    "lib/",
    "lib64/",
    "parts/",
    "sdist/",
    "var/",
    "wheels/",
    "*.egg-info/",
    ".installed.cfg",
    "*.egg",
    ".coverage.*",
    "coverage.xml",
    "*.cover",
    ".hypothesis/",
    ".mypy_cache/",
    ".tox/",
    ".venv",
    "venv/",
    "ENV/",
    "env.bak/",
    "venv.bak/",
}

def find_files_to_delete(root_dir: Path) -> List[Path]:
    """Find all files and directories that match the target patterns."""
    to_delete = set()
    
    for target in TARGETS:
        # Handle directory patterns (ending with /)
        if target.endswith('/'):
            for dirpath, dirnames, _ in os.walk(root_dir):
                if target.rstrip('/') in dirnames:
                    to_delete.add(Path(dirpath) / target.rstrip('/'))
        # Handle file patterns
        elif '*' in target:
            for file_path in root_dir.rglob(target):
                to_delete.add(file_path)
        # Handle exact matches
        else:
            for file_path in root_dir.rglob(target):
                if file_path.name == target or file_path.name.startswith(target):
                    to_delete.add(file_path)
    
    # Convert to list and sort for consistent output
    return sorted(to_delete, key=lambda x: (x.is_file(), str(x)))

def delete_paths(paths: List[Path]) -> None:
    """Delete the given paths, printing what's being deleted."""
    for path in paths:
        try:
            if path.is_file() or path.is_symlink():
                print(f"Deleting file: {path}")
                path.unlink()
            elif path.is_dir():
                print(f"Deleting directory: {path}")
                shutil.rmtree(path)
        except Exception as e:
            print(f"Error deleting {path}: {e}")

def main() -> None:
    """Main function to run the cleanup."""
    # Get the project root directory (where this script is located)
    project_root = Path(__file__).parent.parent.resolve()
    print(f"Cleaning up project at: {project_root}")
    
    # Find all files and directories to delete
    to_delete = find_files_to_delete(project_root)
    
    if not to_delete:
        print("No cache or temporary files found to clean up.")
        return
    
    # Show what will be deleted
    print("\nThe following files and directories will be deleted:")
    for path in to_delete:
        print(f"  - {path.relative_to(project_root)}")
    
    # Ask for confirmation
    response = input("\nAre you sure you want to delete these files? [y/N] ").strip().lower()
    if response != 'y':
        print("Cleanup cancelled.")
        return
    
    # Delete the files and directories
    print("\nStarting cleanup...")
    delete_paths(to_delete)
    print("\nCleanup complete!")

if __name__ == "__main__":
    main()
