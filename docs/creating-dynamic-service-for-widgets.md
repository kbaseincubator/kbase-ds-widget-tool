# Getting Started

This document will guide you through the process of creating a new KBase Dynamic
Service, and upgrading with Widget support.

If you have an existing Dynamic Service and wish to add widgets to it, see the companion
document [Adding Widgets to an Existing Dynamic
Service](adding-widgets-to-an-existing-dynamic-service.md).

For more about Dynamic Services and the KBase SDK, see [the
documentation](https://kbase.github.io/kb_sdk_docs).

## Prerequisites

Since all tools run in docker containers, you will need docker installed on your
machine. On macOS or Windows [Docker Desktop](https://www.docker.com/products/docker-desktop/) is a great, easy choice.

## A. Create a kb-sdk dynamic service

First, we'll create a new Dynamic Service. This section follows the upstream
instructions at https://kbase.github.io/kb_sdk_docs/tutorial/2_install.html, but
modifies the process to fit this tutorial.

1. Create or navigate to a project directory:

    We'll be doing all of our work within a single project direcotry.

    E.g.

    ```shell
    mkdir myproject
    cd myproject
    ```

2. Create a local copy of the kb-sdk tool:

    > The upstream instructions specify to install this tool globally, but we'll just
    > use it locally for this tutorial, in order to be less intrusive in your system.
    > You may, of course, choose to install it in a central location and modify your
    > login profile to ensure it is always in your `PATH`.

    ```shell
    docker run kbase/kb-sdk genscript > ./kb-sdk
    chmod +x ./kb-sdk
    export PATH=$PATH:${PWD}
    ```

3. Initialize your new service

    Here we use the `kb-sdk` tool set up above to create and populate a KBase "module".

    ```shell
    kb-sdk init --verbose --language python --user yourusername yourusernameSomeService
    ```

    This creates a directory named after the module, `yourusernameSomeService`, and
    populates it with the initial code for a KBase app or dynamic service.

    If you were creating a real service, you would use your KBase username in place of
    `yourusername `.

    The final `yourusernameSomeService` is the name of the module. It is
    recommended that this be a concatenation of your username and the name for the sensible
    name for the module, which in this case will be a dynamic service. This helps ensure
    that the module name is unique within KBase.

    > In practice, I've not seen many people do this - in this case they would simply
    > use `SomeService`.

4. Next we'll set up git and make the first commit.


    ```shell
    cd yourusernameSomeService
    git init
    git add --all
    git commit -m "My first commit"
    ```

    This will help you see the changes that are made to your service, beyond the initial
    setup, as we add widget support, and then add widgets.

5. Next, run all service preparation steps in one fell swoop

    ```shell
    make all
    ```

    That should have generated 7 files.

    For example, we can now list the changes since the commit above:

    ```shell
    % git status  -bs
    ## main
    M lib/yourusernameSomeService/yourusernameSomeServiceImpl.py
    M scripts/entrypoint.sh
    ?? bin/
    ?? lib/yourusernameSomeService/yourusernameSomeServiceImpl.py.bak-2023-12-07-18-42-21
    ?? lib/yourusernameSomeService/yourusernameSomeServiceServer.py
    ?? scripts/start_server.sh
    ?? test/run_tests.sh
    ```

6. Commit the changes again

    Let's commit the files changed or added by `make all`, so that when we add widget
    support we can inspect all the files added.

    ```shell
    git add --all; git commit -m "Initialized service with 'make all'"
    ```

    And now you should see a clean slate:

    ```shell
    % git status  -bs
    ## main
    ```

    The output shows that we are on the `main` branch, and there are no changed files listed.

## B. Add Widget Support to the Dynamic Service

Now we are ready to add widget support to the dynamic service.

To do this we use the `ds-widget-tool` which, similar to `kb-sdk`, runs as a docker
container.

1. Obtain a copy of the tool

    To get started, we'll install a copy of the `ds-widget-tool` locally. At present, it cannot be
    run remotely, but must be installed locally.

    First, navigate back to the project directory as we'll be installing the tool there.

    ```shell
    cd ..
    ls
    kb-sdk			yourusernameSomeService
    ```

    Then install the tool:

    ```shell
    git clone https://github.com/eapearson/ds-widget-tool
    ```

2. Ensure the tool will work correctly

    To ensure the tool will work

1. Convert the app to a dynamic service

By default, the KBase SDK will create an "app", which differs from a "dynamic service"
in that the app is run through the execution service, and the dynamic service is a live
web app.

Since this tool can be used to convert any dynamic service, a new one or an old one, but
should not be applied to an app, we do require that a new SDK module be converted to a
dynamic service first

To convert the module to a dynamic service, we simply add the following to the end of
the 
`kbase.cfg` configuration file:

```yaml
service-config:
    dynamic-service: true
```

which should then look like:

```yaml
module-name:
    yourusernameSomeService

module-description:
    A KBase module

service-language:
    python

module-version:
    0.0.1

owners:
    [yourusername]

service-config:
    dynamic-service: true

```

8. Commit the changes

Let's go ahead and commit those changes, so we can observe what is changed when we
convert the codebase to support widgets.

```shell
git add --all
git commit -m "Ran 'make all' and converted to dynamic service"
```

9. Use the `ds-widget-tool` to upgrade the module

Now we are ready to run the ds widget tool to add the widget support to the module
codebase.

The tool is available from github at `https://github.com/kbase/ds-widget-tool`

> TODO: this will probably change, and we also want to allow users to use this from the
> command line via the image/container...

To get started, clone the tool into your project directory

```shell
git clone https://github.com/kbase/ds-widget-tool
```

And then change into the tool's directory:

```shell
cd ds-widget-tool
```

The tool is run through a shell script named `Taskfile`.

If you run `Taskfile` without a command, it will show a little help screen:

```shell
% ./Taskfile
./Taskfile <task> <args>
Runs the tasks listed below.
To find out more about them, either read the source
for ./Taskfile or the docs located in 'docs/tasks.md'.
Tasks:
     1  alias-me
     2  check-module
     3  help
     4  init-module
     5  shell
Task completed in 0m0.007s
```

9. Validate service module directory

To get our feet wet, let's first run the `check-module` command to ensure that we have a
good KBase SDK module.

First, from the service module you set up above, copy the path (or type it in, your
choice).

For example, on macOS, from a terminal in the module directory, try this:

```shell
pwd | pbcopy
```

to copy the path into the clipboard.

Back in the DS Tool directory, issue the following command:

```shell
./Taskfile check-module MODULE_DIR
```

where `MODULE_DIR` is the directory you copied above.

Or if you used pbcopy above, try

```shell
./Taskfile check-module $(pbpaste)
```

E.g.

```shell
% ./Taskfile check-module /Users/erikpearson/Work/KBase/2023/service-widget/practice/yourusernameSomeService

Using service directory /Users/erikpearson/Work/KBase/2023/service-widget/practice/yourusernameSomeService

Analyzing module directory ...


✅ "kbase.yml" config file found, it looks like a KBase kb-sdk service!


✅ "kbase.yml" successfully loaded


✅ The service module "yourusernameSomeService" is indeed a dynamic service as well

Module name        : yourusernameSomeService
Module description : A KBase module
Service language   : python
Module version     : 0.0.1
Owners             : yourusername
Task completed in 0m0.510s
erikpearson@Eriks-MBP ds-widget-tool % 
```

If anything is wrong with the service directory, an error message should be
appropriately displayed.

E.g. if we have not yet converted it to a dynamic service the following error message
will be displayed:

```shell
❌ ERROR: Attribute service-config.dynamic-service expected in KBase Config but was not found.
```

10. Add widget support to the service module

Now we are ready for the show to begin.

Similar to the command above:

```shell
./Taskfile init-module MODULE_DIR
```


## Start the service

Next start the service


```shell
export KBASE_ENDPOINT=https://ci.kbase.us/services/ 
export SDK_CALLBACK_URL=
docker compose run --service-ports yourusernamesomeservice bash
```

If docker compose fails due to the port already being allocated, set the `PORT`
environment variable first, like:

```shell
PORT=5200 docker compose run --service-ports yourusernamesomeservice bash
```

This will leave you in side the service container on the bash shell command line. You
can now start the server:

```shell
./scripts/start_server.sh
```



Try it out:

- first the status endpoint:

```shell
curl -X POST http://localhost:5200 \
    -d '{"version": "1.1", "id": "123", "method": "yourusernameSomeService.status", "params": []}'
```

and you should get this response:

```json
{
    "version": "1.1",
    "result": [
        {
            "state": "OK",
            "message": "",
            "version": "0.0.1",
            "git_url": "",
            "git_commit_hash": "83fb078dd8806965a8b642d0f0fb01c4b194a683"
        }
    ],
    "id": "123"
}
```

The widget enhancement comes with a couple of sample widgets to get you started.

http://localhost:5200/widgets/demos



- then the "config" widget:

http://localhost:5200/widgets/config




---

## Notes


## Copy docker-compose.yml


need to deal with `SDK_CALLBACK_URL`.

It is in quite a few locations which should be conditionally avoided, or omitted by
kb-sdk, but for now we can set it to an empty string.


        self.callback_url = os.environ['SDK_CALLBACK_URL']

from  
