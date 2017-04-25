# -*- coding: utf-8 -*-

import unittest
import mock


def mocked_requests_utf8_get(*args, **kwargs):
    class MockResponse:
        encoding = 'utf-8'
        status_code = 200
        content = b'\xe2\x80\x98sample.tgz\xe2\x80\x99'

    return MockResponse()


class TestCommonHelperFunctions(unittest.TestCase):
    """
    Tests helper functions in floyd.client.common
    """
    @mock.patch('requests.get', side_effect=mocked_requests_utf8_get)
    def test_get_url_contents(self, mocked_get):
        from floyd.client.common import get_url_contents
        self.assertEqual(get_url_contents('foobar.baz/api/v1/content'),
                         u'\u2018sample.tgz\u2019')
