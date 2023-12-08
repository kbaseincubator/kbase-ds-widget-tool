# HOW TO ...

## Start Dev Environment

Let's try dev in a container ... maybe even add a devcontainer too ...

Start the service container with the "bash" command, which puts it into the bash shell.

> see `./scripts/entrypoint.sh`

> Note: This should have been "shell", with the shell being whatever one we currently support.

```shell
chmod a+x scripts/entrypoint.sh
export KBASE_ENDPOINT=https://ci.kbase.us/services/ 
docker compose run --service-ports eapearsonservicewidgetdemo bash
```

You can then maybe point your VSC interpreter to the container. If that doesn't work
well, maybe the best thing is to set up a devcontainer...

Make sure the container is as expected. E.g.

```shell
python --version
```

which currently returns

```shell
Python 3.6.3 :: Anaconda, Inc.
```

The server can now be started, like:

```shell
sh ./scripts/start_server.sh
```

or:

```shell
chmod a+x ./scripts/start_server.sh
./scripts/start_server.sh
```

In any case, you should then see something like:

```shell

root@eapearsonservicewidgetdemo:/kb/module# ./scripts/start_server.sh
*** Starting uWSGI 2.0.17.1 (64bit) on [Mon Dec  4 17:34:57 2023] ***
compiled with version: 4.8.2 20140120 (Red Hat 4.8.2-15) on 15 August 2018 17:45:24
os: Linux-6.5.11-linuxkit #1 SMP PREEMPT_DYNAMIC Mon Dec  4 10:03:25 UTC 2023
nodename: eapearsonservicewidgetdemo
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
uwsgi socket 0 bound to TCP address 127.0.0.1:42045 (port auto-assigned) fd 3
uWSGI running as root, you can use --uid/--gid/--chroot options
*** WARNING: you are running uWSGI as root !!! (use the --uid flag) *** 
Python version: 3.6.3 |Anaconda, Inc.| (default, Nov 20 2017, 20:43:55)  [GCC 7.2.0]
Python main interpreter initialized at 0x1c6e400
uWSGI running as root, you can use --uid/--gid/--chroot options
*** WARNING: you are running uWSGI as root !!! (use the --uid flag) *** 
python threads support enabled
your server socket listen backlog is limited to 100 connections
your mercy for graceful operations on workers is 60 seconds
mapped 688464 bytes (672 KB) for 25 cores
*** Operational MODE: preforking+threaded ***
WSGI app 0 (mountpoint='') ready in 0 seconds on interpreter 0x1c6e400 pid: 52 (default app)
uWSGI running as root, you can use --uid/--gid/--chroot options
*** WARNING: you are running uWSGI as root !!! (use the --uid flag) *** 
*** uWSGI is running in multiple interpreter mode ***
spawned uWSGI master process (pid: 52)
spawned uWSGI worker 1 (pid: 54, cores: 5)
spawned uWSGI worker 2 (pid: 55, cores: 5)
spawned uWSGI worker 3 (pid: 61, cores: 5)
Python auto-reloader enabled
spawned uWSGI worker 4 (pid: 67, cores: 5)
spawned uWSGI worker 5 (pid: 72, cores: 5)
spawned uWSGI http 1 (pid: 75)

```

The service is running on port 5000 inside the container, and 5100 outside.

> Note: on macOS, port 5000 is reserved

You can make sure it is up in two ways.

First, from your host:


```shell
curl -X POST http://localhost:5200 \
    -d '{"version": "1.1", "id": "123", "method": "epearsonFirst.status", "params": []}'
```

which should return a result (reformatted for readability):

```json
{
    "version": "1.1",
    "result": [
        {
            "state": "OK",
            "message": "",
            "version": "0.0.1",
            "git_url": "ssh://git@github.com/eapearson/eapearsonServiceWidgetDemo",
            "git_commit_hash": "9b839be4e44448ec04355ec7ee293061d574f39e"
        }
    ],
    "id": "123"
}
```

I like to use the "RESTer" extension for Firefox (using developer edition) to poke at
the service, but you can use the command line as well.

If this doesn't work, as a sanity check, inside the container you can issue a curl
command:

> If you don't know how to open a shell into a running container, it is easy to use
> docker desktop to do the same (well, it is always easier!)

```shell
# curl http://localhost:5000
```

which should return an error (reformatted for readability):

```json
{
    "error": {
        "code": -32700,
        "name": "Parse error",
        "message": "Expecting value: line 1 column 1 (char 0)",
        "error": null
    },
    "version": "1.1"
}```

But nicer is a real request:

```shell
curl -X POST http://localhost:5000 \
    -d '{"version": "1.1", "id": "123", "method": "epearsonServiceWidgetDemo.status", "params": []}'
```

which should return a result (reformatted for readability):

```json
{
    "version": "1.1",
    "result": [
        {
            "state": "OK",
            "message": "",
            "version": "0.0.1",
            "git_url": "ssh://git@github.com/eapearson/eapearsonServiceWidgetDemo",
            "git_commit_hash": "9b839be4e44448ec04355ec7ee293061d574f39e"
        }
    ],
    "id": "123"
}
```

## Anatomy of a Landing Page

One of the demos in the example service is a simple landing page for `Media` objects. It
is a clone of the existing landing page found in the Narrative and kbase-ui.

As for external dependencies, it utilizes:

- jQuery
- Bootstrap 5
- DataTables

It also utilizes a pair of KBase utilities:

- lib.js - helper functions
- client.js - generic client for accessing KBase JSON-RPC 1.1 services

The widget is implemented with:

- external dependencies loaded via a CDN
- Javascript is loaded globally
- jQuery is used to render data into the widget

This represents a basic parity with Narrative development practices, with the exception
that the Narrative loads 








http://localhost:5100/widgets/media_viewer?token=MYTOKEN&ref=58110/2/10