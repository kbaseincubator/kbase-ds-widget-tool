from epearsonServiceWidgetDemo.widget.widgets.utils import (
    get_param,
    object_info_to_dict,
    workspace_info_to_dict,
)
from installed_clients.WorkspaceClient import Workspace
from jinja2 import ChoiceLoader, Environment, FileSystemLoader, PackageLoader


class Widget:
    """
    Implementation of the media viewer widget. 
    """
    def __init__(self, token, params, path_rest, config):
        # KBase auth token, as provided by the router
        self.token = token

        # Ref parameter, as provided by the router.
        self.ref = get_param(params, 'ref')

        print('WS URL??', config)

        self.workspace_url = config.get('workspace-url')

        # Config, as provided by the router, but that just gets it from  the
        # global service config.
        # self.config = Config2()

        # Set up for loading templates out of the templates directory.
        # global_loader = PackageLoader("epearsonServiceWidgetDemo.widgets", "templates")
        # widget_loader = PackageLoader(
        #     "epearsonServiceWidgetDemo.widgets.media_viewer", "templates"
        # )
        
        global_loader = FileSystemLoader("./lib/epearsonServiceWidgetDemo/widget/widgets/templates")
        widget_loader = FileSystemLoader(
            "./lib/epearsonServiceWidgetDemo/widgets/media_viewer/templates"
        )
        

        loader = ChoiceLoader([widget_loader, global_loader])
        self.env = Environment(loader=loader) 

    def render(self) -> str:
        """
        Render the widget, returning bytes
        """
        # get workspace and object infos.
        workspace = Workspace(
            url = self.workspace_url,
            token = self.token
        )
        params = {
            'includeMetadata': 1,
            'objects': [{'ref': self.ref}]
        }
        try:
            object_info = object_info_to_dict(workspace.get_object_info3(params)['infos'][0])

        except Exception as ex:
            template = self.env.get_template("error.html")
            error = {
                "title": "Error",
                "code": "error-fetching-object",
                "message": str(ex),
            }
            return template.render(error=error).encode('utf-8')

        if object_info['size'] > 1_000_000:
            raise Exception(f"Object too big: {object_info['size']}")

        # workspace_id, _, _ = parse_workspace_ref(self.ref)

        workspace_id = object_info['workspace_id']

        workspace_info = workspace_info_to_dict(workspace.get_workspace_info({"id": workspace_id}))

        # print('WSINFO', workspace_info)
        
        # params = {
        #     'objects': [{'ref': self.ref}],
        #     'infostruct': 1
        # }
        # media_object = workspace.get_objects2(params)['data'][0]

        params = [{'ref': self.ref}]
        media_object = workspace.get_objects(params)[0]

        template = self.env.get_template("index.html")
        return template.render(
            token=self.token, object_info=object_info, workspace_info=workspace_info, media_object=media_object
        ).encode('utf-8')
