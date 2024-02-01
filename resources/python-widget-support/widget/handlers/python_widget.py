import importlib
from http import cookies
from urllib.parse import parse_qs


class WidgetError(Exception):
    pass


class PythonWidget(object):
    def __init__(self, service_package_name, name, title, description, service_config, widget_config, widget_package_name, path):
        self.service_package_name = service_package_name
        self.name = name
        self.title = title
        self.description = description
        self.service_config = service_config
        self.widget_package_name = widget_package_name
        self.widget_config = widget_config
        self.path = path
        self.widget_mod = importlib.import_module(f"widget.widgets.{widget_package_name}.widget")


    def handle(self, rest_path, request_env):
        """
        This is called when a path is being handled by the server which corresponds to a
        widget instance of this class. At that time, the relevant facts are those of the
        request, such as the path after the widget id, the search fragment (query
        params). The former is to be obtained from url path and is passed in as
        "rest_path", and the latter is part of the request_env, which we just take as a
        whole here.
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
            # The auth token comes from the cookie, either `kbase_session`, available
            # for services in all environments but not in prod, in which services run on
            # kbase.us and front ends on narrative.kbase.us. In prod, the cookie
            # 'kbase_session_backup` is used.
            #
            browser_cookie = request_env.get('HTTP_COOKIE') or ''
            cookie = cookies.SimpleCookie()
            cookie.load(browser_cookie)
            if 'kbase_session' in cookie:
                token = cookie['kbase_session'].value
            elif self.widget_config.get('deploy_environment') == 'prod' and 'kbase_session_backup' in cookie:
                token = cookie['kbase_session_backup'].value
            else:
                token = None

            widget = self.widget_mod.Widget(
                service_package_name=self.service_package_name,
                widget_package_name=self.widget_package_name, 
                token=token, 
                params=params, 
                rest_path=rest_path, 
                service_config=self.service_config,
                widget_config=self.widget_config)

            content = widget.render()

            return "200 OK", "text/html; charset=utf-8", content

        return handler(request_env)
