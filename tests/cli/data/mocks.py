def mock_access_token():
    class AccessToken:
        username = 'foo_user'
        token = '123'

    return AccessToken()

def mock_data(data_id):
    class Data:
        id = data_id
        name = 'test/name/123'

    return Data()

def mock_project_client():
    class Project:
        id = '123'

    class MockClient:
        def get_by_name(*args):
            return Project()

    return MockClient()
