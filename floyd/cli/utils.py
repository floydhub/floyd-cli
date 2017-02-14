import floyd
from floyd.constants import DOCKER_IMAGES


def get_task_url(id):
    """
    Return the url to proxy to a running task
    """
    return "{}/{}".format(floyd.floyd_proxy_host, id)


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
