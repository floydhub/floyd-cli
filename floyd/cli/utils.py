import pkg_resources

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


def normalize_data_name(data_name):
    if data_name.endswith('/output'):
        name_parts = data_name.split('/')
        if len(name_parts) <= 4:
            name_parts.insert(1, 'projects')
            data_name = '/'.join(name_parts)
        return data_name
    else:
        name_parts = data_name.split('/')
        if len(name_parts) <= 3:
            name_parts.insert(1, 'datasets')
            data_name = '/'.join(name_parts)
        return data_name


def normalize_job_name(job_name):
    job_name_parts = job_name.split('/')
    if len(job_name_parts) <= 3:
        job_name_parts.insert(1, 'projects')
        job_name = '/'.join(job_name_parts)
    return job_name


def get_cli_version():
    return pkg_resources.require("floyd-cli")[0].version
