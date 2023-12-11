import os
from pathlib import Path

MEDIA_TYPE_MAPPING = {
    "html": "text/html",
    "text": "text/plain",
    "css": "text/css",
    "js": "application/javascript",
    "json": "application/json",
    "png": "image/png",
    "jpg": "image/jpg",
    "csv": "text/csv",
}

DEFAULT_MEDIA_TYPE = "application/octet-stream"


def handle_static_file(container_path, resource_path):
    """
    Respond with the requested file within the container directory, or the appropriate
    error response if something goes wrong.
    """

    #
    if not container_path.is_dir():
        response_status = '404 Not Found'
        response_content_type = 'text/plain; charset=utf-8'
        response_content = f"The container for the resource does not exist: {container_path}"
        return (response_status, response_content_type, response_content.encode('utf-8'))

    resource = container_path.joinpath(resource_path)

    # TODO: ensure that the full path is within container path

    # Now we we can ensure the requested resource exists.
    if not resource.is_file():
        response_status = '404 Not Found'
        response_content_type = 'text/plain; charset=utf-8'
        response_content = f"The file was not found: {resource_path}"
        return (response_status, response_content_type, response_content.encode('utf-8'))

    # Get the extension, media type, return 415 if not supported:
    if resource.suffix == '':
        response_status = '404 Not Found'
        response_content_type = 'text/plain; charset=utf-8'
        response_content = "The requested resource must have an extension to serve it"
        return (response_status, response_content_type, response_content.encode('utf-8'))

    extension = resource.suffix[1:]
    response_content_type = MEDIA_TYPE_MAPPING.get(extension)

    if response_content_type is None:
        response_status = '415 Unsupported Media Type'
        response_content_type = 'text/plain; charset=utf-8'
        response_content = f"The requested resource with extension {extension} is not supported"
        return (response_status, response_content_type, response_content.encode('utf-8'))

    response_content = resource.read_bytes()

    response_status = '200 OK'

    return (response_status, response_content_type, response_content)
