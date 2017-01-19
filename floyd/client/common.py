import requests

from floyd.exceptions import FloydException


def get_url_contents(url):
    """
    Downloads the content of the url and returns it
    """
    response = requests.get(url)
    if response.status_code == 200:
        return response.content.decode()
    else:
        raise FloydException("Failed to get contents of the url : {}".format(url))
