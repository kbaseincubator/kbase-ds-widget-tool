# Design Notes

A dynamic service is based on uwsgi.

The generated server file contains no less than 2 different server configurations - neither of which are used. It is a mess.

We won't attempt to fix that. Though it is a good argument for a simplified dynamic service architecture.

Rather, uwsgi is started from the command line in the `start_server.sh` script. The uwsgi binary will search for the variable "application" in the file passed in as `--uwsgi-file`. It will consider this to be the entrypoint for the uwsgi application.

The uwsgi file is none other than the dynamic service's generated server file, in this case `epearsonServiceWidgetDemo/epearsonServiceWidgetDemoServer.py`. Quite a mouthful, and unnecessarily so, but that is another discussion.

Within this file is a class named Application. This is the class behind the `application` variable created loose in the file. Within Application is a method `__call__` which is there to make the instance "callable". It is this method that is invoked by uwsgi to initialize the application. And it is this method that handles the request, so it is in this method that we need to intercept the request in order to have it handle widgets.

So in the end it is just a handful of lines to handle the widget request. The responsibility of that code is to determine if the path begins with /widget, and if so, pass the request to the widget handler. The widget handler is a separate file, so we can go wild there, and code as we wish!

