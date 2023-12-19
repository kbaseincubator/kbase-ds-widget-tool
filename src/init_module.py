"""A module whose purpose is to initialize a KBase Dynamic Service with widget support"""

import sys

from ds_widget_tool.widget_support import WidgetSupport


def usage():
    print('init MODULE-DIRECTORY')
    print('')
    print('Initializes the given directory for Dynamic Service Widgets')
    print('')

def main():
    """
    Ensure that the first argument identifies a directory which is a valid dynamic
    service, and if so proceeds to add widget support to it.
    """
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    widget_support = WidgetSupport(
        sdk_module_directory=sys.argv[1]
    )
    widget_support.add_widget_support()
    print()


if __name__ == '__main__':
    main()
