import pkg_resources
import sys
import os

from floyd.exceptions import FloydException
from floyd.manager.auth_config import AuthConfigManager
from floyd.manager.experiment_config import ExperimentConfigManager
from floyd.manager.data_config import DataConfigManager

from floyd.constants import DOCKER_IMAGES


def get_docker_image(env, gpu):
    gpu_cpu = "gpu" if gpu else "cpu"
    return DOCKER_IMAGES.get(gpu_cpu).get(env)


def get_module_task_instance_id(task_instances):
    """
    Return the first task instance that is a module node.
    """
    for id in task_instances:
        if task_instances[id] == 'module_node':
            return id
    return None


def get_data_name(data_str, default=None):
    """
    If data_str is of the format <ID>:<NAME>, return <NAME>
    Else return default if default is present
    Otherwise return ID itself
    """
    if ':' in data_str:
        _, name = data_str.split(':')
    else:
        name = default if default else data_str
    return name


def get_data_id(data_str):
    """
    If data_str is of the format <ID>:<NAME>, or <URI>/<PATH>:<NAME>
    return ID or URI
    """
    if ':' in data_str:
        name_or_id, _ = data_str.split(':')
        return name_or_id
    else:
        return data_str


def normalize_data_name(raw_name, default_username='', default_dataset_name='', use_data_config=True):
    raw_name = raw_name or ''
    if raw_name.endswith('/output'):
        return normalize_job_name(raw_job_name=raw_name[:-len('/output')],
                                  default_username=default_username,
                                  default_project_name=default_dataset_name,
                                  use_config=False) + '/output'
    elif raw_name.endswith('/home'):
        return normalize_job_name(raw_job_name=raw_name[:-len('/home')],
                                  default_username=default_username,
                                  default_project_name=default_dataset_name,
                                  use_config=False) + '/home'
    elif '/projects/' in raw_name:
        return normalize_job_name(raw_job_name=raw_name,
                                  default_username=default_username,
                                  default_project_name=default_dataset_name,
                                  use_config=False)

    name_parts = raw_name.split('/')

    namespace = default_username
    if use_data_config:
        default_dataset_name = default_dataset_name or current_dataset_name()
        namespace = namespace or current_dataset_namespace()

    name = default_dataset_name
    number = None  # current version number

    # When nothing is passed, use all the defaults
    if not raw_name:
        pass
    elif len(name_parts) == 4:
        # mckay/datasets/foo/1
        namespace, _, name, number = name_parts
    elif len(name_parts) == 3:
        if name_parts[2].isdigit():
            # mckay/foo/1
            namespace, name, number = name_parts
        else:
            # mckay/projects/foo
            namespace, _, name = name_parts
    elif len(name_parts) == 2:
        if name_parts[1].isdigit():
            # foo/1
            name, number = name_parts
        else:
            # mckay/foo
            namespace, name = name_parts
    elif len(name_parts) == 1:
        if name_parts[0].isdigit():
            # 1
            number = name_parts[0]
        else:
            # foo
            name = name_parts[0]
    else:
        return raw_name

    name_parts = [namespace, 'datasets', name]

    if number is not None:
        name_parts.append(number)

    if not name:
        raise FloydException('Dataset name resolution: Could not infer a name from "%s". Please include a name to identify the dataset' % raw_name)

    return '/'.join(name_parts)


def normalize_job_name(raw_job_name, default_username='', default_project_name='', use_config=True):
    raw_job_name = raw_job_name or ''

    if use_config:
        default_project_name = default_project_name or current_project_name()

    name_parts = raw_job_name.split('/')

    namespace = default_username or current_project_namespace()
    project_name = default_project_name
    number = ''  # current job number

    # When nothing is passed, use all the defaults
    if not raw_job_name:
        pass
    elif len(name_parts) == 4:
        # mckay/projects/foo/1
        namespace, _, project_name, number = name_parts
    elif len(name_parts) == 3:

        if name_parts[2].isdigit():
            # mckay/foo/1
            namespace, project_name, number = name_parts
        else:
            # mckay/projects/foo
            namespace, _, project_name = name_parts
    elif len(name_parts) == 2:
        if name_parts[1].isdigit():
            # foo/1
            project_name, number = name_parts
        else:
            # mckay/foo
            namespace, project_name = name_parts
    elif len(name_parts) == 1:
        if name_parts[0].isdigit():
            # 1
            number = name_parts[0]
        else:
            # foo

            project_name = name_parts[0]
    else:
        return raw_job_name

    # If no number is found, query the API for the most recent job number
    if not number:
        job_name_from_api = get_latest_job_name_for_project(namespace, project_name)
        if not job_name_from_api:
            raise FloydException("Could not resolve %s. Make sure the project exists and has jobs." % raw_job_name)
        return job_name_from_api

    if not project_name:
        raise FloydException('Job name resolution: Could not infer a project name from "%s". Please include a name to identify the project' % raw_job_name)

    return '/'.join([namespace, 'projects', project_name, number])


def get_cli_version():
    return pkg_resources.require("floyd-cli")[0].version


def current_username():
    return AuthConfigManager.get_access_token().username


def current_project_name():
    return ExperimentConfigManager.get_config().name


def current_project_namespace():
    return ExperimentConfigManager.get_config().namespace or current_username()


def current_dataset_name():
    return DataConfigManager.get_config().name


def current_dataset_namespace():
    return DataConfigManager.get_config().namespace or current_username()


def get_latest_job_name_for_project(username, project_name):
    from floyd.client.project import ProjectClient
    project = ProjectClient().get_by_name(project_name, username)

    if not project:
        return ''

    return project.latest_experiment_name


def is_conda_env():
    return 'conda' in sys.version or 'ontinuum' in sys.version


def get_namespace_from_name(name):
    """
    can be either
    <namespace>/projects/<project_name>
    or
    <namespace>/<project_name>
    """
    name_parts = name.split("/", 2)
    if len(name_parts) > 1:
        return name_parts[0], name_parts[-1]
    else:
        return current_username(), name


yaml_config_names = ['floyd.yml', 'floyd.yaml']


def read_yaml_config():
    config = None
    for filename in yaml_config_names:
        if not os.path.exists(filename):
            continue
        with open(filename) as fd:
            config = fd.read()
    return config
