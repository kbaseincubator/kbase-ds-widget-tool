from widget.lib.widget_base import WidgetBase


class Widget(WidgetBase):
    def context(self):
        return {
          "greeting": "Hello KBase!"
        }