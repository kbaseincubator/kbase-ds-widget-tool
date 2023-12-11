import re


def not_found(widget_name):
    status = '404 Not Found'
    content_type = 'text/plain; charset=utf-8'
    content = f"Widget Not Found: {widget_name}".encode('utf-8')
    return status, content_type, content

WIDGETS = {}

def has_widget(name):
    return name in WIDGETS

def get_widget(name):
    return WIDGETS[name]

def add_widget(name, instance):
    WIDGETS[name] = instance


def handle_widget(service_module_name, widget_name, widget_path, request_env, config):
    # our new widget objects; already initialized for this environment.
    if has_widget(widget_name):
        widget = get_widget(widget_name)
        return widget.handle(widget_path, request_env)
    else:
        return not_found(widget_name)

def widget_handler(service_module_name, request_env, config):
    path = request_env['PATH_INFO']
    result = re.match(r'^/widgets/(.*?)(?:/(.*))?$', path)

    widget_name = result.group(1)
    widget_path = result.group(2)

    status, content_type, content = handle_widget(service_module_name, widget_name, widget_path, request_env, config)

    response_headers = [
        ('content-type', content_type),
        ('content-length', str(len(content)))]

    return status, response_headers, content
