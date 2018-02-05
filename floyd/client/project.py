import sys
from floyd.manager.auth_config import AuthConfigManager
from floyd.exceptions import (
    FloydException, AuthenticationException, NotFoundException
)
from floyd.client.base import FloydHttpClient
from floyd.model.project import Project
from floyd.log import logger as floyd_logger
from floyd.cli.utils import get_namespace_from_name


class ProjectClient(FloydHttpClient):
    """
    Client to get projects from the server
    """
    def __init__(self):
        self.url = "/projects"
        super(ProjectClient, self).__init__()

    def get_projects(self):
        try:
            response = self.request("GET", self.url)
            projects_dict = response.json()
            return [Project.from_dict(project) for project in projects_dict.get("projects", [])]
        except FloydException as e:
            floyd_logger.info("Error while retrieving projects: {}".format(e.message))
            if isinstance(e, AuthenticationException):
                # exit now since there is nothing we can do without login
                sys.exit(1)
            return []

    def get_by_name(self, name, namespace=None):
        """
        name: can be either <namespace>/<project_name> or just <project_name>
        namespace: if specified, will skip name parsing, defaults to current user's username
        """
        if not namespace:
            namespace, name = get_namespace_from_name(name)
        if not namespace:
            namespace = AuthConfigManager.get_access_token().username
        try:
            response = self.request('GET', '%s/%s/%s' % (self.url, namespace, name))
            return Project.from_dict(response.json())
        except NotFoundException:
            return None

    def exists(self, name, namespace=None):
        try:
            response = self.request("GET", '{}/{}/{}'.format(self.url, namespace, name))
            if response.status_code == 200:
                return True
            else:
                return False
        except NotFoundException:
            return False
