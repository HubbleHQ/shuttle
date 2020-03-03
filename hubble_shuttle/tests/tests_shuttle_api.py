import requests
from requests.exceptions import RequestException
from unittest import TestCase
from unittest.mock import MagicMock, patch

import hubble_shuttle
from hubble_shuttle import ShuttleAPI


class ShuttleAPITestClient(ShuttleAPI):
    api_endpoint = "http://test_http_server/"


class ShuttleAPITest(TestCase):

    def test_get_request(self):
        response = ShuttleAPITestClient().http_get("/get")
        self.assertEqual('http://test_http_server/get', response.data['url'], "Parses the JSON response")
        self.assertEqual({}, response.data['args'], "Doesn't include any query params")

    def test_get_request_parse_response_text(self):
        response = ShuttleAPITestClient().http_get("/robots.txt")
        self.assertEqual("User-agent: *\nDisallow: /deny\n", response.data, "Returns the text response as a string")

    def test_get_request_parse_response_json(self):
        response = ShuttleAPITestClient().http_get("/json")
        self.assertEqual({'slideshow': {'author': 'Yours Truly',
                'date': 'date of publication',
                'slides': [{'title': 'Wake up to WonderWidgets!', 'type': 'all'},
                           {'items': ['Why <em>WonderWidgets</em> are great',
                                      'Who <em>buys</em> WonderWidgets'],
                            'title': 'Overview',
                            'type': 'all'}],
                'title': 'Sample Slide Show'}}, response.data, "Returns the JSON response as parsed object")

    def test_get_request_parse_response_default(self):
        response = ShuttleAPITestClient().http_get("/base64/SGVsbG8=")
        self.assertEqual(b"Hello", response.data, "Returns the response as a binary string")

    def test_get_request_with_class_headers(self):
        client = ShuttleAPITestClient()
        client.headers = {"Foo": "Bar"}
        response = client.http_get("/get")
        self.assertEqual("Bar", response.data['headers']['Foo'], "Sends the client-level headers")

    def test_get_request_with_request_headers(self):
        client = ShuttleAPITestClient()
        response = client.http_get("/get", headers={"Foo": "Bar"})
        self.assertEqual("Bar", response.data['headers']['Foo'], "Sends the request-level headers")

    def test_get_request_with_class_and_request_headers(self):
        client = ShuttleAPITestClient()
        client.headers = {"Foo": "Bar"}
        response = client.http_get("/get", headers={"Bar": "Baz"})
        self.assertEqual("Bar", response.data['headers']['Foo'], "Sends the client-level headers")
        self.assertEqual("Baz", response.data['headers']['Bar'], "Sends the request-level headers")

    def test_get_request_with_class_and_request_headers_conflict(self):
        client = ShuttleAPITestClient()
        client.headers = {"Foo": "Bar"}
        response = client.http_get("/get", headers={"Foo": "Baz"})
        self.assertEqual("Baz", response.data['headers']['Foo'], "Sends the request-level headers")

    def test_get_request_with_class_query_param(self):
        client = ShuttleAPITestClient()
        client.query = {"foo": "bar"}
        response = client.http_get("/get")
        self.assertEqual("bar", response.data['args']['foo'], "Sends the client-level parameters")

    def test_get_request_with_request_query_param(self):
        client = ShuttleAPITestClient()
        response = client.http_get("/get", query={"foo": "bar"})
        self.assertEqual("bar", response.data['args']['foo'], "Sends the request-level parameters")

    def test_get_request_with_class_and_request_query_param(self):
        client = ShuttleAPITestClient()
        client.query = {"foo": "bar"}
        response = client.http_get("/get", query={"bar": "baz"})
        self.assertEqual("bar", response.data['args']['foo'], "Sends the client-level parameters")
        self.assertEqual("baz", response.data['args']['bar'], "Sends the request-level parameters")

    def test_get_request_with_class_and_request_query_param_conflict(self):
        client = ShuttleAPITestClient()
        client.query = {"foo": "bar"}
        response = client.http_get("/get", query={"foo": "baz"})
        self.assertEqual("baz", response.data['args']['foo'], "Sends the request-level parameters")

    def test_get_generic_networking_error(self):
        client = ShuttleAPITestClient()
        client.api_endpoint = 'http://non_existing_http_server'
        with self.assertRaises(hubble_shuttle.exceptions.APIError) as cm:
            client.http_get("/get")

    def test_get_400_http_error(self):
        with self.assertRaises(hubble_shuttle.exceptions.BadRequestError) as cm:
            ShuttleAPITestClient().http_get("/status/400")

    def test_get_404_http_error(self):
        with self.assertRaises(hubble_shuttle.exceptions.NotFoundError) as cm:
            ShuttleAPITestClient().http_get("/status/404")

    def test_get_499_http_error(self):
        with self.assertRaises(hubble_shuttle.exceptions.HTTPClientError) as cm:
            ShuttleAPITestClient().http_get("/status/499")

    def test_get_500_http_error(self):
        with self.assertRaises(hubble_shuttle.exceptions.InternalServerError) as cm:
            ShuttleAPITestClient().http_get("/status/500")

    def test_get_599_http_error(self):
        with self.assertRaises(hubble_shuttle.exceptions.HTTPServerError) as cm:
            ShuttleAPITestClient().http_get("/status/599")

