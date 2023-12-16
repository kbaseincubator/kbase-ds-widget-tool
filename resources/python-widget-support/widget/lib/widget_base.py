import os
import re

from jinja2 import ChoiceLoader, Environment, FileSystemLoader
from widget.lib.generic_client import GenericClient
from widget.lib.widget_error import WidgetError
from widget.lib.widget_utils import object_info_to_dict, workspace_info_to_dict


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

    def get_object(self, ref, allowed_types):
        workspace = GenericClient(
            module_name='Workspace',
            url = self.config.get('workspace-url'),
            token = self.token,
            timeout=10000
        )
        params = {
            'includeMetadata': 1,
            'objects': [{'ref': ref}]
        }
        try:
            object_info = object_info_to_dict(workspace.call_func('get_object_info3', [params])[0]['infos'][0])
        except WidgetError as werr:
            raise werr
        except Exception as ex:
            raise WidgetError(
                title="Error",
                code="error-fetching-object",
                message=str(ex)) from ex

        if object_info['size'] > 1_000_000:
            raise WidgetError(
                title="Error",
                code="file-too-big",
                message=f"Object too big: {object_info['size']}")

        type_module, type_name, _type_version_major, _type_version_minor = re.split(r'[.-]', object_info['type_id'])

        type_id_versionless = '.'.join([type_module, type_name])

        # if type_module != "KBaseStructure" and type_name != "ProteinStructures":
        if type_id_versionless not in allowed_types:
            raise WidgetError(
                title="Error",
                code="incorrect-type",
                message=f"Expected an object of type KBaseStructure.ProteinStructures, but got {object_info['type_id']}"
            )

        workspace_id = object_info['workspace_id']

        workspace_info = workspace_info_to_dict(workspace.call_func('get_workspace_info', [{"id": workspace_id}])[0])

        params = {
            'objects': [{'ref': ref}],
            'infostruct': 1
        }
        data_object = workspace.call_func('get_objects2', [params])[0]['data'][0]

        return [data_object, workspace_info]