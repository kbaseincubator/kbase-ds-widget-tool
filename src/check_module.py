"""A module whose purpose is to allow one to verify that a given directory is a KBase Dynamic Service"""

import sys

from ds_widget_tool.widget_support import WidgetSupport


def usage():
    print("check MODULE-DIRECTORY")
    print("")
    print("Check that the given directory is a valid KBase SDK Dynamic Service ")
    print("")


def main():
    """
    Ensure that the first argument identifies a directory which is a valid dynamic
    service.
    """
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    module_directory = sys.argv[1]
    widget_support = WidgetSupport(sdk_module_directory=module_directory)
    widget_support.ensure_valid_service()
    print()


if __name__ == "__main__":
    main()
