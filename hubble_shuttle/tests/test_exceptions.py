import requests
from requests.exceptions import RequestException
from unittest import TestCase
from unittest.mock import MagicMock

from hubble_shuttle.http import ShuttleResponse
from hubble_shuttle.exceptions import APIError, HTTPError

MOCK_SERVICE_NAME = "a-service-name"
MOCK_SOURCE = "some_function_name"

class ShuttleAPIExceptionsTest(TestCase):
    def test_create_from_request_exception(self):
        request_error = RequestException()
        api_error = APIError(MOCK_SERVICE_NAME, MOCK_SOURCE, request_error)

        self.assertEqual(
            api_error.original_error, request_error, "Sets original_error correctly"
        )
        self.assertEqual(
            api_error.service_name, MOCK_SERVICE_NAME, "Sets service_name correctly"
        )
        self.assertEqual(api_error.source, MOCK_SOURCE, "Sets source correctly")

    def test_create_from_http_error(self):
        error_response = MagicMock()
        response = ShuttleResponse({"some_key": "some_value"}, 410, {})

        http_error = requests.exceptions.HTTPError(response=error_response)

        api_error = HTTPError(MOCK_SERVICE_NAME, MOCK_SOURCE, http_error, response)

        self.assertEqual(
            api_error.internal_status_code, 410, "Sets status code correctly",
        )
        self.assertEqual(
            api_error.response,
            {"some_key": "some_value"},
            "Sets the response correctly",
        )

