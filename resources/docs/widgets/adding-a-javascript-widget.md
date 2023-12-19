# Adding a Javascript Widget

Within the dynamic service widget support, a javascript widget is simply a set of static resources served up in a uniform manner. The underlying implemntation of the widget is entirely up to you. We do provide examples of various types of widgets, as well as library support for interacting with KBase.

Here is what we'll do:

- Add a Javascript / static widget directory and files
- Add an entry to the widgets registry

## Prerequisites

You'l need a working kb-sdk dynamic service with widget support, see [creating-dynamic-service-for-widgets.md](creating-dynamic-service-for-widgets.md).

## Add widget to registry

A widget must be added to the "widget registry" located in `widget/widgets.yml` before it may be accessed. 

In this tutorial we'll add a "minimal javascript widget", and name it "minimal_widget_js".

A widget registry entry for a Javascript widget looks like this: 

```yaml
  - name: minimal_example_js
    type: static
    path: minimal_example
    title: Your Widget
```

Where:

- `name` is the url component that will correspond to the widget. In a url it is used like
  `https://ci.kbase.us/dynserv/895d41678a4b59e1d4c639e619b10bd27b7b0fe3.usernameService/widgets/minimal_example_js`
- `type` is always `static` for a javascript widget
- `minimal_example` is the path within the `widget/widgets` directory in which the widget is implemented. This property is optional, as it defaults to the `name`. In fact, best practice is to have the `name` be the same as the `path`.
- `title` is optional, and defaults to the `name`. The title is only used in contexts in which the widget must be communicated to a human, such as in error messages, log entries. Arguably, a nice `name` is just as good as a title, so it is recommended to just create a fully spelled-out name which can serve as a "good enough" title.

Note that, unlike Python widgets, Javascript widgets have no package -- they are decoupled from the Python codebase.

It may seem strange that the `type` for a Javascript widget is `static`. However, the type reflects the implementation style, not the programming language. Indeed, a `static` widget may be implemented in any language which transpiles to Javascript, or even to WASM. The only requirement is that the widget container be an html file.

## Layout

The most minimal Javascript-based widget has a very simply layout:

```text
widget
    widgets
        minimal_widget
            index.html
```

That's right. All that is required is a single html file. Of course, this would not be a very useful widget, but it would work. 

```html
<!DOCTYPE html>
<html lang="en-US">
  <head>
    <title>Minimal Example Widget in Javascript</title>
    <meta charset="utf-8">
  </head>
  <body>
    Hello KBase!
  </body>
</html>
```

At it's heart, a Javascript widget is a single html file. What it does inside that html file - well, inside the browser - is where the magic happens.

However, we'll create a minimal widget that mirrors the minimal functionality of the minimal Python widget. To so we'll need to have a simple data structure which provides a "greeting" property, and have the index page display it.

First, let's modify the index page to support a dynamic greeting:

```html
<!DOCTYPE html>
<html lang="en-US">
  <head>
    <title>Minimal Example Widget in Javascript</title>
    <meta charset="utf-8">
  </head>
  <body>
    <div id="greeting"></div>
  </body>
  <script>
    document.getElementById('greeting').innerText = "Hello KBase!";
  </script>
</html>
```

### Trying it out

Now that you have:

- added the widget to the regsitry
- added the implementation index html file

you are ready to try out your new widget!

```shell
export KBASE_USERNAME="username"
export SDK_MODULENAME="ModuleName" 
export SDK_MODULE="${KBASE_USERNAME}${SDK_MODULENAME}"
docker compose run --service-ports $(echo "${SDK_MODULE}" | tr '[:upper:]' '[:lower:]') bash
DEV=t ./scripts/start_server.sh
```

where

- `KBASE_USERNAME` is your KBase username
- `SDK_MODULENAME` is the module name suffix, or "logical module name"

(please see [creating-dynamic-service-for-widgets.md](creating-dynamic-service-for-widgets.md) for details)

Navigate your browser to [http://localhost:5100/widgets/minimal_example_js][http://localhost:5100/widgets/minimal_example_py]

You should see: 

```text
Hello KBase!
```

## Next Steps

Now that we've established the process of adding a static, Javascript powered widget to a dynamic service, we'll next explore adding additional style and javascript support, including communcation with KBase services and Narratives.

[Next - Advanced Javascript Widgets](advanced-javascript-widgets.md)

