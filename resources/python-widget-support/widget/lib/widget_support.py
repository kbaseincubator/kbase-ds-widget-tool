import os
import re

import yaml
from widget.handlers.assets import Assets
from widget.handlers.python_widget import PythonWidget
from widget.handlers.static_widget import StaticWidget
from widget.lib.widget_error import WidgetError


def not_found(widget_name):
    status = '404 Not Found'
    content_type = 'text/plain; charset=utf-8'
    content = f"Widget Not Found: {widget_name}".encode('utf-8')
    return status, content_type, content

GLOBAL_WIDGET_SUPPORT = None


class WidgetSupport(object):
    WIDGETS = {}
    def __init__(self, service_config, service_package_name, service_instance_hash, init_file=None):
        self.service_config = service_config
        self.service_instance_hash = service_instance_hash

        # TODO: remove that parameter, as it is now in the config
        self.service_package_name = service_package_name

        self.widget_config = self.load_config()

        dev_env_var = os.environ.get('DEV') or ''
        self.runtime_mode = "DEVELOPMENT" if dev_env_var.lower().startswith('t') else "PRODUCTION"

        print(f'!! RUNTIME MODE: {self.runtime_mode}')
        
        if self.runtime_mode == "DEVELOPMENT":
            self.base_path = ""
        else:
            self.base_path = f"/dynserv/{service_instance_hash}.{service_package_name}"
            
        result = re.match(r'^(.+)://(.+?)(?:/.*)?$', service_config['kbase-endpoint'])

        protocol = result.group(1)
        hostname = result.group(2)
        origin = f'{protocol}://{hostname}'

        #
        # UI origin is designed to match the kbase deploy environment, not this service,
        # which may be running locally.
        #
        if origin == 'https://kbase.us':
            self.ui_origin = 'https://narrative.kbase.us'
            self.deploy_environment = 'prod'
        else:
            self.ui_origin = origin
            deploy_env, _, _ = hostname.split('.')
            self.deploy_environment = deploy_env

        #
        # Here we create a set of origins and urls that point back to this service.
        #

        if self.runtime_mode == "DEVELOPMENT":
            #
            # If running locally, the url should be something like http://localhost:5100
            #

            # 
            # TODO: need to get the local url somehow; can we assume it is
            # http://localhost? THen all we need is the port
            #
            port = 5100
            self.service_origin = f'http://localhost:{port}'
            self.service_url = self.service_origin + self.base_path
        else:
            #
            # If not local, then the base origin is still the deploy env.
            #
            self.service_origin = origin
            self.service_url = origin + self.base_path

        self.initialize_widgets()

    def load_config(self):
        with open(os.path.join(os.path.dirname(__file__), '../../../widget/widgets.yml'), 'r', encoding="utf-8") as fin:
            return yaml.safe_load(fin)

    def initialize_widgets(self):
        for widget in self.widget_config['widgets']:
            if widget['type'] == "assets":
                self.add_assets_widget(widget['name'])
            elif widget['type'] == "static":
                self.add_static_widget(
                    widget['name'],
                    path=widget.get('path') or widget['name'],
                    title=widget.get('title'),
                    description=widget.get('description')
                    )
            elif widget['type'] == "python":
                self.add_python_widget(
                    widget['name'], 
                    package=widget.get('package') or widget['name'], 
                    title=widget.get('title'),
                    description=widget.get('description')
                )
            else:
                raise WidgetError(
                    title= "Invalid Widget Type in Config",
                    code= "invalid-widget-config",
                    message = f"The widget type {widget['type']} is not supported."
                )

    def get_widget_config(self):
        return {
            "runtime_mode": self.runtime_mode,
            "base_path": self.base_path,
            "ui_origin": self.ui_origin,
            "deploy_environment": self.deploy_environment,
            "service_origin": self.service_origin,
            "service_url": self.service_url
        }

    def has_widget(self, name):
        return name in self.WIDGETS

    def get_widget(self, name):
        return self.WIDGETS[name]

    def add_assets_widget(self, name, title=None, path=None):
        widget_instance = Assets(
            service_package_name = self.service_package_name,
            name = name,
            path = path or name,
            title = title or name.title(),
            service_config = self.service_config,
            widget_config = self.get_widget_config()
        )

        self.WIDGETS[name] = widget_instance

    def add_static_widget(self, name, title=None, path=None, description=None):

        widget_instance = StaticWidget(
            service_package_name = self.service_package_name,
            name = name,
            path = path or name,
            title = title or name.title(),
            description = description,
            service_config = self.service_config,
            widget_config = self.get_widget_config()
        )

        self.WIDGETS[name] = widget_instance

    def add_python_widget(self, name, package=None, title=None, path=None, description=None):

        widget_instance = PythonWidget(
            service_package_name = self.service_package_name,
            name = name,
            path = path or name,
            title = title or name.title(),
            description = description, 
            service_config = self.service_config,
            widget_package_name = package,
            widget_config = self.get_widget_config()
        )

        self.WIDGETS[name] = widget_instance


    def run_widget(self, widget_name, widget_path, request_env):
        # our new widget objects; already initialized for this environment.
        if self.has_widget(widget_name):
            widget = self.get_widget(widget_name)
            return widget.handle(widget_path, request_env)
        else:
            return not_found(widget_name)

    def handle_widget(self, request_env):
        path = request_env['PATH_INFO']
        result = re.match(r'^/widgets/(.*?)(?:/(.*))?$', path)

        widget_name = result.group(1)
        widget_path = result.group(2)

        status, content_type, content = self.run_widget(widget_name, widget_path, request_env)

        response_headers = [
            ('content-type', content_type),
            ('content-length', str(len(content)))]

        return status, response_headers, content

    def set_global(self):
        global GLOBAL_WIDGET_SUPPORT
        GLOBAL_WIDGET_SUPPORT = self


def handle_widget_request(http_environment):
    """
    """
    path = http_environment['PATH_INFO']

    # All widget access is rooted at /widgets.
    if not path.startswith('/widgets'):
        return None

    # Global widget support is created by the implementation module, which must itself
    # be created before the service can operate, so it is safe to assume it is
    # initialized by the time a request is handled, and this function called.
    widget_support = GLOBAL_WIDGET_SUPPORT
    if widget_support is None:
        # raise ServerError('Widget support not yet available for /widgets!')
        error_message = 'Widget support not yet available for /widgets!'
        return "500 Internal Server Error", {'content-type': 'text/plain'}, error_message

    return widget_support.handle_widget(http_environment)
