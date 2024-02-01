# Tasks

These are the tasks available via the `Taskfile` script

## `alias-me`

Creates a `run` command that you may issue instead of `./Taskfile` - a slight
convenience.

E.g.

```shell
% source ./Taskfile alias-me
% run
Taskfile <task> <args>
Runs the tasks listed below.
To find out more about them, either read the source
for Taskfile or the docs located in 'docs/tasks.md'.
Tasks:
     1	alias-me
     2	check-module
     3	help
     4	init-module
     5	shell
     6	status
Task completed in 0m0.019s
```

Note that the command must be run with `source` in order for the alias to take effect in
the current shell environment.

## `help`

Prints information about the `Taskfile` script as well as all available tasks.

## `status`

Prints information about the `ds-widget-tool`.

## `clean`

Removes development artifacts from the `resources` directory, to prevent them being
copied into a service.

The same files "cleaned" from `resources` are also included in `.gitignore`. The utility
of this script is to ease iteration over the process of adding widget support to a
dynamic service.

Such files include Python bytcode files, macOS finder files, editor backup files.

## `check-module $MODULE_PATH`

Inspects the directory provided by `$MODULE_PATH` and prints out the results. If all
inspections succeed, the directory contains a valid KBase Dynamic Service.

The inspection is not very deep, so it does not determine, for instance, that the
service actually runs or runs without error, etc.

## `init-module $MODULE_PATH`

Adds widget support to the KBase Dynamic Service located in the directory
`$MODULE_PATH`.

It will first check the module (the same as `check-module`) to ensure it is a valid
dynamic service.
