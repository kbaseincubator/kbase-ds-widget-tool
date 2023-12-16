import json

from widget.lib.widget_base import WidgetBase
from widget.lib.widget_error import WidgetError


class Widget(WidgetBase):
    def get_context(self) -> dict:
        """
        Get the object info, workspace info, and the object itself.
        """
        ref = self.get_param('ref')

        [protein_structures_object, workspace_info] = self.get_object(ref, ["KBaseStructure.ProteinStructures"])

        if 'pdb_infos' not in protein_structures_object["data"]:
            raise WidgetError(
                title='Error',
                code='no-pdb-infos',
                message="No 'pdb_infos' found in the object"
            )

        pdb_infos_json = json.dumps(protein_structures_object["data"]["pdb_infos"])

        return {
            'token': self.token, 
            'workspace_info': workspace_info, 
            'ui_origin': self.widget_config.get('ui_origin'),
            'base_path': self.widget_config.get('base_path'),
            'asset_url': self.get_asset_url(),
            'widget_asset_url': self.get_widget_asset_url(),
            'protein_structures_object': protein_structures_object,
            'pdb_infos_json': pdb_infos_json
        }
