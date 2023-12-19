from widget.lib.widget_base import WidgetBase
from widget.lib.widget_error import WidgetError


class Widget(WidgetBase):

    def context(self) -> dict:
        """
        Get the object info, workspace info, and the object itself.
        """

        if not self.has_param('output_genome_ref'):
            raise WidgetError(
                title = 'Missing parameter "output_genome_ref"',
                code = "missing-parameter",
                message = 'The required parameter "output_genome_ref" was not provided'
            )
        output_genome_ref = self.get_param('output_genome_ref')

        if not self.has_param('change_log'):
            raise WidgetError(
                title = 'Missing parameter "change_log"',
                code = "missing-parameter",
                message = 'The required parameter "change_log" was not provided'
            )
        change_log = self.get_param('change_log')

        [genome_object, workspace_info] = self.get_object(output_genome_ref, ['KBaseGenomes.Genome'])

        return {
            'workspace_info': workspace_info, 
            'genome_object': genome_object,
            'change_log': change_log,
        }
