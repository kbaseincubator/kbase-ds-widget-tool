# Adding a Python Widget

In brief, here is what we'll do:

- create the directory structure and files for the python widget implementation (code and templates)
- create the directory structure and files for the widget's static assets
- add the widget to the widget registry file
- implement a minimal widget
- try it out!

## Create Directories

Python widgets are implemented through a convention of specifically named files in specific locations. There are two sets of files required - the code implementation consisting of Python and Jinja2 templates, and the static assets consisting of stylesheets, javascript, and images.

Since this is written in a tutorial style, we'll provide explicit instructions for replicating this procedure. You may, of course, read between the lines and use it as a rough guide and change the order and style of implementation (other than the placement and naming of files).

The first task is to create the directories and files required for the implementation. In addition to creating the directories, create empty files as placeholders.

- decide on an id for your widget. Best is lower case, understore separators ("snake-case"), so that it is friendly to urls and to python.

  - The url name and internal name for a widget may be different, but it simplifies life if they are the same.

- within directory create the minimal structure:

  ```
  lib
    widget
      widgets
        minimal_example
          widget.py
          templates
            index.html
  widget
  	assets
  	  widgets
        minimal_example
          index.css
  ```

- The python widget lives in the `lib/widget/widgets/minimal_example` directory, and is available on the package path `widget.widgets.your_widget`.

- The implementation of the widget will be in `widget.py`

- The initial template to render is `templates/index.html`. Widgets use `jinja2` templating.

  - Any sub or partial templates will also need to reside within `templates`, more on this later.

- Any static assets for widgets, including stylesheets, images, or javascript files, reside in the static support directory `widget/assets/your_widget`. Each python widget has a static directory in `widget/assets`.

### Add widget to registry

A widget must be added to the "widget registry" located in `widget/widgets.yml` before it may be accessed. 

A widget registry entry looks like this: 

```yaml
  - name: minimal_example_py
    type: python
    package: minimal_example
    title: Your Widget
```

Where:

- `name` is the url component that will correspond to the widget. In a url it is used like
  `https://ci.kbase.us/dynserv/895d41678a4b59e1d4c639e619b10bd27b7b0fe3.usernameService/widgets/minimal_example_py`

- `type` is always `python` for a python widget

- `package` is  the python package name for the widget. It is optional and defaults to the `name`. All widgets live in the directory `lib/widget/widgets` and have a unique directory within this which also forms the module's package name. All Python widgets reside in the `widget.widgets` package. The widget package name is appended to this, thus `widget.widgets.minimal_example`. 

  It is recommended to omit this property, unless there is a good reason that the module name is different than the url path component name. 

- `title` is also optional, and defaults to the `name` as well. The title is only used in contexts in which the widget must be communicated to a human, such as in error messages, log entries. Arguably, a nice `name` is just as good as a title, so it is recommended to just create a fully spelled-out name which can serve as a "good enough" title.

### Create the Python implementation

A widget typically divides it's implementation into two parts, guided by the design we have provided.

The widget implementation file fetches and prepares data to be displayed. The widget template expects that data and prepares html for display inthe browser.

#### Widget implementation module

The implementation module is a python module named `widget.py` . It resides on the path `lib/widget/widgets/minimal_example/widget.py`, and is addressable on the dotted module path `widget.widgets.your_widget.widget`, although you will probably never need to use this. It is implemented as a subclass of the `WidgetBase` class. The simplest possible Widget is:

```python
from widget.lib.widget_base import WidgetBase
class Widget(WidgetBase):
    pass
```

This widget would provide no additional template data other than that provided by `WidgetBase`. (See the section below on WidgetBase)

Note that the widget class must be named `Widget`. This is not a problem in terms of name collision, as each widget implementation resides on a unique dotted module path. This requirement is part of the "convention over configuration" or "convension over complex introspection" design of widgets.

