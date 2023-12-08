# Startup

How does a dynamic service start up?

- The image is run with the `entrypoint.sh` script invoked upon container start.

- The `entrypoint.sh` script first invokes `/kb/deployment/user-env.sh`

    > I don't know what this does - need to ask.

- The `entrypoint.sh` script then creates a `deploy.cfg` configuration file; this is the
  singular configuration for the service.

  - It uses the script `./scripts/prepare_deploy_cfg.py` to apply configuration
    properties to the configuration template to produce the configuration file

  - The configuration properties have two sources - environment variables (with some
    values synthesized from them), and a properties file.

  - The environment variables are:
    `KBASE_ENDPOINT` - the base URL for service urls, consisting of the `origin` and
    base path. Realistically, the base path is `/services/`, and the origin is of
    the format `https://ENV.kbase.us`, where `ENV` is one of `ci`, `next`, `appdev`, or a
    development environment (e.g. `narrative-dev` has been used). One exception is
    `https://kbase.us`, which is the origin for production.

    For example, `https://ci.kbase.us/services/` is the `KBASE_ENDPOINT` for the CI
    environment.

    > Note that `KBASE_ENDPOINT` always ends in a `/` - some code depends on this
    > practice, although kb-sdk actually assumes it does not, and thus creates
    > ill-formed urls (which work, but are incorrect, e.g.
    > `https://ci.kbase.us/services//ws` - note the `//`)

  - The `prepare_deploy_cfg.py` script generates the following service endpoints from
    the `KBASE_ENDPOINT`:
        - `kbase_endpoint`
        - `job_service_url`
        - `workspace_url`
        - `shock_url`
        - `handle_url`
        - `srv_wiz_url`
        - `njsw_url`

    A service url has the form `$KBASE_ENDPOINT/service_path`. E.g. the url for the
    Workspace service is `$KBASE_ENDPOINT/ws`, which resolves in CI to
    `https://ci.kbase.us/services//ws` (note the broken form, it should really be
    `https://ci.kbase.us/services/ws`).

    Note that this is both an incomplete and obsolete set of service urls. In practice,
    service paths as described above have never changed once deployed, so it is both
    safe and necessary often to craft service urls within code.

  - The `prepare_deploy_cfg.py` script then sets `auth_service_url` if the
    `AUTH_SERVICE_URL` environment variable is set, with no default value

    This is a relic from an era in which the auth service url was unlike that of other
    services, and in which services needed to grab that url for a single purpose - to
    validate a KBase auth token. In reality, the auth service path has been `auth` for
    many years now, and can be constructed just as for other services. It is indeed not
    a JSON-RPC 1.1 service, so its base url is used differently by an client for the
    auth service.

  - The `prepare_deploy_cfg.py` script then sets `auth_service_url_allow_insecure` if the
    `AUTH_SERVICE_URL_ALLOW_INSECURE` environment variable is set, defaulting to
    `false`.

  - The `prepare_deploy_cfg.py` script then sets a configuration property for any
    environment variable prefixed with `KBASE_SECURE_CONFIG_PARAM_`. The name of the
    config property is whatever follows `KBASE_SECURE_CONFIG_PARAM_` (no case
    conversion is applied.)

    Such environment variables are propagated from the service settings managed through
    the Catalog interface. A service developer, admin, or devop may add any number of such
    configuration properties through the Catalog interface.

  - The `prepare_deploy_cfg.py` script sets a configuration property for all
    properties found in the `./work/config.properties` file. This file is mounted into
    the container for the service by the app deployment machinery.

    > NOTE: I don't know what goes into this file.

  - The `prepare_deploy_cfg.py` renders the configuration file itself using the
    configuration properties as described above, and the configuration template supplied
    to it, which is always `./deploy.cfg` (at the root of the repo).

    - Any configuration property to be available to the service must be captured by this
      template; the configuration properties themselves are not available to the
      service.

    - You should augment this file to support `KBASE_SECURE_CONFIG_PARAM_` configuration
      properties you have established in the Catalog.

    - At present, the config template is:

```ini

[MODULE]
kbase-endpoint = {{ kbase_endpoint }}
job-service-url = {{ job_service_url }}
workspace-url = {{ workspace_url }}
shock-url = {{ shock_url }}
handle-service-url = {{ handle_url }}
srv-wiz-url = {{ srv_wiz_url }}
njsw-url = {{ njsw_url }}
auth-service-url = {{ auth_service_url }}
auth-service-url-allow-insecure = {{ auth_service_url_allow_insecure }}
scratch = /kb/module/work/tmp
```

        - Note the config "section" carries the name of your service module, in this case `MODULE`

    - The generated config file is actually written on top of the template (!) `./deploy.cfg`, with the original file copied to `./deploy.cfg.orig`

- The `entrypoint.sh` script then starts the server with the script
  `./scripts/start_server.sh`.

    - This script sets the environment variable `KB_DEPLOYMENT_CONFIG` to the path to
      the generated config file `deploy.cfg`, which we know is located at the root of
      the repo (`/kb/module` in the container).

- Whe the server starts, the configuration is read by the main server file
  `MODULE_Server.py`, where `MODULE_` is the name of your service module.

  - only the section with the name of your module (as shown above.)

  - this should be considered that canonical source of configuration. It will be
    provided to the DS Widget mechanism automatically. If you poke around you may see
    some code use the config file directly, but this is not a good practice, as future
    changes to kb-sdk may change the format of the config file. Your service should only
    care that a dict of configuration values is available.