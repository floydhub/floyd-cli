def mock_exp(exp_id):
    class Experiment:
        id = exp_id
        state = 'success'
        name = 'test_name'
        task_instances = []
    return Experiment()


def mock_running_exp(exp_id):
    class Experiment:
        id = exp_id
        state = 'running'
        name = 'running experiment'
        task_instances = []
    return Experiment()


def mock_queued_exp(exp_id):
    class Experiment:
        id = exp_id
        state = 'queued'
        name = 'queued experiment'
        task_instances = []
    return Experiment()
