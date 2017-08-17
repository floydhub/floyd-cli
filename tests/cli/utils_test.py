import unittest


class TestCliUtil(unittest.TestCase):
    """
    Tests cli utils helper functions
    """
    def test_normalize_data_name(self):
        from floyd.cli.utils import normalize_data_name
        assert normalize_data_name('foo/bar/1') == 'foo/datasets/bar/1'
        assert normalize_data_name('foo/datasets/bar/1') == 'foo/datasets/bar/1'
        assert normalize_data_name('foo/bar/1/output') == 'foo/projects/bar/1/output'
        assert normalize_data_name('foo/projects/bar/1/output') == 'foo/projects/bar/1/output'

    def test_normalize_job_name(self):
        from floyd.cli.utils import normalize_job_name
        assert normalize_job_name('foo/bar/1') == 'foo/projects/bar/1'
        assert normalize_job_name('foo/projects/bar/1') == 'foo/projects/bar/1'
