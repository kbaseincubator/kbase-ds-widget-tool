# Getting Started

This document will guide you through the process of creating a new KBase Dynamic
Service, and upgrading with Widget support.

If you have an existing Dynamic Service and wish to add widgets to it, see the companion
document [Adding Widgets to an Existing Dynamic
Service](adding-widgets-to-an-existing-dynamic-service.md).

For more about Dynamic Services and the KBase SDK, see [the
documentation](https://kbase.github.io/kb_sdk_docs).

## Prerequisites

Since all tools run in docker containers, you will need `docker` installed on your
machine. On macOS or Windows [Docker
Desktop](https://www.docker.com/products/docker-desktop/) is a great, easy choice.

In addition, the `make` utility is required. This is ubiquitous on Linux, BSD, macOS,
and is available on Windows as well.

In this document each instruction step's title will be followed by the context,
usually a directory, in which the task will be carried out. Otherwise, I sense the
instructions may be confusing, as we utilize 3 different directories.

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

2. Create a local copy of the kb-sdk tool (`myproject`):

    > The upstream instructions specify to install this tool globally, but we'll just
    > use it locally for this tutorial, in order to be less intrusive in your system.
    > You may, of course, choose to install it in a central location and modify your
    > login profile to ensure it is always in your `PATH`.

    ```shell
    docker run kbase/kb-sdk genscript > ./kb-sdk
    chmod +x ./kb-sdk
    export PATH=$PATH:${PWD}
    ```

    > The `PATH` configuration is necessary because the `Makefile` assumes that `kb-sdk`
    > is in the search path

3. Initialize your new service (`myproject`)

    Here we use the `kb-sdk` tool set up above to create and populate a KBase "module".

    You can set up these environment variables in order to facilitate future commands.
    If you play to deploy this service, as opposed to simply practicing this process,
    you should use your KBase username below, and think of an appropriate module name.

    ```shell
    export KBASE_USERNAME="yourusername"
    export SDK_MODULENAME="YourModuleName"
    ```

    Then create the service with `kb-sdk`:

    ```shell
    export SDK_MODULE="${KBASE_USERNAME}${SDK_MODULENAME}"
    kb-sdk init --verbose --language python --user "${KBASE_USERNAME}" "${SDK_MODULE}"
    ```

    This creates a directory named after the module, `$SDK_MODULE`, and
    populates it with the initial code for a KBase app or dynamic service. Note that:

    - The service is implemented in `python`.
    - the initial sole owner of the project is the user specified in `$KBASE_USERNAME`
    - the name of the module is the concatenation of the username and a descriptive
      module name. This naming scheme helps ensure that the module name is unique within
      KBase. In this case it would be `yourusernameYourModuleName`.

    > In practice, I've not seen many people do this - they would simply name it use
    > `YourModuleName`, is it is briefer, less confusing, and naturally descriptive.

4. Next we'll set up git and make the first commit (`myproject/${SDK_MODULE}`).

    ```shell
    cd "${SDK_MODULE}"
    git init
    git add --all
    git commit -m "My first commit"
    ```

    This will help you see the changes that are made to your service, beyond the initial
    setup, as we add widget support, and then add widgets.

    > Tip: I would recommend opening your favorite IDE or git GUi for the
    > `${SDK_MODULE}` directory; you may then easily see the effects of each
    > step we are carrying out, without issuing any git commands.

5. Next, run all service preparation steps in one fell swoop (`myproject/${SDK_MODULE}`)

    ```shell
    make all
    ```

    That should have generated 7 files.

    For example, we can now list the changes since the commit above:

    ```shell
    % git status  -bs
    ## main
    M lib/yourusernameYourModuleName/yourusernameYourModuleNameeImpl.py
    M scripts/entrypoint.sh
    ?? bin/
    ?? lib/yourusernameYourModuleName/yourusernameYourModuleNameImpl.py.bak-2023-12-07-18-42-21
    ?? lib/yourusernameYourModuleName/yourusernameYourModuleNameServer.py
    ?? scripts/start_server.sh
    ?? test/run_tests.sh
    ```

6. Commit the changes again (`myproject/${SDK_MODULE}`)

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

## B. Get the Dynamic Service Widget Tool (`myproject`)

Before we continue to convert this KBase service module into a dynamic service with
widgets, let us get familiar with the tool we'll be using.

This tool is the Dynamic Service Widget Tool , `ds-widget-tool`, which, similar to
`kb-sdk`, runs as a docker container.

1. Obtain a copy of the tool (`myproject`)

    To get started, we'll install a copy of the `ds-widget-tool` locally. At present, it cannot be
    run remotely, but must be installed locally.

    First, navigate back to the project directory as we'll be installing the tool there.

    ```shell
    cd ..
    ```

    The contents of this directory should be:

    ```shell
    % ls
    kb-sdk			yourusernameYourModuleName
    ```

    Then install the tool:

    ```shell
    git clone https://github.com/eapearson/ds-widget-tool
    ```

2. Ensure the tool will work correctly (`myproject/ds-widget-tool`)

    For convenience, we'll be running the commands inside the ds-widget-tool directory:

    ```shell
    cd ds-widget-tool
    ```

    The tool works via a script named `Taskfile`, to which you will provide commands and parameters.

    First, you can run the tool without any command to get a help screen which lists
    available commands:

    ```shell
    ./Taskfile
    ``

    which prints

    ```shell
    To find out more about them, either read the source
    for ./Taskfile or the docs located in 'docs/tasks.md'.
    Tasks:
     1  alias-me
     2  bash
     3  check-module
     4  help
     5  init-module
     6  shell
     7  status
    Task completed in 0m0.009s
    ```

    To ensure the tool will work, run the `status` task, which will run the
    `status.py` script within the container.

    ```shell
    ./Taskfile status
    ```

    You should see:

    ```shell
    This is the ds-widget-tool, a docker-based set of Python scripts
    to help manage a KBase dynamic service with widgets.

    See https://github.com/eapearson/ds-widget-tool.
    ```

## C. Add Widget Support to the Dynamic Service

Now we are ready to add widget support to the dynamic service!

1. Verify the module (`myproject/ds-widget-tool`)

    Our first step is to ensure that the KBase SDK service module is ready to receive
    widget support. To do this, we run the `check-module` command, passing it the
    directory of the service we wish to work with.

    ```shell
    ./Taskfile check-module $MODULE_DIR    
    ```

    where `$MODULE_DIR` is the absolute path to the service module directory.

    You may use any means necessary to determine the absolute path to the directory, the
    simplest of which is probably to open a terminal in that directory, issue `pwd`, 
    copy the result, and set the environment variable like so:

    ```shell
    export MODULE_DIR=/path/to/projectdir/yourusernameYourModuleName
    ```

    > On macOS you can issue `pwd | pbcopy` to avoid the mouse usage of highlight-copy.

    There are various clever ways of doing this on the command line, but many are not
    universal across systems.

    E.g. this

    ```shell
    ./Taskfile check-module $(find $(cd ..; pwd) -maxdepth 1 -name yourusernameYourModuleName)
    ```

    or

    ```shell
    export MODULE_DIR=$(find $(cd ..; pwd) -maxdepth 1 -name yourusernameYourModuleName)
    ./Taskfile check-module $MODULE_DIR
    ```

    should work on most POSIX compliant systems if `yourusernameYourModuleName` and
    `ds-widget-tool` were placed in the same project directory (i.e. they are sibling directories.)

    In any case, you should see something like this:

    ```shell
     % ./Taskfile check-module $MODULE_DIR
   
    Using service directory /Users/erikpearson/Work/KBase/2023/service-widget/practice/yourusernameYourModuleName

    ⓘ Analyzing module directory ...

    ✅ "kbase.yml" successfully loaded
    ✅ The service module "eapearsonWidgetDemo7" is not a dynamic service and will be converted

    ⓘ Module name        : eapearsonWidgetDemo7
    ⓘ Module description : A KBase module
    ⓘ Service language   : python
    ⓘ Module version     : 0.0.1
    ⓘ Owners             : eapearson

    Task completed in 0m0.480s
    ```

2. Use the `init-module` task to upgrade the module (`myproject/ds-widget-tool`)

    Now we are ready to run the `init-module` task  to add the widget support to the module
    codebase.

    Similar to when we checked the module, we issue the task in a terminal:

    ```shell
    ./Taskfile init-module $MODULE_DIR
    ```

    If all goes well, you should see output like the following:

    ```shell
    ⓘ Analyzing module directory ...

    ✅ "kbase.yml" successfully loaded
    ✅ The service module "eapearsonWidgetDemo7" is not a dynamic service and will be converted

    ⓘ Module name        : eapearsonWidgetDemo7
    ⓘ Module description : A KBase module
    ⓘ Service language   : python
    ⓘ Module version     : 0.0.1
    ⓘ Owners             : eapearson

    ✅ Module configured as dynamic service
    ✅ Auth client imports fixed
    ✅ Server snippets added
    ✅ Test file repaired
    ✅ Impl snippets added
    ✅ gitignore snippets added
    ✅ Docker compose copied
    ✅ Python widget support copied
    ✅ Static widget support copied
    ✅ Widget docs copied
    ✅ Fixed Makefile
    ✅ Debugging suppport added to impl file

    Task completed in 0m0.664s
    ```

3. Start the service (`myproject/${MODULE_DIR}`)

    Next we'll start the service and make sure it is working.

    To do this, we need to utilize a terminal in the service module directory, set two environment variables, and use `docker compose` to start the service.

    ```shell
    export KBASE_ENDPOINT=https://ci.kbase.us/services/ 
    docker compose run --rm --service-ports yourusernameyourmodulename bash
    ```

    Note that the service module name has been converted to lower case; this is a
    requirement for docker.

    A copy-pastable form without the hardcoded service name `yourusernameyourmodulename`
    is:

    ```shell
    docker compose run --rm --service-ports $(echo "${SDK_MODULE}" | tr '[:upper:]' '[:lower:]') bash
    ```

    If docker compose fails due to port 5100 already being allocated, set the `PORT`
    environment variable first. E.g. the following starts the container using port 5200:

    ```shell
    PORT=5200 docker compose run --rm --service-ports yourusernameyourmodulename bash
    ```

    This will leave you inside the service container on the bash shell command line.

    We are utilizing this workflow because it facilitates workflow similar to your local
    machine, but inside the container.

    For instance, you can determine the version of Python running in the official KBase
    service container:

    ```shell
    % python --version
    Python 3.6.3 :: Anaconda, Inc.
    ```

    ```shell
    DEV=t ./scripts/start_server.sh
    ```

    The `DEV` environment variable tells the server whether it should run in
    "development" or "production" mode. Setting it to `t` (or any string beginning with
    the letter `t`, case insensitive), will set it to "development" mode. This is
    necessary for proper construction of urls.

    You should see a long printout of the status of the server:

    ```shell
    *** Starting uWSGI 2.0.17.1 (64bit) on [Fri Dec  8 18:39:47 2023] ***
    compiled with version: 4.8.2 20140120 (Red Hat 4.8.2-15) on 15 August 2018 17:45:24
    os: Linux-6.5.11-linuxkit #1 SMP PREEMPT_DYNAMIC Mon Dec  4 10:03:25 UTC 2023
    nodename: yourusernameyourmodulename
    machine: x86_64
    clock source: unix
    pcre jit disabled
    detected number of CPU cores: 6
    current working directory: /kb/module
    detected binary path: /miniconda/bin/uwsgi
    uWSGI running as root, you can use --uid/--gid/--chroot options
    *** WARNING: you are running uWSGI as root !!! (use the --uid flag) *** 
    your memory page size is 4096 bytes
    detected max file descriptor number: 1048576
    lock engine: pthread robust mutexes
    thunder lock: disabled (you can enable it with --thunder-lock)
    uWSGI http bound on :5000 fd 4
    uwsgi socket 0 bound to TCP address 127.0.0.1:42723 (port auto-assigned) fd 3
    uWSGI running as root, you can use --uid/--gid/--chroot options
    *** WARNING: you are running uWSGI as root !!! (use the --uid flag) *** 
    Python version: 3.6.3 |Anaconda, Inc.| (default, Nov 20 2017, 20:43:55)  [GCC 7.2.0]
    Python main interpreter initialized at 0xc553b0
    uWSGI running as root, you can use --uid/--gid/--chroot options
    *** WARNING: you are running uWSGI as root !!! (use the --uid flag) *** 
    python threads support enabled
    your server socket listen backlog is limited to 100 connections
    your mercy for graceful operations on workers is 60 seconds
    mapped 688464 bytes (672 KB) for 25 cores
    *** Operational MODE: preforking+threaded ***
    WSGI app 0 (mountpoint='') ready in 0 seconds on interpreter 0xc553b0 pid: 46 (default app)
    uWSGI running as root, you can use --uid/--gid/--chroot options
    *** WARNING: you are running uWSGI as root !!! (use the --uid flag) *** 
    *** uWSGI is running in multiple interpreter mode ***
    spawned uWSGI master process (pid: 46)
    spawned uWSGI worker 1 (pid: 48, cores: 5)
    spawned uWSGI worker 2 (pid: 51, cores: 5)
    spawned uWSGI worker 3 (pid: 56, cores: 5)
    spawned uWSGI worker 4 (pid: 63, cores: 5)
    spawned uWSGI worker 5 (pid: 67, cores: 5)
    spawned uWSGI http 1 (pid: 72)
    ```

    As a sanity check, you can call the `status` endpoint within the service. This is a
    standard endpoint in all KBase dynamic services (and most KBase core services as well).

    From any terminal window, issue this command (assuming you have the `curl` program
    installed, if not, see below). Also, note that if you had to use a different port,
    replace the `5100` which whichever port you used.

    ```shell
    curl -X POST http://localhost:5100 \
        -d '{"version": "1.1", "id": "123", "method": "yourusernameYourModuleName.status", "params": []}'
    ```

    and you should get a response like this:

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

4. Try out the demo widgets

    The widget support package comes with some widget tools and also sample widgets.

    In this document we'll cover just two: the config widget, and the demos widget.

5. The `config` widget (your browser)

    The config widget simply displays the contents of the service's configuration. This
    is a "Python widget", in that it is run as Python code that generates html.

    To invoke it, visit this url:

    [http://localhost:5100/widgets/config](http://localhost:5100/widgets/config)

    (substituting for port 5100 if you need to).

    THe code for this widget resides in `src/widget/widgets/config`.

6. The `demos` widget (your browser)

    The demos widget is both a widget itself, and contains links to or other ways of
    accessing widgets.

    To invoke it, visit this url:

    [http://localhost:5100/widgets/demos](http://localhost:5100/widgets/demos)

    (substituting for port 5100 if you need to).

    The code for this widget resides in `src/widget/widgets/demos`.

## Registering your new dynamic service

> TODO, or out of scope? I think at least a brief doc would be useful

- commit all the changes:

    ```shell
    git add --all; git commit -m "Added widget support"
    ```

- create re
po at github
- copy remote command
- add as remote in the service dir
- push to repo
- go to the catalog new registration page [https://ci.kbase.us/legacy/catalog/register](https://ci.kbase.us/legacy/catalog/register)
- visit the repo, copy the url of the repo
- paste the repo url into the catalog registration page
- register

- verify it is up:

```shell
curl -X POST https://ci.kbase.us/services/service_wizard/rpc \
    -H 'Accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "version": "1.1",
    "id": "123",
    "method": "ServiceWizard.get_service_status",
    "params": [{"module_name": "eapearsonWidgetTest10", "version": "dev"}]
}'
```

- Copy the url from the result:

```json
{
    "version": "1.1",
    "result": [
        {
            "git_commit_hash": "e1f05e7c6555f6de25a20d27ebe1a2e48f983ad0",
            "status": "active",
            "version": "0.0.1",
            "hash": "e1f05e7c6555f6de25a20d27ebe1a2e48f983ad0",
            "release_tags": [
                "dev"
            ],
            "url": "https://ci.kbase.us:443/dynserv/e1f05e7c6555f6de25a20d27ebe1a2e48f983ad0.eapearsonWidgetTest10",
            "module_name": "eapearsonWidgetTest10",
            "health": "healthy",
            "up": 1
        }
    ],
    "id": "123"
}
```

- Invoke the status endpoint to make sure it is working:

```shell
curl -X POST https://ci.kbase.us:443/dynserv/e1f05e7c6555f6de25a20d27ebe1a2e48f983ad0.eapearsonWidgetTest10 \
    -d '{"version": "1.1", "id": "123", "method": "eapearsonWidgetTest10.status", "params": []}'
```

- Invoke the config widget in a browser:

```url
https://ci.kbase.us:443/dynserv/e1f05e7c6555f6de25a20d27ebe1a2e48f983ad0.eapearsonWidgetTest10/widgets/config
```

- Invoke the demos widget in a browser

```url
https://ci.kbase.us:443/dynserv/e1f05e7c6555f6de25a20d27ebe1a2e48f983ad0.eapearsonWidgetTest10/widgets/demos
```

## Anatomy of the Widget Support

Now that we've converted the service module to a dynamic service that supports widgets,
let's explore how this was accomplished.

Fortunately we had a fresh git status before the changes, so we can list all of the
files.

> TODO: write this section.

## Notes

### Conversion of standard SDK app to a dynamic service

Other than the configuration change to set the dynamic service flag, there are bits of
the codebase that assume it is running as an app.

The only one that causes a problem is that when the `SDK_CALLBACK_URL` is not set, the
server will fail to start.

The line of code looks something like:

```python
self.callback_url = os.environ['SDK_CALLBACK_URL']
```

A direct dict attribute reference like this will fail if the attribute does not exist.

The documentation instructs to modify the codebase to avoid this problem. However, there
are several parts of the codebase that are affected by this. That code is not run into
when in dynamic service mode, but the missing environment variable is a problem easily
resolved by setting it to an empty string, which is what the instructions above provide.

