from installed_clients.WorkspaceClient import Workspace
from widget.lib.widget_base import WidgetBase
from widget.lib.widget_error import WidgetError
from widget.lib.widget_utils import object_info_to_dict, workspace_info_to_dict


class Widget(WidgetBase):

    def get_context(self) -> dict:
        """
        Get the object info, workspace info, and the object itself.
        """
        ref = self.get_param('ref')

        [media_object, workspace_info] = self.get_object(ref, ['KBaseBiochem.Media'])


        return {
            'token': self.token, 
            'workspace_info': workspace_info, 
            'media_object': media_object,
            'ui_origin': self.widget_config.get('ui_origin'),
            'base_path': self.widget_config.get('base_path'),
            'asset_url': self.get_asset_url(),
            'widget_asset_url': self.get_widget_asset_url()
        }
