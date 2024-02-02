# Publishing Your Service

So you've created a dynamic service, added some cool widgets, and you want it to be
available for use in Narratives?

To do this, you'll need to:

- create a GithHub Repo
- push your local code upt to the github repo
- register your app in the Catalog
- utilize the Narrative's widget developer tool to insert the widget into a narrative

## Prerequisites

In order to register your service and have it available for usage within KBase, you need
to have a KBase account, and have developer access for that account.

> TODO: write this up

## Create Github Repo

All KBase apps, including dynamic services, reside in the GitHub organization
[kbaseapps](https://github.com/kbaseapps).

In order to use a KBase app within a Narrative, it must first be registered. We'll get
to that later, but I wanted to note this because of a restriction this places on GitHub
app repos -- they __must__ be located in the `kbaseapps` organization. This is because
once an app is registered within KBase, there is no automated process for moving an app
repo from it's original location.

> ...
>
> TODO: document here how to create a repo within `kbaseapps`
>
> ...

Once you have created the repo, GitHub will provide instructions for pushing an existing
from the command line. Leave that page up, because we'll copy a copy of lines for our usage.

## Push code to repo

Once the repo is created, you are ready to push your app up to the repo.

> These instructions are for the command line, as a reference; of course you are free to
> use another process, such as git support in your favorite IDE.

If you have followed the [instructions](./creating-dynamic-service-for-widgets-tldr.md),
the service will already be configured as a GitHub repo.

1. We'll first need to add the GitHub repo as a "remote".

    From within the service directory, if you are using ssh with github:

    ```shell
    git remote add origin ssh://git@github.com/kbaseapps/yourusernameYourModuleName
    ```

    or if you are using https:

    ```shell
    git remote add origin https://github.com/kbaseapps/yourusernameYourModuleName
    ```

    To confirm the setting, you can issue:

    ```shell
    git remote -v
    ```

    and you should see

    ```shell
    origin	ssh://git@github.com/kbaseapps/yourusernameYourModuleName (fetch)
    origin	ssh://git@github.com/kbaseapps/yourusernameYourModuleName (push)
    ```

    or the https variant.

2. Next, push the repo up!

    ```shell
    git push -u origin main
    ```

    > You only need the `-u` (set-upstream) option the first time you push to github.

3. Confirm the push

    While on the github web page you had previously left open, refresh it. You should
    see the instructions replaced with the contents of your service repo.

## Register app

Registering an app with KBase is actually very simple.

> NOTE: update for the app

1. Take your browser to kbase: `https://ci.kbase.us`

2. Sign in with your KBase account that has developer access

3. Once signed in, navigate to the "Catalog", via the icon on the left side of the page.

    ![Catalog menu item](./images/catalog_menu_item.png)

4. Then navigate to the "Index" menu.

    ![Index menu item](./images/index_menu_item.png)

5. Then navigate to the "New Module Registration Page"

    ![New Module Regisration Page](./images/new_module_registration_page_menu_item.png)

6. In the "Register a KBase Module:" form, paste the url for your repo into the "Module
   Git URL" field. You can get this url from the browser when you are on the repo's
   initial page.

    ![Register a KBase Module form](./images/register_a_kbase_module_view.png)

7. You do not need to fill in the commit -- the Catalog registration will pull your repo
   from the most recent commit.

8. Click the "Register" button

9. The catalog will proceed to build and then register your service! If all goes well a
   simple message will be displayed at the bottom of the log display:

   ```text
   done
   ```

   ![Successful Registration Message](./images/registration-done.png)

## Use widget developer tool to insert into narrative

Your dynamic service widgets should now be available for usage in the narrative.

For purposes of this document, we'll assume that you have installed the demo widgets. If
you have removed them and created your own, you can translate these instructions to your
own case.

We'll be using the widget developer tool to ensure that your widgets appear correctly in
the narrative. It is important to note that typical usage of your widget will only be
possible:

- if a data viewer, the [NarrativeViewers](./updating-narrative-viewers.md) have been
updated and redeployed

- if an app output viewer, the app is available and registered, and has the [proper
configuration for widgets](./configuring-apps.md).

We'll formulate these instructions for the use case of creating a demonstration
Narrative in order to evaluate and/or share the progress of your widgets.

1. Open a new o Narrative

    Use the Navigator to open a new Narrative.

    ![Navigator New Narrative Button](./images/navigator-new-narrative.png)

2. Re-open the Narrative in developer mode

    From the hamburger menu (upper left corner of the page), select "Reopen in Developer
    Mode".

    > If this menu option is not available, you have not been registered as a KBase
    > developer.

    ![Reopen in Developer Mode Menu](./images/reopen-in-developer-mode.png)

    (After reopening in developer mode, you may return to "User Mode" at any time by
    reselecting the menu item, whose label will have become to "Reopen in User Mode".)

    Once reopened in developer mode, a new "developer" menu item will appear in the top
    menu

    ![Developer Menu Item](./images/developer-menu-item.png)

3. Use the "developer" menu to insert the "config" widget

    Open the developer menu and select the "Insert Generic Service Widget" item.

    ![Insert Generic Service Widget Menu Item](./images/insert-generic-service-widget-menu-item.png

    In the dialog that pops up

    ![Insert Generic Service Widget Form](./images/insert-generic-service-widget-form.png)

    enter the following information into the form:

    - Module: The name of your module, e.g. `yourusernameYourModuleName`
    - Widget: `config`
    - Title: Whatever you want the title of the cell to be
    - Subtitle: Whatver you want the subtitle of the cell to be

    For example:

    ![Insert Generic Service Widget Form
    Example](./images/insert-generic-service-widget-form-example.png)

    You should now see a new cell in the Narrative that looks like:

    ![Service Widget Cell with Config Widget](./images/config-service-widget-cell.png)

4. Use the "developer" menu to insert the "media viewer" widget

    > TO BE WRITTEN

