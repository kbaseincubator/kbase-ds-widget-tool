import os

from jinja2 import ChoiceLoader, Environment, FileSystemLoader


def object_info_to_dict(object_info):
    [
        object_id,
        object_name,
        type_id,
        save_date,
        version,
        saved_by,
        workspace_id,
        workspace_name,
        checksum,
        size,
        metadata,
    ] = object_info

    return {
        'object_id': object_id,
        'object_name': object_name,
        'type_id': type_id,
        'save_date': save_date,
        'version': version,
        'saved_by': saved_by,
        'workspace_id': workspace_id,
        'workspace_name': workspace_name,
        'checksum': checksum,
        'size': size,
        'metadata': metadata,
    }

def workspace_info_to_dict(workspace_info):
    [
        workspace_id,
        workspace_name,
        owner,
        modified_at,
        max_object_id,
        user_permission,
        global_permission,
        lock_status,
        metadata,
    ] = workspace_info

    return {
        'workspace_id': workspace_id,
        'workspace_name': workspace_name,
        'owner': owner,
        'modified_at': modified_at,
        'max_object_id': max_object_id,
        'user_permission': user_permission,
        'global_permission': global_permission,
        'lock_status': lock_status,
        'metadata': metadata,
    }

def get_param(params, key):
    """ 
    Safely gets a parameter from the dict created by parse_qs.

    The parsed search params is not a straight dict, as the value is an array, to
    accommodate multiple parameters (a rare case!).
    """
    value = params.get(key)
    if value is None:
        return None
    if len(value) != 1:
        return None
    return value[0]

class WidgetError(Exception):
    def __init__(self, title, code, message):
        super().__init__(message)
        self.title = title
        self.code = code
        self.message = message

    def get_context(self):
        return {
            "title": self.title,
            "code": self.code,
            "message": self.message
        }


class WidgetBase:
    """
    Base behavior for Python Widgets
    """
    def __init__(self, service_module_name, widget_module_name, token, params, rest_path, config, widget_config):
        # The module name for the service (directory name, first component of service
        # package path)
        self.service_module_name = service_module_name

        # The name of the widget's import path (or name) component within the widgets
        # package. The Python widgets package resides in
        # widget.widgets
        # We need this value for dynamically constructing the file system loader for templates.
        self.widget_module_name = widget_module_name

        # Service config (from deploy.cfg)
        self.config = config

        self.widget_config = widget_config

        # KBase auth token, as provided by the router
        self.token = token

        # Paraemters from the url search component - i.e. query params
        self.params = params

        # The rest of the path after the widget name itself. This can be used for
        # parameterization as well, or for any purpose.
        self.rest_path = rest_path

        # We look for templates in the top level "templates" directory, to provide
        # shared templates, and within the widget's "templates" directory as well. The
        # widget templates take precedence, allowing a widget to override a global
        # template
        #
        # Note: For some reason, the package loader is not working. It may be the jinja2
        # version, or the old python.
        # Note: this of course relies up on the standard kb-sdk directory layout, as
        # well as that established by Dynamic Service Widgets.
        global_loader = FileSystemLoader("./lib/widget/widgets/templates")
        widget_loader = FileSystemLoader(
           f"./lib/widget/widgets/{self.widget_module_name}/templates"
        )
        loader = ChoiceLoader([widget_loader, global_loader])
        self.env = Environment(loader=loader)

    def get_param(self, key):
        """ 
        Safely gets a parameter from the dict created by parse_qs.

        The parsed search params is not a straight dict, as the value is an array, to
        accommodate multiple parameters (a rare case!).
        """
        value = self.params.get(key)
        if value is None:
            return None
        if len(value) != 1:
            return None
        return value[0]

    def get_context(self) -> dict:
        """
        Provides a "context dict" for the template. 

        In the base class, it defaults to an empty dict, so that a simple widget with no
        context will just work.
        """
        return {}

    def render(self) -> str:
        """
        Render the widget, returning bytes
        """
        try:
            context = self.get_context()
            template = self.env.get_template("index.html")
            return template.render(context).encode('utf-8')
        except WidgetError as ex:
            template = self.env.get_template("error.html")
            return template.render({"error": ex.get_context()}).encode("utf-8")
        except Exception as ex:
            context = {
                "title": "Error",
                "code": "error-generating-context",
                "message": str(ex),
            }
            template = self.env.get_template("error.html")
            return template.render(context).encode("utf-8")

    def get_base_path(self):
       return self.widget_config.get('base_path')

    def get_asset_url(self):
       return os.path.join(self.widget_config.get('service_url'), 'widgets', 'assets')

    def get_widget_asset_url(self):
        return os.path.join(self.widget_config.get('service_url'), 'widgets', 'assets', self.widget_module_name)

        