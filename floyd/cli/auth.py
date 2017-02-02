import click
import webbrowser

import floyd
from floyd.client.auth import AuthClient
from floyd.manager.auth_config import AuthConfigManager
from floyd.model.access_token import AccessToken
from floyd.log import logger as floyd_logger


@click.command()
def login():
    """
    Log into Floyd via Auth0.
    """
    cli_info_url = "{}/cli".format(floyd.floyd_web_host)
    if not click.confirm('Access token page will now open in your browser. Continue?'):
        return

    webbrowser.open(cli_info_url)
    access_code = click.prompt('Please paste the code here', type=str)

    user = AuthClient().get_user(access_code)
    access_token = AccessToken(username=user.username,
                               token=access_code)
    AuthConfigManager.set_access_token(access_token)
    floyd_logger.info("Login Successful")

    # verifier = base64.urlsafe_b64encode(os.urandom(32))
    # verifier_challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier).digest())
    # verifier = "abc"
    # verifier_challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier).digest())
    #
    # redirect_uri = "http://localhost:3000"
    #
    # login_url = "{}/authorize?response_type=code&scope=openid%20profile&client_id={}&redirect_uri={}&code_challenge={}&code_challenge_method=S256&connection=Username-Password-Authentication".format(AUTH0_URL, AUTH0_CLIENT_ID, redirect_uri, verifier_challenge)
    # webbrowser.open(login_url)
    #
    # code = click.prompt('Please enter the code', type=str)
    # access_token_url = "{}/oauth/token".format(AUTH0_URL)
    # request_data = {"code": code,
    #                 "code_verifier": verifier,
    #                 "client_id": AUTH0_CLIENT_ID,
    #                 "grant_type": "authorization_code",
    #                 "redirect_uri": redirect_uri}
    #
    # response = requests.post(access_token_url, data=request_data)
    # print(response.json())
    # credentials = Credentials(username, password)
    # access_token = AuthClient().login(credentials)


@click.command()
def logout():
    """
    Logout of Floyd.
    """
    AuthConfigManager.purge_access_token()
