class WidgetError(Exception):
    def __init__(self, title, code, message):
        super().__init__(message)
        self.title = title
        self.code = code
        self.message = message

    def get_context(self):
        return {
            "title": self.title,
            "code": self.code,
            "message": self.message
        }
