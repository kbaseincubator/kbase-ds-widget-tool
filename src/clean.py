"""
A module whose purpose is to "clean" the tool's directory tree to ensure no unwanted
files are present. This is commonly run when updating the tool to ensure that no
development artifacts are present. Most if not all of these cases are handled by the
.gitgnore, but sometimes you want to clear these files manually, especially when
exercising the tool locally after a set of changes.

The most common case are ___pycache __ directories.
"""
import os
import shutil
import sys
from pathlib import Path

from src.utils import error_exit

DIRECTORIES_TO_CLEAN = ['__pycache__']
FILES_TO_CLEAN = ['.DS_Store']


def clean_directory(path):
    if path.name in DIRECTORIES_TO_CLEAN:
        shutil.rmtree(path)
        return True
    else:
        return False


def clean_file(path):
    if path.name in FILES_TO_CLEAN:
        path.unlink()
        return True
    else:
        return False


def clean(path):
    # Walk the entire directory tree
    for root, directories, files in os.walk(str(path)):
        for file in files:
            clean_file(Path(root).joinpath(file))
        for directory in directories:
            directory_path = Path(root).joinpath(directory)
            if not clean_directory(directory_path):
                clean(directory_path)

def usage():
    print("clean DIRECTORY")
    print("")
    print("Cleans extraneous files out of the given ds-widget-tool directory")
    print("")


def main():
    """
    Ensure that the first argument identifies a directory which is a valid dynamic
    service.
    """
    if len(sys.argv) < 2:
        usage()
        print(sys.argv)
        error_exit('Please provide the PATH to the directory to clean')

    directory_to_clean = sys.argv[1]

    # TODO: make sure directory exists.

    path_to_clean = Path(directory_to_clean)
    if not path_to_clean.is_dir():
        error_exit("The provided path is not a directory")

    clean(path_to_clean)


if __name__ == "__main__":
    main()
