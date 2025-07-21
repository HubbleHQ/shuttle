import requests

from unittest import TestCase
from unittest.mock import MagicMock, patch

from hubble_shuttle.http import RequestsShuttleTransport

class ShuttleAPITest(TestCase):

    def test_api_building(self):
        kwargs = {
            "headers": {},
            "query": {},
            "request_content_type": "application/json"
        }
        self.assertEqual(
            "http://host/path",
            RequestsShuttleTransport(api_endpoint = "http://host", **kwargs)._prepare_request_url("/path"),
            "Concatenates the path after the host name"
        )
        self.assertEqual(
            "http://host/path",
            RequestsShuttleTransport(api_endpoint = "http://host/", **kwargs)._prepare_request_url("/path"),
            "Doesn't duplicate slashes between host and path"
        )
        self.assertEqual(
            "http://host/api/path",
            RequestsShuttleTransport(api_endpoint = "http://host/api", **kwargs)._prepare_request_url("/path"),
            "Keeps any path on the api_endpoint as a path prefix"
        )
        self.assertEqual(
            "http://host/api/path",
            RequestsShuttleTransport(api_endpoint = "http://host/api/", **kwargs)._prepare_request_url("///path"),
            "Keeps any path on the api_endpoint as a path prefix"
        )
        self.assertEqual(
            "http://host:123/path",
            RequestsShuttleTransport(api_endpoint = "http://host:123", **kwargs)._prepare_request_url("/path"),
            "Preserves the port number"
        )
