from widget.lib.widget_base import WidgetBase


class Widget(WidgetBase):
    def get_context(self) -> dict:
        return {
            "config": self.config
        }
