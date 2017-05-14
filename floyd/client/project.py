from floyd.client.base import FloydHttpClient
from floyd.exceptions import FloydException
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
            return []

    def get_project_matching_name(self, name):
        projects = self.get_projects()
        for project in projects:
            if name == project.name:
                return project
        return None
