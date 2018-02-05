from floyd.model.experiment_config import ExperimentConfig


def mock_exp(exp_id):
    class Experiment:
        id = exp_id
        state = 'success'
        name = 'test_name'
        task_instances = []
    return Experiment()


def mock_exp(exp_id):
    class Experiment:
        id = exp_id
        state = 'success'
        name = 'test_name'
        task_instances = []
    return Experiment()


def mock_task_inst(exp_id):
    class TaskInstance:
        module_id = '999999'
    return TaskInstance()


def mock_experiment_config():
    return ExperimentConfig(name="name", family_id="family_id")


def mock_data_config():
    class DataConfig:
        name = 'my_dataset'
        namespace = None
    return DataConfig()


def mock_access_token():
    class AccessToken:
        username = 'username'
        token = 'token'
    return AccessToken()
