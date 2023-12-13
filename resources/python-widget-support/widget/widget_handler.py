import os
import re

from widget.handlers.assets import Assets
from widget.handlers.python_widget import PythonWidget
from widget.handlers.static_widget import StaticWidget


def not_found(widget_name):
    status = '404 Not Found'
    content_type = 'text/plain; charset=utf-8'
    content = f"Widget Not Found: {widget_name}".encode('utf-8')
    return status, content_type, content

GLOBAL_WIDGET_SUPPORT = None


class WidgetSupport(object):
    WIDGETS = {}
    def __init__(self, config, service_module_name, git_commit_hash):
        self.config = config
        self.git_commit_hash = git_commit_hash

        # TODO: remove that parameter, as it is now in the config
        self.service_module_name = service_module_name

        dev_env_var = os.environ.get('DEV') or ''
        self.runtime_mode = "DEVELOPMENT" if dev_env_var.lower().startswith('t') else "PRODUCTION"
        
        print("RUNTIME MODE", self.runtime_mode)

        if self.runtime_mode == "DEVELOPMENT":
            self.base_path = ""
        else:
            self.base_path = f"/dynserv/{git_commit_hash}.{service_module_name}"
            
        print("BASE PATH", self.base_path)

        result = re.match(r'^((?:.+)://(?:.+?))(?:/.*)?$', config['kbase-endpoint'])

        origin = result.group(1)

        #
        # UI origin is designed to match the kbase deploy environment, not this service,
        # which may be running locally.
        #
        if origin == 'https://kbase.us':
            self.ui_origin = 'https://narrative.kbase.us'
        else:
            self.ui_origin = origin

        print("UI ORIGIN", self.ui_origin)


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

            print('SERVICE ORIGIN', self.service_origin)

            self.service_url = self.service_origin + self.base_path

            print('SERVICE URL', self.service_url)
        else:
            #
            # If not local, then the base origin is still the deploy env.
            #
            self.service_origin = origin

            print('SERVICE ORIGIN', self.service_origin)

            self.service_url = origin + self.base_path

            print('SERVICE URL', self.service_url)

    def get_widget_config(self):
        return {
            "runtime_mode": self.runtime_mode,
            "base_path": self.base_path,
            "ui_origin": self.ui_origin,
            "service_origin": self.service_origin,
            "service_url": self.service_url
        }

    def has_widget(self, name):
        return name in self.WIDGETS

    def get_widget(self, name):
        return self.WIDGETS[name]

    def add_assets_widget(self, name, title=None, path=None):
        widget_instance = Assets(
            service_module_name = self.service_module_name,
            name = name,
            path = path or name,
            title = title or name.title(),
            config = self.config,
            widget_config = self.get_widget_config()
        )

        self.WIDGETS[name] = widget_instance

    def add_static_widget(self, name, title=None, path=None):

        widget_instance = StaticWidget(
            service_module_name = self.service_module_name,
            name = name,
            path = path or name,
            title = title or name.title(),
            config = self.config,
            widget_config = self.get_widget_config()
        )

        self.WIDGETS[name] = widget_instance

    def add_python_widget(self, name, module=None, title=None, path=None):

        widget_instance = PythonWidget(
            service_module_name = self.service_module_name,
            name = name,
            path = path or name,
            title = title or name.title(),
            config = self.config,
            widget_module_name = module or name,
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

def set_global_widget_support(widget_support):
    global GLOBAL_WIDGET_SUPPORT
    GLOBAL_WIDGET_SUPPORT = widget_support

def get_global_widget_support():
    return GLOBAL_WIDGET_SUPPORT