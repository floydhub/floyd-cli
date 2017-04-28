from __future__ import print_function
from time import sleep
import requests
import sys

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


def wait_for_url(url, status_code=200, sleep_duration_seconds=1, iterations=120, message_frequency=15):
    """
    Wait for the url to become available
    """
    for iteration in range(iterations):
        print(".", end='')
        sys.stdout.flush()
        response = requests.get(url)
        if response.status_code == status_code:
            print(".")
            return True
        sleep(sleep_duration_seconds)
    print(".")
    return False


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
