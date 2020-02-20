import requests
from requests.exceptions import RequestException
from unittest import TestCase
from unittest.mock import MagicMock, patch

import hubble_shuttle
from hubble_shuttle import ShuttleAPI


class ShuttleAPITestClient(ShuttleAPI):
    api_endpoint = "http://myapi/"


class ShuttleAPITest(TestCase):

    @patch("requests.get")
    def test_get_request(self, mock_requests):
        response = MagicMock()
        response.json.return_value = {"returned": "data"}
        mock_requests.return_value = response

        response = ShuttleAPITestClient().http_get("/path")

        mock_requests.assert_called_with("http://myapi/path")
        self.assertEqual({"returned": "data"}, response.data, "Returns the parsed JSON data")

    @patch("requests.get")
    def test_get_request_with_class_headers(self, mock_requests):
        client = ShuttleAPITestClient()
        client.headers = {"foo": "bar"}
        client.http_get("/path")

        mock_requests.assert_called_with("http://myapi/path", headers={"foo": "bar"})

    @patch("requests.get")
    def test_get_request_with_request_headers(self, mock_requests):
        client = ShuttleAPITestClient()
        client.http_get("/path", headers={"foo": "bar"})

        mock_requests.assert_called_with("http://myapi/path", headers={"foo": "bar"})

    @patch("requests.get")
    def test_get_request_with_class_and_request_headers(self, mock_requests):
        client = ShuttleAPITestClient()
        client.headers = {"foo": "bar"}
        client.http_get("/path", headers={"bar": "baz"})

        mock_requests.assert_called_with("http://myapi/path", headers={"foo": "bar", "bar": "baz"})

    @patch("requests.get")
    def test_get_request_with_class_and_request_headers_conflict(self, mock_requests):
        client = ShuttleAPITestClient()
        client.headers = {"foo": "bar"}
        client.http_get("/path", headers={"foo": "baz"})

        mock_requests.assert_called_with("http://myapi/path", headers={"foo": "baz"})

    @patch("requests.get")
    def test_get_request_with_request_query_param(self, mock_requests):
        client = ShuttleAPITestClient()
        client.http_get("/path", query={"foo": "bar"})

        mock_requests.assert_called_with("http://myapi/path", params={"foo": "bar"})

    @patch("requests.get")
    def test_get_request_with_class_and_request_query_param(self, mock_requests):
        client = ShuttleAPITestClient()
        client.query = {"foo": "bar"}
        client.http_get("/path", query={"bar": "baz"})

        mock_requests.assert_called_with("http://myapi/path", params={"foo": "bar", "bar": "baz"})

    @patch("requests.get")
    def test_get_request_with_class_and_request_query_param_conflict(self, mock_requests):
        client = ShuttleAPITestClient()
        client.query = {"foo": "bar"}
        client.http_get("/path", query={"foo": "baz"})

        mock_requests.assert_called_with("http://myapi/path", params={"foo": "baz"})

    @patch("requests.get")
    def test_get_generic_networking_error(self, mock_requests):
        response = MagicMock()
        response_error = requests.exceptions.RequestException
        response.raise_for_status.side_effect = response_error

        mock_requests.return_value = response
        with self.assertRaises(hubble_shuttle.exceptions.APIError) as cm:
            ShuttleAPITestClient().http_get("/path")

    @patch("requests.get")
    def test_get_400_http_error(self, mock_requests):
        response = MagicMock()
        response.status_code = 400
        response.data = {"some_key": "some_value"}
        response_error = requests.exceptions.HTTPError(response=response)
        response.raise_for_status.side_effect = response_error

        mock_requests.return_value = response
        with self.assertRaises(hubble_shuttle.exceptions.BadRequestError) as cm:
            ShuttleAPITestClient().http_get("/path")

    @patch("requests.get")
    def test_get_404_http_error(self, mock_requests):
        response = MagicMock()
        response.status_code = 404
        response.data = {"some_key": "some_value"}
        response_error = requests.exceptions.HTTPError(response=response)
        response.raise_for_status.side_effect = response_error

        mock_requests.return_value = response
        with self.assertRaises(hubble_shuttle.exceptions.NotFoundError) as cm:
            ShuttleAPITestClient().http_get("/path")

    @patch("requests.get")
    def test_get_499_http_error(self, mock_requests):
        response = MagicMock()
        response.status_code = 499
        response.data = {"some_key": "some_value"}
        response_error = requests.exceptions.HTTPError(response=response)
        response.raise_for_status.side_effect = response_error

        mock_requests.return_value = response
        with self.assertRaises(hubble_shuttle.exceptions.HTTPClientError) as cm:
            ShuttleAPITestClient().http_get("/path")

    @patch("requests.get")
    def test_get_500_http_error(self, mock_requests):
        response = MagicMock()
        response.status_code = 500
        response.data = {"some_key": "some_value"}
        response_error = requests.exceptions.HTTPError(response=response)
        response.raise_for_status.side_effect = response_error

        mock_requests.return_value = response
        with self.assertRaises(hubble_shuttle.exceptions.InternalServerError) as cm:
            ShuttleAPITestClient().http_get("/path")

    @patch("requests.get")
    def test_get_599_http_error(self, mock_requests):
        response = MagicMock()
        response.status_code = 599
        response.data = {"some_key": "some_value"}
        response_error = requests.exceptions.HTTPError(response=response)
        response.raise_for_status.side_effect = response_error

        mock_requests.return_value = response
        with self.assertRaises(hubble_shuttle.exceptions.HTTPServerError) as cm:
            ShuttleAPITestClient().http_get("/path")

