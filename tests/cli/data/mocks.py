def mock_data(data_id):
    class Data:
        id = data_id
        name = 'test name'
    return Data()
