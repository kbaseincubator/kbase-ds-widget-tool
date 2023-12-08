import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from string import Template

from utils import error_exit, feedback
from yaml import YAMLError, safe_load


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

    def ensure_valid_service(self):
        """
        Ensures that the given directory implements a KBase kb-sdk dynamic service
        """
        feedback('Analyzing module directory ...')

        # Determine if it is a directory
        if not os.path.isdir(self.sdk_module_directory):
            error_exit(f'The given directory "{self.sdk_module_directory}" does not exist')

        # See if it is probably a module directory.
        # We do that by looking for the "kbase.yml" file, with the proper structure.
        # Ideally we don't want it to be touched yet, but it is okay if it is.
        kbase_config_file = Path(os.path.join(self.sdk_module_directory, 'kbase.yml'))
        if not kbase_config_file.is_file():
            error_exit(f'The KBase module config file "kbase.yml" was not found in the module directory {self.sdk_module_directory}: {kbase_config_file.resolve()}')

        feedback('✅ "kbase.yml" config file found, it looks like a KBase kb-sdk service!')

        try:
            with open(kbase_config_file, "r", encoding="utf-8") as fin:
                kbase_config = safe_load(fin)
        except OSError as oserr:
            error_exit(f"Error opening or reading kbase config file: {str(oserr)}")
        except YAMLError as yerr:
            error_exit(f"Error parsing config file as YAML: {str(yerr)}")

        feedback('✅ "kbase.yml" successfully loaded')

        if self.ensure_attribute(kbase_config, "service-config.dynamic-service", "KBase Config") is not True:
            error_exit('The KBase kb-sdk service must already be configured as a dynamic service')

        module_name = self.ensure_attribute(kbase_config, "module-name", "KBase Config")

        feedback(f'✅ The service module "{module_name}" is indeed a dynamic service as well')

        print(f'Module name        : {module_name}')
        print(f'Module description : {self.ensure_attribute(kbase_config, "module-description", "KBase Config")}')
        print(f'Service language   : {self.ensure_attribute(kbase_config, "service-language", "KBase Config")}')
        print(f'Module version     : {self.ensure_attribute(kbase_config, "module-version", "KBase Config")}')
        print(f'Owners             : {", ".join(self.ensure_attribute(kbase_config, "owners", "KBase Config"))}')
        self.sdk_module_name = kbase_config['module-name']
        self.checked = True


    def assert_has_been_checked(self):
        if self.checked is not True:
            error_exit('Must ensure the target directory is a valid SDK Dynamic Service before processing it.')

    def get_resources_path(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(current_dir, '../resources')
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
        with open(os.path.join(resources_path, file_path), "r", encoding="utf-8") as fin:
            return fin.read()

    def add_server_snippets(self):
        """
        Adds snippets of python to add support for the /widgets endpoint within the service.
        """
        # Add the import snippet.
        import_snippet_template = self.get_resource_file('snippets/service-server-snippet-0.txt')
        import_snippet = Template(import_snippet_template).substitute({
            'service_module_name': self.sdk_module_name
        })

        # Add the path handling snippet.
        handler_snippet = self.get_resource_file('snippets/service-server-snippet-1.txt')

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
                print('------')
                print('IMPORT LINE')
                print(import_snippet)
                print('-------')
                server_file_replaced.append(import_snippet)
                server_file_replaced.append(line)
            elif line.startswith('    def __call__(self, environ, start_response):'):
                print('HANDLER LINE')
                server_file_replaced.append(line)
                server_file_replaced.append(handler_snippet)
            else:
                server_file_replaced.append(line)

        new_server_file_contents = '\n'.join(server_file_replaced)

        file_timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        server_file_backup_path = f"{server_file_path}.bak-{file_timestamp}"

        shutil.move(server_file_path, server_file_backup_path)

        with open(server_file_path, "w", encoding="utf-8") as fout:
            fout.write(new_server_file_contents)

        feedback('✅ Server snippets added')


    def sdk_python_placeholder(self, placeholder):
        return re.compile(f'[\\s]*#[\\s]*{placeholder}')


    def add_impl_snippets(self):
        """
        Adds snippets of python to add support for the /widgets endpoint within the service.
        """
        #
        # Add the import snippet to the impl file.
        #
        import_snippet_template = self.get_resource_file('snippets/service-impl-snippet-0.txt')
        import_snippet = Template(import_snippet_template).substitute({
            'service_module_name': self.sdk_module_name
        })

        # Add the path handling snippet.
        widgets_snippet = self.get_resource_file('snippets/service-impl-snippet-1.txt')

        impl_filename = f"{self.sdk_module_name}Impl.py"
        impl_file_path = Path(os.path.join(self.sdk_module_directory, 'lib', self.sdk_module_name, impl_filename))
        if not impl_file_path.is_file():
            error_exit(f'Could not find module impl file: {impl_file_path.resolve()}')

        impl_file_lines = impl_file_path.read_text(encoding='utf-8').split('\n')

        # Okay, place the import line at the end of the imports.
        # We determine this based on the presence of the global variable DEPLOY which
        # appears at the end of the imports.

        impl_file_replaced = []
        for line in impl_file_lines:
            if re.match(self.sdk_python_placeholder('END_HEADER'), line):
                impl_file_replaced.append(import_snippet)
                impl_file_replaced.append(line)
            elif re.match(self.sdk_python_placeholder('END_CONSTRUCTOR'), line):
                impl_file_replaced.append(widgets_snippet)
                impl_file_replaced.append(line)
            else:
                impl_file_replaced.append(line)

        new_impl_file_contents = '\n'.join(impl_file_replaced)

        file_timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        impl_file_backup_path = f"{impl_file_path.resolve()}.bak-{file_timestamp}"

        shutil.move(impl_file_path, impl_file_backup_path)

        impl_file_path.write_text(new_impl_file_contents, encoding="utf-8")

        feedback('✅ Impl snippets added')


    def add_gitignore_snippets(self):
        """
        Adds missing lines to gitignore
        """
        #
        # Add the gitignore snippet to the gitignore
        #

        gitignore_snippet = self.get_resource_file('snippets/gitignore.txt')

        gitignore_filename = ".gitignore"

        file_path = Path(os.path.join(self.sdk_module_directory, gitignore_filename))
        if not file_path.is_file():
            error_exit(f'Could not find gitignore file: {file_path.resolve()}')

        file_lines = file_path.read_text(encoding='utf-8').split('\n')

        file_lines.append(gitignore_snippet)

        file_timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        file_backup_path = f"{file_path.resolve()}.bak-{file_timestamp}"

        shutil.move(file_path, file_backup_path)

        new_file_contents = '\n'.join(file_lines)

        file_path.write_text(new_file_contents, encoding="utf-8")

        feedback('✅ gitignore snippets added')

    def copy_docker_compose(self):
        # Read docker compose file
        docker_compose_source = self.get_resource_file('docker/docker-compose.yml')

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


    def copy_python_widget_support(self):
        source_dir = self.get_resource_dir('python-widget-support/widget')
        dest_dir = os.path.join(self.sdk_module_directory, 'lib', self.sdk_module_name, 'widget')
        shutil.copytree(source_dir, dest_dir)
        feedback('✅ Python widget support copied')


    def copy_docs(self):
        source_dir = self.get_resource_dir('docs')
        dest_dir = os.path.join(self.sdk_module_directory, 'docs')
        shutil.copytree(source_dir, dest_dir)
        feedback('✅ Widget docs copied')


    def copy_static_widget_support(self):
        source_dir = self.get_resource_dir('static-widget-support/widget')
        dest_dir = os.path.join(self.sdk_module_directory, 'widget')
        feedback('Copying python support files')
        feedback(f'From {source_dir}')
        feedback(f'To {dest_dir}')
        shutil.copytree(source_dir, dest_dir)
        feedback('✅ Static widget support copied')


    def get_server_file_path(self):
        server_filename = f"{self.sdk_module_name}Server.py"
        server_file_path = os.path.join(self.sdk_module_directory, 'lib', self.sdk_module_name, server_filename)
        return server_file_path

    def get_server_file(self):
        server_file_path = self.get_server_file_path()
        if not os.path.isfile(server_file_path):
            error_exit(f'Could not find module server file: {server_file_path}')
        with open(server_file_path, "r", encoding="utf-8") as fin:
            return fin.read()

    def save_server_file(self, new_server_file_contents):
        server_file_path = self.get_server_file_path()
        file_timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        server_file_backup_path = f"{server_file_path}.bak-{file_timestamp}"

        shutil.move(server_file_path, server_file_backup_path)

        with open(server_file_path, "w", encoding="utf-8") as fout:
            fout.write(new_server_file_contents)

    def get_service_file_path(self, relative_file_path):
        server_file_path = os.path.join(self.sdk_module_directory, 'lib', self.sdk_module_name, relative_file_path)
        return server_file_path

    def get_service_file(self, relative_file_path):
        file_path = self.get_service_file_path(relative_file_path)
        if not os.path.isfile(file_path):
            error_exit(f'Could not find module file: {file_path}')
        with open(file_path, "r", encoding="utf-8") as fin:
            return fin.read()

    def save_service_file(self, relative_file_path, new_file_contents):
        file_path = self.get_service_file_path(relative_file_path)
        file_timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        file_backup_path = f"{file_path}.bak-{file_timestamp}"

        shutil.move(file_path, file_backup_path)

        with open(file_path, "w", encoding="utf-8") as fout:
            fout.write(new_file_contents)


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
        file_timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        file_backup_path = f"{file_path}.bak-{file_timestamp}"

        shutil.move(file_path, file_backup_path)

        with open(file_path, "w", encoding="utf-8") as fout:
            fout.write(new_file_contents)


    def fix_auth_client(self):
        expected_import = f"{self.sdk_module_name}.authclient"
        correct_import = f"installed_clients.authclient"

        server_file_content = self.get_server_file()
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

        config_snippet = self.get_resource_file('snippets/dynamic-service-config.txt')
        config_content = self.get_service_file('kbase.yml')
        config_content += config_snippet
        self.save_service_file('kbase.yml', config_content)


    def add_widget_support(self):
        self.assert_has_been_checked()

        # Updates the kbase.yml to ensure this is a dynamic service
        # Actually, we ask the user to do this by hand. That way, we can use this tool for
        # any DS module, and not just a fresh generic module.

        # Fixes incorrect import of the kbase auth client
        self.fix_auth_client()

        # Adds Python code snippets to the server file
        self.add_server_snippets()

        # Adds Python code snippets to the implementation file
        self.add_impl_snippets()

        # Add some missing items from .gitignore
        self.add_gitignore_snippets()

        # add docker compose
        self.copy_docker_compose()

        # add widget python support
        self.copy_python_widget_support()

        # add widget static support (javascript and resources)
        self.copy_static_widget_support()

        # add docs
        self.copy_docs()

        # add python widget examples

        # add javascrip widget examples

        # add direct widget examples
