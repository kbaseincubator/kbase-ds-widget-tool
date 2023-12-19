from widget.lib.widget_base import WidgetBase

ROUTES = [
    'home',
    'data-viewers',
    'media-viewer-js',
    'media-viewer-py',
    'protein-structures-viewer',
    'generic-widgets',
    'demo-genome-viewer',
]


class Widget(WidgetBase):
    def context(self) -> dict:
        demo = self.get_param('demo') or 'home'

        if demo in ROUTES:
            return {
                "demo": [f"partials/{demo}.html", "error.html"],
                "requested_demo": demo,
                "error": {
                    "title": "Error - Template Not Found",
                    "code": "template-not-found",
                    "message": "A route is defined for the demo, but the template was not found",
                    "info": {
                        "Requested Demo": demo
                    }
                }
            }
        else:
            return {
                "demo": "partials/not-found.html",
                "requested_demo": demo
            }
