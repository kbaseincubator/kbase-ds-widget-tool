import re

# from .handlers import (
#     assets_handler,
#     direct_widget_handler,
#     python_widget_handler,
#     static_widget_handler,
# )
# from .handlers.static_widget import StaticWidget


def not_found(widget_name):
    status = '404 Not Found'
    content_type = 'text/plain; charset=utf-8'
    content = f"Widget Not Found: {widget_name}".encode('utf-8')
    return status, content_type, content

# WIDGETS = {
#     "first": StaticWidget(
#         service_module_name="foo"
#         widget_name="First"
#         path="first"
#         config=
#     )
# }

WIDGETS = {}

def has_widget(name):
    return name in WIDGETS

def get_widget(name):
    return WIDGETS[name]

def add_widget(name, instance):
    WIDGETS[name] = instance


# def find_widget_handler(widget_name):
#     if widget_name in direct_widget_handler.WIDGETS:
#         #
#         # Test widgets are hosted directly in this file
#         #
#         return direct_widget_handler.handle
#     else:
#         #
#         # And that is all we offer for now.
#         #
#         return not_found_handler


def handle_widget(service_module_name, widget_name, widget_path, request_env, config):
    # our new widget objects; already initialized for this environment.
    if has_widget(widget_name):
        widget = get_widget(widget_name)
        return widget.handle(widget_path, request_env)
    else:
        return not_found(widget_name)
        # handle = find_widget_handler(widget_name)
        # return handle(service_module_name, widget_name, widget_path, request_env, config)


def widget_handler(service_module_name, request_env, config):
    path = request_env['PATH_INFO']
    result = re.match(r'^/widgets/(.*?)(?:/(.*))?$', path)

    widget_name = result.group(1)
    widget_path = result.group(2)

    # handle = find_widget_handler(widget_name)

    # #
    # # A widget handler returns a subset of a full response. 
    # # status - the usual wsgi response, a string composed of the response code and the
    # # response text. E.g. "200 OK"abs
    # # content_type - for the respons header; used literally as provided
    # # content - a byte array; so strings must be encoded already.
    # #
    # status, content_type, content = handle(service_module_name, widget_name,
    # widget_path, request_env, config)
    
    status, content_type, content = handle_widget(service_module_name, widget_name, widget_path, request_env, config)

    response_headers = [
        ('content-type', content_type),
        ('content-length', str(len(content)))]

    return status, response_headers, content
