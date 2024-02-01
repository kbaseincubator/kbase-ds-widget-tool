# Creating a Dynamic Service With Widgets

This document will, as briefly as possible, guide you through the process of
creating a new KBase Dynamic Service, and then upgrading it with Widget support.

For more information, you may follow the [verbosely annotated
version](./creating-dynamic-service-for-widgets.md), which has the same
instructions, but provides fuller explanations.

If you have an existing Dynamic Service and wish to add widgets to it, see the
companion document [Adding Widgets to an Existing Dynamic
Service](adding-widgets-to-an-existing-dynamic-service.md).

> Unfortunately, the this has not been written or even evaluated yet.

For more about Dynamic Services and the KBase SDK, see [the `kb_sdk`
documentation](https://kbase.github.io/kb_sdk_docs).

## Prerequisites

This tool runs all processes in docker containers. Thus, you will need
`docker` installed on your machine. On macOS or Windows [Docker
Desktop](https://www.docker.com/products/docker-desktop/) is a great, easy
choice. On Linux, you may simply use your package manager to install `docker`.

The `kb-sdk` itself, a separate tool utilized in the instructions, requires, in
addition, the `make` program. This is ubiquitous on Linux, BSD, macOS, and is
available on Windows as well. I don't think it is particularly sensitive to the
version of `make`.

These instructions were created and tested withing the macOS (Sonoma) terminal,
but should be applicable to Linux or Windows wsl.

## Using these instructions

In this document each instruction step's title will be followed by the context,
usually a directory,  in which the task will be carried out. We utilize three
different directories: a project directory, inside of which is one directory for
the service and one for this tool.

For handy reference, the eventual directory structure is:

```text
myproject/
  yourusernameYourServiceModule/
  kbase-ds-widget-tool/
  kb-sdk
```

Where `yourusername` is your KBase username, and `YourServiceModule` is the base
name for your module. `kb-sdk` is the KBase SDK tool that will be installed.

> It is not strictly required that your module name be the concatenation of your
> username and a descriptive module name, but it is recommended by the KBase
> SDK.

Most blocks of commands may be simply copy/pasted into the terminal. We'll let
you know if this is not the case.

## A. Create a kb-sdk dynamic service

First, let's create a new Dynamic Service. This section follows the KBase SDK
instructions at https://kbase.github.io/kb_sdk_docs/tutorial/2_install.html, but
modifies the process to fit this tutorial.

1. Create or navigate to a project directory:

    ```shell
    mkdir myproject
    cd myproject
    ```

2. Create a local copy of the kb-sdk tool (`myproject`):

    ```shell
    docker run kbase/kb-sdk genscript > kb-sdk
    chmod +x kb-sdk
    export PATH="$PATH:${PWD}"
    ```

3. Initialize your new service (`myproject`)

    Set your username, replacing `yourusername` below with, well, your user name.

    > Note that if you are practicing this process and not going to actually
    > deploy the resulting service within KBase, you may use the instructions as
    > is.

    ```shell
    export KBASE_USERNAME="yourusername"
    ```

    Set your module's descriptive name, replacing `YourModuleName` with the
    module name you wish to use. It must be a string, is typically "proper
    cased" with an upper case letter at the beginning of each word, and no
    spaces between words.

    ```shell
    export SDK_MODULENAME="YourModuleName"
    ```

    Now create the service:

    ```shell
    export SDK_MODULE="${KBASE_USERNAME}${SDK_MODULENAME}"
    kb-sdk init --verbose --language python --user "${KBASE_USERNAME}" "${SDK_MODULE}"
    cd "${SDK_MODULE}"
    git init
    git add --all
    git commit -m "My first commit"
    make all
    git add --all; git commit -m "Initialized service with 'make all'"
    ```

    You'll note that the terminal is now in the newly created service module directory.

## B. Update with the dynamic service widget tool

1. Install the Dynamic Service Widget tool in the project directory (`myproject`)

    Let's open a new terminal in the project directory

    > The previous step will have left you in the service widget directory.

    ```shell
    git clone https://github.com/eapearson/kbase-ds-widget-tool
    cd kbase-ds-widget-tool
    ```

2. Copy the service directory path (`myproject/kbase-ds-widget-tool`)

    Copy this to the terminal, but don't press `Return` (`Enter`) yet!

    ```shell
    export MODULE_DIR=$(pbpaste)
    ```

3. Copy the directory path to the service (`myproject/yourusernameYourModuleName`)

    Back in the service terminal:

    ```shell
    pwd | pbcopy
    ```

4. Set the module directory (`myproject/kbase-ds-widget-tool`)

    Back in the widget tool directory, you may press the `Return` (`Enter`) key to set the
    module directory variable.

5. Check the service directory (`myproject/kbase-ds-widget-tool`):

    ```shell
    ./Taskfile check-module $MODULE_DIR
    ```

6. Initialize the service with service widget support (`myproject/kbase-ds-widget-tool`):

    ```shell
    ./Taskfile init-module $MODULE_DIR
    ```

7. Commit the changes (`myproject/yourusernameYourModuleName`)

    Back in the service directory:

    ```shell
    git add --all; git commit -m "Converted to dynamic service"
    ```

8. Create the SDK_MODULE variable for widget tool (`myproject/kbase-ds-widget-tool`)

    Back in the widget tool terminal, we'll do the copy/paste dance again,
    copying the following without hitting the `Enter` (or `Return`) key:

    ```shell
    export SDK_MODULE=$(pbpaste)
    ```

9. Copy the SDK_MODULE variable (`myproject/yourusernameYourModuleName`)

    Back in the service terminal:

    ```shell
    echo $SDK_MODULE | pbcopy
    ```

10. Create the SDK_MODULE variable for widget tool (`myproject/kbase-ds-widget-tool`)

    Back in the widget tool terminal:

    ```shell
    export SDK_MODULE=$(pbpaste)
    ```

11. Start the service container (`myproject/yourusernameYourModuleName`)

    Back in the service terminal:

    ```shell
    export KBASE_ENDPOINT=https://ci.kbase.us/services/ 
    export SERVICE_NAME=$(echo "$SDK_MODULE" | tr '[:upper:]' '[:lower:]')
    docker compose run --service-ports $SERVICE_NAME bash
    ```

    If docker compose fails due to port 5100 already being allocated, set the `PORT`
    environment variable first. E.g. the following starts the container using port 5200:

    ```shell
    PORT=5200 docker compose run --service-ports $SERVICE_NAME bash
    ```

    You should see a terminal prompt like this:

    ```shell
    root@youserusernameyourmodulename:/kb/module#
    ```

12. Check the container (`myproject/yourusernameYourModuleName`)

    ```shell
    python --version
    ```

    should show:

    ```shell
    Python 3.6.3 :: Anaconda, Inc.
    ```

13. You can now start the service's server (`myproject/yourusernameYourModuleName`)

    ```shell
    DEV=t ./scripts/start_server.sh
    ```

    The `DEV` environment variable tells the server whether it should run in
    "development" or "production" mode. Setting it to `t` (or any string beginning with
    the letter `t`, case insensitive), will set it to "development" mode. This is
    necessary for proper construction of local urls.

14. Check the service is up by calling the `status` endpoint (`myproject/kbase-ds-widget-tool`)

    Back in the widget tool terminal:

    ```shell
    curl -X POST http://localhost:5100 \
        -d "{\"version\": \"1.1\", \"id\": \"123\", \"method\": \"${SDK_MODULE}.status\", \"params\": []}"
    ```

    and you should get a response like this (but not as nicely formatted);

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

15. Try out the demo widgets

    The widget support package comes with some widget tools and also sample widgets.

    In this document we'll cover just two: the config widget, and the demos widget.

16. Try the built-in `config` widget (your browser)

    [http://localhost:5100/widgets/config](http://localhost:5100/widgets/config)

    (substituting for port 5100 if you need to).

17. The `demos` widget (your browser)

    [http://localhost:5100/widgets/demos](http://localhost:5100/widgets/demos)

    (substituting for port 5100 if you need to).
