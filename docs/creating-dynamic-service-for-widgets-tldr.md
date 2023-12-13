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
    ```shell
    mkdir myproject
    cd myproject
    ```

2. Create a local copy of the kb-sdk tool (`myproject`):
    ```shell
    docker run kbase/kb-sdk genscript > ./kb-sdk
    chmod +x ./kb-sdk
    export PATH=$PATH:${PWD}
    ```

3. Initialize your new service (`myproject`)
    ```shell
    export KBASE_USERNAME="eapearson"
    export SDK_MODULENAME="WidgetDemo7"

    export SDK_MODULE="${KBASE_USERNAME}WidgetDemo7"
    kb-sdk init --verbose --language python --user "${KBASE_USERNAME}" "${SDK_MODULE}"
    cd ${SDK_MODULE}
    git init
    git add --all
    git commit -m "My first commit"
    make all
    git add --all; git commit -m "Initialized service with 'make all'"
    pwd | pbcopy
    ```

## B. Update with the dynamic service widget tool (`myproject/ds-widget-tool`)

    ```shell
    export MODULE_DIR=$(pbpaste)
    echo "${MODULE_DIR}"
    ./Taskfile check-module $MODULE_DIR
    ./Taskfile init-module $MODULE_DIR
    ```

4. Commit the changes (`myproject/yourusernameSomeService`)

    Let's go ahead and commit those changes, so we can observe what is changed when we
    convert the codebase to support widgets.

    In the terminal whose current working directory is the service directory `yourusernameSomeService`:

    ```shell
    git add --all; git commit -m "Converted to dynamic service"
    ```

6. Start the service (`myproject/yourusernamesomeservice`)

    Next we'll start the service and make sure it is working.

    To do this, we need to utilize a terminal in the service module directory, set two environment variables, and use `docker compose` to start the service.

    ```shell
    export KBASE_ENDPOINT=https://ci.kbase.us/services/ 
    docker compose run --service-ports yourusernamesomeservice bash
    ```

    Note that the service module name has been converted to lower case; this is a
    requirement for docker.

    If docker compose fails due to port 5100 already being allocated, set the `PORT`
    environment variable first. E.g. the following starts the container using port 5200:

    ```shell
    PORT=5200 docker compose run --service-ports yourusernamesomeservice bash
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

    You can now start the server:

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
    nodename: yourusernamesomeservice
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
        -d '{"version": "1.1", "id": "123", "method": "yourusernameSomeService.status", "params": []}'
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

7. Try out the demo widgets

    The widget support package comes with some widget tools and also sample widgets.

    In this document we'll cover just two: the config widget, and the demos widget.

8. The `config` widget (your browser)

    The config widget simply displays the contents of the service's configuration. This
    is a "Python widget", in that it is run as Python code that generates html.

    To invoke it, visit this url:

    [http://localhost:5100/widgets/config](http://localhost:5100/widgets/config)

    (substituting for port 5100 if you need to).

    The code for this widget resides in `src/widget/widgets/config`.

9. The `demos` widget (your browser)

    The demos widget is both a widget itself, and contains links to or other ways of
    accessing widgets.

    To invoke it, visit this url:

    [http://localhost:5100/widgets/demos](http://localhost:5100/widgets/demos)

    (substituting for port 5100 if you need to).

    The code for this widget resides in `src/widget/widgets/demos`.


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

The line of code looks /something like:

```python
self.callback_url = os.environ['SDK_CALLBACK_URL']
```

A direct dict attribute reference like this will fail if the attribute does not exist.

The documentation instructs to modify the codebase to avoid this problem. However, there
are several parts of the codebase that are affected by this. That code is not run into
when in dynamic service mode, but the missing environment variable is a problem easily
resolved by setting it to an empty string, which is what the instructions above provide.

