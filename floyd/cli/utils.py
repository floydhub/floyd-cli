import pkg_resources

from floyd.exceptions import FloydException
from floyd.manager.auth_config import AuthConfigManager
from floyd.manager.experiment_config import ExperimentConfigManager


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


def get_mode_parameter(mode):
    """
    Map the mode parameter to the server parameter
    """
    if mode == 'job':
        return 'cli'
    elif mode == 'serve':
        return 'serving'
    else:
        return mode


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


def normalize_data_name(raw_name, default_username=None, default_dataset_name=None):
    if raw_name.endswith('/output'):
        return normalize_job_name(raw_name[:-len('/output')], default_username, default_dataset_name) + '/output'

    name_parts = raw_name.split('/')

    username = default_username or current_username()
    name = default_dataset_name or current_experiment_name()
    number = None # current job number

    # When nothing is passed, use all the defaults
    if not raw_name:
        pass
    elif len(name_parts) == 4:
        # mckay/datasets/foo/1
        username, _, name, number = name_parts
    elif len(name_parts) == 3:

        if name_parts[2].isdigit():
            # mckay/foo/1
            username, name, number = name_parts
        else:
            # mckay/projects/foo
            username, _, name = name_parts
    elif len(name_parts) == 2:
        if name_parts[1].isdigit():
            # foo/1
            name, number = name_parts
        else:
            # mckay/foo
            username, name = name_parts
    elif len(name_parts) == 1:
        if name_parts[0].isdigit():
            # 1
            job_number = name_parts[0]
        else:
            # foo
            name = name_parts[0]
    else:
        return raw_name

    # If no number/version is found, query the API for the most recent version
    if number is None:
        name_from_api = get_dataset_number(username, name)
        if not name_from_api:
            raise FloydException("Could not resolve %s. Make sure the project exists and has jobs." % raw_name)
        return name_from_api

    return '/'.join([username, 'datasets', name, number])


def normalize_job_name(raw_job_name, default_username=None, default_project_name=None):
    name_parts = raw_job_name.split('/')

    username = default_username or current_username()
    project_name = default_project_name or current_experiment_name()
    job_number = None # current job number

    # When nothing is passed, use all the defaults
    if not raw_job_name:
        pass
    elif len(name_parts) == 4:
        # mckay/projects/foo/1
        username, _, project_name, job_number = name_parts
    elif len(name_parts) == 3:

        if name_parts[2].isdigit():
            # mckay/foo/1
            username, project_name, job_number = name_parts
        else:
            # mckay/projects/foo
            username, _, project_name = name_parts
    elif len(name_parts) == 2:
        if name_parts[1].isdigit():
            # foo/1
            project_name, job_number = name_parts
        else:
            # mckay/foo
            username, project_name = name_parts
    elif len(name_parts) == 1:
        if name_parts[0].isdigit():
            # 1
            job_number = name_parts[0]
        else:
            # foo

            project_name = name_parts[0]
    else:
        return raw_job_name

    # If no job_number is found, query the API for the most recent job number
    if job_number is None:
        job_name_from_api = get_last_job_name(username, project_name)
        if not job_name_from_api:
            raise FloydException("Could not resolve %s. Make sure the project exists and has jobs." % raw_job_name)
        return job_name_from_api

    return '/'.join([username, 'projects', project_name, job_number])


def get_cli_version():
    return pkg_resources.require("floyd-cli")[0].version

def current_username():
    access_token = AuthConfigManager.get_access_token()
    return access_token.username

def current_experiment_name():
    experiment_config = ExperimentConfigManager.get_config()
    return experiment_config.name

def get_last_job_name(username, project_name):
    from floyd.client.project import ProjectClient
    project = ProjectClient().get_by_name(project_name, username)

    if not project:
        return ''

    return project.latest_experiment_name

# TODO: totalVersionsCount will not always get us the correct version number,
# but it will be correct a lot of the time. The API will offer this information
# in the future.
def get_dataset_number(username, dataset_name):
    from floyd.client.dataset import DatasetClient

    dataset = DatasetClient().get_by_name(dataset_name, username=username)

    if not dataset:
        return ''

    return '%s/datasets/%s/%s' % (username, dataset_name, dataset.totalVersionsCount)
