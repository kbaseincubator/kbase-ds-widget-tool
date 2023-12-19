from widget.lib.widget_base import WidgetBase


class Widget(WidgetBase):

    def context(self) -> dict:
        """
        Get the object info, workspace info, and the object itself.
        """
        ref = self.get_param('ref')

        [media_object, workspace_info] = self.get_object(ref, ['KBaseBiochem.Media'])

        return {
            'workspace_info': workspace_info, 
            'media_object': media_object,
        }
