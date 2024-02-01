import json
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
    def __init__(self, service_package_name, widget_package_name, token, params, rest_path, service_config, widget_config):
        # The module name for the service (directory name, first component of service
        # package path)
        self.service_package_name = service_package_name

        # The name of the widget's import path (or name) component within the widgets
        # package. The Python widgets package resides in
        # widget.widgets
        # We need this value for dynamically constructing the file system loader for templates.
        self.widget_package_name = widget_package_name

        # Service config (from deploy.cfg)
        self.service_config = service_config

        self.widget_config = widget_config

        # KBase auth token, as provided by the router
        self.token = token


        self.params = self.extract_params(params)

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
           f"./lib/widget/widgets/{self.widget_package_name}/templates"
        )
        loader = ChoiceLoader([widget_loader, global_loader])
        self.env = Environment(loader=loader)

    def extract_params(self, url_search_params):
        """
        Extracts normalized parameters from the dict of search fragment query fields as
        provided by the requests library.

        Note that as a search query field may be repeated, requests represents the value
        as an array. We just take the first element, although future work could, for
        example, allow an array to be passed via repeated fields. For now, the solution
        for any data more complex than a string is to use the special `params` parameter.

        Parameters from the url search component - i.e. query params
        We support two styles. For simplicity, a param may be provided directly as a
        search/query param. Of course, the value will be a string - the widget is
        responsible for interpreting it, casting to the ultimate form, etc.
        For reliability and extensibility, a single `params` search param may be
        supplied, which is a JSON text value. That is, it is a JSON-compatible
        structure which has been converted to a JSON string form (e.g. in JS
        JSON.stringify(params), or Python json.dumps(params)), and url-encoded to make
        it safe to transport in a URL. This style preservers, of course, any
        JSON-compatible value in it's native form.
        """
        params = {}
        for key, value in url_search_params.items():
            if key == 'params':
                print('PARAMS??', json.loads(value[0]))
                params.update(json.loads(value[0]))
            else:
                params[key] = value[0]
        return params


    def get_param(self, key):
        """ 
        Safely gets a parameter from the dict created by parse_qs.

        The parsed search params is not a straight dict, as the value is an array, to
        accommodate multiple parameters (a rare case!).
        """
        return self.params.get(key)

    def has_param(self, key):
        return key in self.params

    def context(self):
        """
        To be implemented, if need be, by a widget implementation
        """
        return {}

    def get_context(self) -> dict:
        """
        Provides a "context dict" for the template. 

        In the base class, it defaults to an empty dict, so that a simple widget with no
        context will just work.
        """
        context = {
            'token': self.token, 
            'service_config': self.service_config,
            'widget_config': self.widget_config,
            'ui_origin': self.widget_config.get('ui_origin'),
            'base_path': self.widget_config.get('base_path'),
            'asset_url': self.get_asset_url(),
            'widget_asset_url': self.get_widget_asset_url(),
        }
        context.update(self.context())
        return context

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
        return os.path.join(self.widget_config.get('service_url'), 'widgets', 'assets', 'widgets', self.widget_package_name)

    def get_object(self, ref, allowed_types):
        workspace = GenericClient(
            module_name='Workspace',
            url = self.service_config.get('workspace-url'),
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

        type_module, type_name, type_version_major, type_version_minor = re.split(r'[.-]', object_info['type_id'])

        type_id_versionless = '.'.join([type_module, type_name])

        # if type_module != "KBaseStructure" and type_name != "ProteinStructures":
        if type_id_versionless not in allowed_types:
            raise WidgetError(
                title="Error",
                code="incorrect-type",
                message=f"Expected an object of type {', '.join(allowed_types)}, but got {type_id_versionless} (v{type_version_major}.{type_version_minor})"
            )

        workspace_id = object_info['workspace_id']

        workspace_info = workspace_info_to_dict(workspace.call_func('get_workspace_info', [{"id": workspace_id}])[0])

        params = {
            'objects': [{'ref': ref}],
            'infostruct': 1
        }
        data_object = workspace.call_func('get_objects2', [params])[0]['data'][0]

        return [data_object, workspace_info]