import sys
from floyd.manager.auth_config import AuthConfigManager
from floyd.exceptions import (
    FloydException, AuthenticationException, NotFoundException
)
from floyd.client.base import FloydHttpClient
from floyd.model.project import Project
from floyd.log import logger as floyd_logger


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

    def get_by_name(self, name):
        access_token = AuthConfigManager.get_access_token()
        try:
            response = self.request('GET', '%s/%s/%s' % (self.url, access_token.username, name))
            return Project.from_dict(response.json())
        except NotFoundException:
            return None

    def exists(self, project_id):
        try:
            response = self.request("GET", '%s/id/%s' % (self.url, project_id))
            if response.status_code == 200:
                return True
            else:
                return False
        except NotFoundException:
            return False
