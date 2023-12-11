from ...widget_utils import WidgetBase


class Widget(WidgetBase):
    def get_context(self) -> dict:
        demo = self.params['demo'][0] if 'demo' in self.params else None
        return {
            "config": self.config,
            "demo": demo
        }
