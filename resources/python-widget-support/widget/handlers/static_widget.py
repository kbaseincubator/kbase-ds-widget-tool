import os
from pathlib import Path

from ..handler_utils import handle_static_file

#
# Static widgets are mapped to the filesystem.
# For now, we are doing this ourselves, but we should explore a 
# more supported way of doing this.
# 
# In the configuration, the "path" is the root path to serve static files from within
# the ./widgets directory of this repo.

class WidgetError(Exception):
    pass


class StaticWidget(object):
    def __init__(self, service_module_name, name, config, widget_config, path, title):
        self.service_module_name = service_module_name
        self.name = name
        self.title = title
        self.config = config
        self.path = path
        self.widget_config = widget_config

        current_dir = os.path.dirname(os.path.realpath(__file__))

        # Create a root path for all file access for the widget root file and all
        # assets.
        
        widgets_path = Path(os.path.join(current_dir, '../../../widget/widgets'))
        widget_path = widgets_path.joinpath(path)
        
        # os.path.abspath(os.path.join(current_dir, '../../../widget/widgets',  path))

        # Ensure the widget exists.
        if not os.path.isdir(widget_path):
            raise WidgetError(f"The static widget path was not found: {name}")

        self.widget_path = widget_path

    def handle(self, rest_path, request_env):
        """
        This is called when a path is being handled by the server which corresponds to a
        widget instance of this class. At that time, the relevant facts are those of the
        request, such as the path after the widget id, the search fragment (query
        params). The former is to be obtained from url path and is passed in as
        "rest_path", and the latter is part of the request_env, which we just take as a
        whole here.

        The implementation is split into two
        """

        def handler(_request_env):
            if rest_path is None:
                resource_path = 'index.html'
            else:
                resource_path = rest_path

            # Now we can offload to the shared static file handler.
            return handle_static_file(self.widget_path, resource_path)

        return handler(request_env)

    