There is no requirement that a widget provide any novel data to render. In fact, one of the built-in widgets `config`, simply displays the current service and widget configurations (which are built into  WidgetBase).

But such widgets are not the primary use case for widgets, which is to visualize data from KBase Narratives!

To provide data to the template, you will need to create a `context` method in your widget class. A context is just a dict which itself may contain values which are strings, numbers, booleans, lists, and other dicts. Think "json-compatible". 

A kb-sdk service uses the "kbase base image", `kbase/sdkbase2:python` hosted at dockerhub, which contains pre-installed libraries. We won't concern ourselves with them now, other than stating that the version of `Jinja2` is `2.10` (yes, indeed, that is very old).


Only a few of these are relevant to implementing a widget. In our minimal use case, we won't use any of these libraries, but we will create a simple context which provides one property: `greeting`.

```python
from widget.lib.minimal_example import WidgetBase
class Widget(WidgetBase):
    def context(self):
        return {
          "greeting": "Hello KBase!"
        }
```

#### Widget Template

A widget always has a single entrypoint template named `index.html`. This file will be processed by `Jinja2` with the context provided by the widget's module. Since the rendered template will be provided as an html response, it needs to be proper html.

We won't delve into it now, but your template may invoke sub-templates, also known as "partials". This is very useful if you widget becomes complex, and the template would become inconveniently large and confusing.

In our case, we'll use a minimal html template:

```html
<!DOCTYPE html>
<html lang="en-US">
  <head>
    <title>Minimal Example Widget in Python</title>
    <meta charset="utf-8">
  </head>
  <body>
    {{ greeting }}
  </body>
</html>
```

In most widgets you will want to include styles and javascript, but we'll cover that in another tutorial.

### Trying it out

Now that you have:

- added the widget to the regsitry
- added the implementation class
- aded the implementation template

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

Navigate your browser to [http://localhost:5100/widgets/minimal_example_py][http://localhost:5100/widgets/minimal_example_py]

You should see: 

```text
Hello KBase!
```

## Next Steps

Now that we've established the process of adding a static, Python powered widget to a dynamic service, we'll next explore adding additional style and javascript support, subtemplates, and communcation with KBase services and Narratives.

[Next - Advanced Python Widgets](advanced-python-widgets.md)



## Notes

### KBase base image installed packages


```text
Package                  Version  
------------------------ ---------
alabaster                0.7.11   
asn1crypto               0.24.0   
Babel                    2.6.0    
biopython                1.72     
certifi                  2018.8.24
cffi                     1.11.5   
chardet                  3.0.4    
conda                    4.5.11   
coverage                 4.5.1    
cryptography             2.3.1    
docutils                 0.14     
gitdb2                   2.0.4    
GitPython                2.1.11   
idna                     2.7      
imagesize                1.1.0    
Jinja2                   2.10     
JSONRPCBase              0.2.0    
MarkupSafe               1.0      
mkl-fft                  1.0.4    
mkl-random               1.0.1    
ndg-httpsclient          0.5.1    
nose                     1.3.7    
nose2                    0.8.0    
numpy                    1.15.0   
packaging                17.1     
pip                      9.0.1    
pyasn1                   0.4.4    
pycosat                  0.6.3    
pycparser                2.19     
Pygments                 2.2.0    
pyOpenSSL                18.0.0   
pyparsing                2.2.1    
PySocks                  1.6.7    
pytz                     2018.5   
PyYAML                   3.13     
requests                 2.19.1   
requests-toolbelt        0.8.0    
ruamel-yaml              0.11.14  
setuptools               40.4.2   
six                      1.11.0   
smmap2                   2.0.4    
snowballstemmer          1.2.1    
Sphinx                   1.8.1    
sphinxcontrib-websupport 1.1.0    
urllib3                  1.23     
uWSGI                    2.0.17.1 
wheel                    0.30.0 
```

> Yes, some of these are very out of date

### Predefined Context



### Widget Base