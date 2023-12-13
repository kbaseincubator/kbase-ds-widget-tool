import importlib
from http import cookies
from urllib.parse import parse_qs


class WidgetError(Exception):
    pass


class PythonWidget(object):
    def __init__(self, service_module_name, name, config, widget_config, widget_module_name, title, path):
        self.service_module_name = service_module_name
        self.name = name
        self.title = title
        self.config = config
        self.widget_module_name = widget_module_name
        self.widget_config = widget_config
        self.path = path

        self.widget_mod = importlib.import_module(f"widget.widgets.{widget_module_name}.widget")

        # current_dir = os.path.dirname(os.path.realpath(__file__))

        # # Create a root path for all file access for the widget root file and all assets.
        # widget_path = os.path.abspath(os.path.join(current_dir, '../../../../widget/widgets',  path))

        # # Ensure the widget exists.
        # if not os.path.isdir(widget_path):
        #     raise WidgetError(f"The static widget path was not found: {widget_namnamee}")

        # self.widget_path = widget_path

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

        def handler(request_env):
            #
            # Parameters are extracted from the query string; the resource_path (the path
            # after the module name) may also carry parameterization, but that is up to the
            # widget itself.
            #
            query_string = request_env.get('QUERY_STRING')
            if query_string is None:
                params = {}
            else:
                params = parse_qs(query_string)

            #
            # The auth token comes from the cookie...
            #
            browser_cookie = request_env.get('HTTP_COOKIE') or ''
            cookie = cookies.SimpleCookie()
            cookie.load(browser_cookie)
            if 'kbase_session' in cookie:
                token = cookie['kbase_session'].value
            else:
                token = None

            widget = self.widget_mod.Widget(
                service_module_name=self.service_module_name,
                widget_module_name=self.widget_module_name, 
                token=token, 
                params=params, 
                rest_path=rest_path, 
                config=self.config,
                widget_config=self.widget_config)

            content = widget.render()

            return "200 OK", "text/html; charset=utf-8", content

        return handler(request_env)

    