import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from string import Template

from yaml import YAMLError, dump, safe_load

from .utils import error_exit, info_feedback, success_feedback


class WidgetSupport(object):
    def __init__(self, sdk_module_directory):
        self.sdk_module_directory = sdk_module_directory
        self.checked = False

    def ensure_attribute(self, data, name, label):
        attribs = name.split('.')

        if len(attribs) == 0:
            error_exit(f"Attribute given for {label} cannot be empty.")

        for attrib in attribs:
            if attrib not in data:
                error_exit(f"Attribute {name} expected in {label} but was not found.")
            data = data.get(attrib)

        return data
        
    def get_attribute(self, data, attribute_path, default_value=None):
        attribs = attribute_path.split('.')

        for attrib in attribs:
            if attrib not in data:
                return default_value
            data = data.get(attrib)

        return data

    def load_kbase_config(self):
        # Determine if it is a directory
        module_dir = Path(self.sdk_module_directory)

        if not module_dir.is_dir():
            error_exit(f'The given module directory "{module_dir.resolve()}" does not exist')

        # See if it is probably a module directory.
        # We do that by looking for the "kbase.yml" file, with the proper structure.
        # Ideally we don't want it to be touched yet, but it is okay if it is.
        kbase_config_file = module_dir.joinpath('kbase.yml')
        if not kbase_config_file.is_file():
            error_exit(f'The KBase module config file "kbase.yml" was not found in the module directory {self.sdk_module_directory}: {kbase_config_file.resolve()}')

        try:
            with open(kbase_config_file, "r", encoding="utf-8") as fin:
                return safe_load(fin)
        except OSError as oserr:
            error_exit(f"Error opening or reading kbase config file: {str(oserr)}")
        except YAMLError as yerr:
            error_exit(f"Error parsing config file as YAML: {str(yerr)}")
            

    def save_kbase_config(self, kbase_config):
        # Determine if it is a directory
        module_dir = Path(self.sdk_module_directory)

        if not module_dir.is_dir():
            error_exit(f'The given module directory "{module_dir.resolve()}" does not exist')

        # See if it is probably a module directory.
        # We do that by looking for the "kbase.yml" file, with the proper structure.
        # Ideally we don't want it to be touched yet, but it is okay if it is.
        kbase_config_file = module_dir.joinpath('kbase.yml')
        # if not kbase_config_file.is_file():
        #     error_exit(f'The KBase module config file "kbase.yml" was not found in the module directory {self.sdk_module_directory}: {kbase_config_file.resolve()}')

        try:
            with open(kbase_config_file, "w", encoding="utf-8") as fout:
                return dump(kbase_config, fout)
        except OSError as oserr:
            error_exit(f"Error opening or reading kbase config file: {str(oserr)}")
        except YAMLError as yerr:
            error_exit(f"Error parsing config file as YAML: {str(yerr)}")

    def ensure_valid_service(self):
        """
        Ensures that the given directory implements a KBase kb-sdk dynamic service
        """
        info_feedback('Analyzing module directory ...')

        kbase_config = self.load_kbase_config()

        # # Determine if it is a directory
        # if not os.path.isdir(self.sdk_module_directory):
        #     error_exit(f'The given directory "{self.sdk_module_directory}" does not exist')

        # # See if it is probably a module directory.
        # # We do that by looking for the "kbase.yml" file, with the proper structure.
        # # Ideally we don't want it to be touched yet, but it is okay if it is.
        # kbase_config_file = Path(os.path.join(self.sdk_module_directory, 'kbase.yml'))
        # if not kbase_config_file.is_file():
        #     error_exit(f'The KBase module config file "kbase.yml" was not found in the module directory {self.sdk_module_directory}: {kbase_config_file.resolve()}')

        # success_feedback('"kbase.yml" config file found, it looks like a KBase kb-sdk service!')

        # try:
        #     with open(kbase_config_file, "r", encoding="utf-8") as fin:
        #         kbase_config = safe_load(fin)
        # except OSError as oserr:
        #     error_exit(f"Error opening or reading kbase config file: {str(oserr)}")
        # except YAMLError as yerr:
        #     error_exit(f"Error parsing config file as YAML: {str(yerr)}")

        success_feedback('"kbase.yml" successfully loaded')

        # if self.ensure_attribute(kbase_config, "service-config.dynamic-service", "KBase Config") is not True:
        #     error_exit('The KBase kb-sdk service must already be configured as a dynamic service')

        module_name = self.ensure_attribute(kbase_config, "module-name", "KBase Config")

        if self.get_attribute(kbase_config, 'service-config.dynamic-service'):
            success_feedback(f'The service module "{module_name}" is indeed a dynamic service as well')
        else:
            success_feedback(f'The service module "{module_name}" is not a dynamic service and will need to be converted')

        info_feedback(f'Module name        : {module_name}')
        info_feedback(f'Module description : {self.ensure_attribute(kbase_config, "module-description", "KBase Config")}')
        info_feedback(f'Service language   : {self.ensure_attribute(kbase_config, "service-language", "KBase Config")}')
        info_feedback(f'Module version     : {self.ensure_attribute(kbase_config, "module-version", "KBase Config")}')
        info_feedback(f'Owners             : {", ".join(self.ensure_attribute(kbase_config, "owners", "KBase Config"))}')
        self.sdk_module_name = kbase_config['module-name']
        self.checked = True


    def assert_has_been_checked(self):
        if self.checked is not True:
            error_exit('Must ensure the target directory is a valid SDK Dynamic Service before processing it.')

    def get_resources_path(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(current_dir, '../../resources')
        if not os.path.isdir(path):
            error_exit('The resources directory was not found')
        return path

    def get_resource_dir(self, dir_path):
        resources_path = self.get_resources_path()
        dir_path = os.path.join(resources_path, dir_path)
        if not os.path.isdir(dir_path):
            error_exit(f'The directory {dir_path} does not exist') 
        return dir_path

    def get_resource_file(self, file_path):
        resources_path = self.get_resources_path()
        file_path = Path(os.path.join(resources_path, file_path))
        if not file_path.is_file():
            error_exit(f'The directory {file_path.resolve()} does not exist') 
        return file_path


    def read_resource_file(self, file_path):
        resources_path = self.get_resources_path()
        with open(os.path.join(resources_path, file_path), "r", encoding="utf-8") as fin:
            return fin.read()

    def add_server_snippets(self):
        """
        Adds snippets of python to add support for the /widgets endpoint within the service.
        """
        # Add the import snippet.
        import_snippet = self.read_resource_file('snippets/service-server-snippet-0.txt')

        # Add the path handling snippet.
        handler_snippet = self.read_resource_file('snippets/service-server-snippet-1.txt')

        server_filename = f"{self.sdk_module_name}Server.py"
        server_file_path = os.path.join(self.sdk_module_directory, 'lib', self.sdk_module_name, server_filename)
        if not os.path.isfile(server_file_path):
            error_exit(f'Could not find module server file: {server_file_path}')

        with open(server_file_path, "r", encoding="utf-8") as fin:
            server_file_lines = fin.read().split('\n')

        # Okay, place the import line at the end of the imports.
        # We determine this based on the presence of the global variable DEPLOY which
        # appears at the end of the imports.

        server_file_replaced = []
        for line in server_file_lines:
            if line.startswith('DEPLOY ='):
                server_file_replaced.append(import_snippet)
                server_file_replaced.append(line)
            elif "status = '500 Internal Server Error'" in line:
                server_file_replaced.append(line)
                server_file_replaced.append(handler_snippet)
            else:
                server_file_replaced.append(line)

        new_server_file_contents = '\n'.join(server_file_replaced)

        self.backup_file(server_file_path)

        with open(server_file_path, "w", encoding="utf-8") as fout:
            fout.write(new_server_file_contents)


    def sdk_python_placeholder(self, placeholder):
        return re.compile(f'[\\s]*#[\\s]*{placeholder}')

    def get_impl_file(self):
        impl_filename = f"{self.sdk_module_name}Impl.py"
        impl_file_path = Path(os.path.join(self.sdk_module_directory, 'lib', self.sdk_module_name, impl_filename))
        if not impl_file_path.is_file():
            error_exit(f'Could not find module impl file: {impl_file_path.resolve()}')
        return impl_file_path

    def read_impl_file(self):
        impl_file = self.get_impl_file()
        return impl_file.read_text(encoding='utf-8')


    def write_impl_file(self, contents):
        impl_file = self.get_impl_file()
        self.backup_file(impl_file)
        impl_file.write_text(contents, encoding="utf-8")

    def fix_impl_file(self):
        """
        Adds snippets of python to add support for the /widgets endpoint within the service.
        """

        import_snippet = self.read_resource_file('snippets/service-impl-snippet-0.txt')
        widgets_snippet = self.read_resource_file('snippets/service-impl-snippet-1.txt')

        impl_file_lines = self.read_impl_file().split('\n')

        # Okay, place the import line at the end of the imports.
        # We determine this based on the presence of the global variable DEPLOY which
        # appears at the end of the imports.

        impl_file_replaced = []
        for line in impl_file_lines:
            if re.match(self.sdk_python_placeholder('END_HEADER'), line):
                # Insert the import snippet just before the "END HEADER" protected
                # text placeholder.
                impl_file_replaced.append(import_snippet)
                impl_file_replaced.append(line)
            elif re.match(self.sdk_python_placeholder('END_CONSTRUCTOR'), line):
                # Insert the widget definitions snippet just before the END_CONSTRUCTOR
                # protected text placeholder.
                impl_file_replaced.append(widgets_snippet)
                impl_file_replaced.append(line)
            elif "os.environ['SDK_CALLBACK_URL']" in line:
                # Replace the usage of a dict key (which breaks for a dynamic service)
                # with dict "get". This is within the protected constructor block, so
                # safe to do one time.
                line = line.replace("os.environ['SDK_CALLBACK_URL']", "os.environ.get('SDK_CALLBACK_URL')")
            else:
                impl_file_replaced.append(line)

        new_impl_file_contents = '\n'.join(impl_file_replaced)

        self.write_impl_file(new_impl_file_contents)



    def fix_test_file(self):
        """
        Fixes the server test file.
        """

        test_filename = f"{self.sdk_module_name}_server_test.py"
        test_file_path = Path(os.path.join(self.sdk_module_directory, 'test', test_filename))
        if not test_file_path.is_file():
            error_exit(f'Could not find test file: {test_file_path.resolve()}')

        test_file_lines = test_file_path.read_text(encoding='utf-8').split('\n')

        # Okay, place the import line at the end of the imports.
        # We determine this based on the presence of the global variable DEPLOY which
        # appears at the end of the imports.

        test_file_replaced = []
        for line in test_file_lines:
            if "os.environ['SDK_CALLBACK_URL']" in line:
                # Replace the usage of a dict key (which breaks for a dynamic service)
                # with dict "get". This is within the protected constructor block, so
                # safe to do one time.
                line = line.replace("os.environ['SDK_CALLBACK_URL']", "os.environ.get('SDK_CALLBACK_URL')")
            else:
                test_file_replaced.append(line)

        new_test_file_contents = '\n'.join(test_file_replaced)

        self.backup_file(test_file_path)

        test_file_path.write_text(new_test_file_contents, encoding="utf-8")


    def backup_file(self, file_path):
        # TODO: ensure file_path everywhere.
        file_path = Path(file_path)

        file_timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

        file_backup_path = f"{file_path.resolve()}.bak-{file_timestamp}"

        shutil.move(file_path, file_backup_path)

    
    def backup_module_file(self, file_path, move = False):
        # TODO: ensure file_path everywhere.
        file_path = self.get_module_path(file_path)

        file_timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

        file_backup_path = f"{file_path.resolve()}.bak-{file_timestamp}"

        if move:
            shutil.move(file_path, file_backup_path)
        else:
            shutil.copy(file_path, file_backup_path)


    def add_gitignore_snippets(self):
        """
        Adds missing lines to gitignore
        """
        #
        # Add the gitignore snippet to the gitignore
        #

        gitignore_snippet = self.read_resource_file('snippets/gitignore.txt')

        gitignore_filename = ".gitignore"

        file_path = Path(os.path.join(self.sdk_module_directory, gitignore_filename))
        if not file_path.is_file():
            error_exit(f'Could not find gitignore file: {file_path.resolve()}')

        file_lines = file_path.read_text(encoding='utf-8').split('\n')

        file_lines.append(gitignore_snippet)
        
        self.backup_file(file_path)

        new_file_contents = '\n'.join(file_lines)

        file_path.write_text(new_file_contents, encoding="utf-8")

    def copy_docker_compose(self):
        # Read docker compose file
        docker_compose_source = self.read_resource_file('docker/docker-compose.yml')

        # We need to lower case the module name, as docker does not like services with non-lowercase.
        service_name = self.sdk_module_name.lower()

        # development_service_port = int(os.environ.get('DEVELOPMENT_SERVICE_PORT') or '5100')

        # substitute
        docker_compose_content = Template(docker_compose_source).substitute({
            "service_name": service_name,
            # "port": development_service_port
        })

        # save into the service
        docker_compose_path = os.path.join(self.sdk_module_directory, 'docker-compose.yml')

        with open(docker_compose_path, "w", encoding="utf-8") as fout:
            fout.write(docker_compose_content)

    def copy_resource_dir(self, source, dest=None):
        source_dir = self.get_resource_dir(source)
        dest_dir = self.get_module_dir(dest or source)
        if dest_dir.is_dir() or dest_dir.is_file():
            raise Exception(f'Destination directory already exists: {dest_dir.resolve()}')
        shutil.copytree(source_dir, dest_dir)
        success_feedback(f'Resource directory {source} successfully copied')

    def copy_resource_file(self, source, dest):
        source_file = self.get_resource_file(source)
        dest_file = self.get_module_path(dest)
        shutil.copy(source_file, dest_file)
        success_feedback('Python widget support copied')

    def get_module_dir(self, path):
        module_dir = Path(self.sdk_module_directory)
        return module_dir.joinpath(path)

    def get_module_path(self, path) -> Path:
        """
        Given a relative path, return an absolute path within the service module directory.
        """
        module_dir = Path(self.sdk_module_directory)
        return module_dir.joinpath(path)

    def read_module_file(self, file_path_string):
        """
        Reads a file from within the service module directory (repo)
        """
        module_file = self.get_module_path(file_path_string)
        if not module_file.is_file():
            error_exit(f'Could not find module file: {module_file.resolve()}')
        return module_file.read_text(encoding="utf-8")


    def copy_python_widget_support(self):
        source_dir = self.get_resource_dir('python-widget-support/widget')
        dest_dir = os.path.join(self.sdk_module_directory, 'lib', 'widget')
        shutil.copytree(source_dir, dest_dir)


    def copy_docs(self):
        source_dir = self.get_resource_dir('docs')
        dest_dir = os.path.join(self.sdk_module_directory, 'docs')
        shutil.copytree(source_dir, dest_dir)


    def copy_static_widget_support(self):
        source_dir = self.get_resource_dir('static-widget-support/widget')
        dest_dir = os.path.join(self.sdk_module_directory, 'widget')
        shutil.copytree(source_dir, dest_dir)


    def get_server_file_path(self):
        server_filename = f"{self.sdk_module_name}Server.py"
        server_file_path = os.path.join(self.sdk_module_directory, 'lib', self.sdk_module_name, server_filename)
        return server_file_path

    def read_server_file(self):
        server_file_path = self.get_server_file_path()
        if not os.path.isfile(server_file_path):
            error_exit(f'Could not find module server file: {server_file_path}')
        with open(server_file_path, "r", encoding="utf-8") as fin:
            return fin.read()

    def save_server_file(self, new_server_file_contents):
        server_file_path = self.get_server_file_path()

        self.backup_file(server_file_path)

        with open(server_file_path, "w", encoding="utf-8") as fout:
            fout.write(new_server_file_contents)

    # def get_service_file_path(self, relative_file_path):
    #     server_file_path = os.path.join(self.sdk_module_directory, 'lib', self.sdk_module_name, relative_file_path)
    #     return server_file_path

    # def get_service_file(self, relative_file_path):
    #     file_path = self.get_service_file_path(relative_file_path)
    #     if not os.path.isfile(file_path):
    #         error_exit(f'Could not find module file: {file_path}')
    #     with open(file_path, "r", encoding="utf-8") as fin:
    #         return fin.read()

    # def save_service_file(self, relative_file_path, new_file_contents):
    #     file_path = self.get_service_file_path(relative_file_path)

    #     self.backup_file(file_path)

    #     with open(file_path, "w", encoding="utf-8") as fout:
    #         fout.write(new_file_contents)


    def get_test_file_path(self, relative_file_path):
        server_file_path = os.path.join(self.sdk_module_directory, 'test', relative_file_path)
        return server_file_path


    def get_test_file(self, relative_file_path):
        file_path = self.get_test_file_path(relative_file_path)
        if not os.path.isfile(file_path):
            error_exit(f'Could not find module file: {file_path}')
        with open(file_path, "r", encoding="utf-8") as fin:
            return fin.read()


    def save_test_file(self, relative_file_path, new_file_contents):
        file_path = self.get_test_file_path(relative_file_path)

        self.backup_file(file_path)

        with open(file_path, "w", encoding="utf-8") as fout:
            fout.write(new_file_contents)


    def fix_auth_client(self):
        expected_import = f"{self.sdk_module_name}.authclient"
        correct_import = f"installed_clients.authclient"

        server_file_content = self.read_server_file()
        fixed_server_file_content = server_file_content.replace(expected_import, correct_import)
        self.save_server_file(fixed_server_file_content)
        
        test_file = f"{self.sdk_module_name}_server_test.py"
        file_content = self.get_test_file(test_file)
        fixed_file_content = file_content.replace(expected_import, correct_import)
        self.save_test_file(test_file, fixed_file_content) 


    def make_dynamic_service(self):
        """
        In which we add the flag to make the app module a dynamic service module :)
        """
        kbase_config = self.load_kbase_config()
        if self.get_attribute(kbase_config, 'service-config.dynamic-service'):
            success_feedback('Already a dynamic service, skipping')
            return

        kbase_config['service-config'] = {'dynamic-service': True}
        config_snippet = self.read_resource_file('snippets/dynamic-service-config.txt')
        config_content = self.read_module_file('kbase.yml')
        config_content += config_snippet
        self.save_module_file('kbase.yml', config_content)

    
    def save_module_file(self, relative_file_path, new_file_contents):
        file_path = self.get_module_path(relative_file_path)

        self.backup_file(file_path)

        with open(file_path, "w", encoding="utf-8") as fout:
            fout.write(new_file_contents)


    def fix_makefile(self):
        # load the makefile
        makefile_content = self.read_module_file('Makefile')

        section = None
        updated = False

        # look for :
        # 		--pyimplname $(SERVICE_CAPS).$(SERVICE_CAPS)Impl;
        new_makefile = []
        for line in makefile_content.split('\n'):
            section_match = re.match(r'^(.+):$', line)
            if section_match is not None:
                section = section_match.group(1)
                new_makefile.append(line)
                continue

            if section == 'compile' and len(line) == 0 and updated is False:
                # first empty line, time to place our new code.
                snippet = self.read_resource_file('snippets/makefile-compile.txt')
                new_makefile.append(snippet)
                updated = True
                new_makefile.append(line)
                continue

            new_makefile.append(line)

        self.save_module_file('Makefile', '\n'.join(new_makefile))

    
    def add_debugging_to_impl(self):
        impl_content_lines = self.read_impl_file().split('\n')
        snippet = self.read_resource_file('snippets/service-impl-status-debugging.txt')
        new_impl = []
        for line in impl_content_lines:
            if "'version': self.VERSION," in line:
                new_impl.append(snippet)
                new_impl.append(line)
            else:
                new_impl.append(line)

        self.write_impl_file('\n'.join(new_impl))


    def add_widget_support(self):
        self.assert_has_been_checked()

        # Updates the kbase.yml to ensure this is a dynamic service
        # Actually, we ask the user to do this by hand. That way, we can use this tool for
        # any DS module, and not just a fresh generic module.
        self.make_dynamic_service()
        success_feedback('Module configured as dynamic service')

        # Fixes incorrect import of the kbase auth client
        self.fix_auth_client()
        success_feedback('Auth client imports fixed')

        # Adds Python code snippets to the server file. j
        self.add_server_snippets()
        success_feedback('Server snippets added')

        # Fixes the generated test script, which has an invalid reliance 
        # upon SDK_CALLBACK_URL
        self.fix_test_file()
        success_feedback('Test file repaired')

        # Adds Python code snippets to the implementation file
        self.fix_impl_file()
        success_feedback('Impl snippets added')

        # Add some missing items from .gitignore
        self.add_gitignore_snippets()
        success_feedback('gitignore snippets added')

        # add docker compose
        self.copy_docker_compose()
        success_feedback('Docker compose copied')

        # add widget python support
        self.copy_python_widget_support()
        success_feedback('Python widget support copied')

        # add widget static support (javascript and resources)
        self.copy_static_widget_support()
        success_feedback('Static widget support copied')

        # add docs
        self.copy_docs()
        success_feedback('Widget docs copied')

        # Amend the Makefile to fix up the server script post-compile.
        self.fix_makefile()
        success_feedback('Fixed Makefile')

        # Update impl file (again), this time adding debugging support
        self.add_debugging_to_impl()
        success_feedback('Debugging suppport added to impl file')

        # add python widget examples

        # add javascrip widget examples

        # add direct widget examples
