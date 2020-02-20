import requests
from requests.exceptions import RequestException
from requests.exceptions import HTTPError as RequestsHTTPError
from urllib.parse import urljoin

from .exceptions import *

class ShuttleAPI:

    headers = {}
    query = {}

    def http_get(self, url, **kwargs):
        try:
            request_url = urljoin(
                self.api_endpoint,
                url,
            )

            request_args = {}

            request_headers = self.prepare_request_headers(kwargs.get("headers", {}))
            if request_headers:
                request_args.update({"headers": request_headers})

            request_query = self.prepare_request_query(kwargs.get("query", {}))
            if request_query:
                request_args.update({"params": request_query})

            response = requests.get(
                request_url,
                **request_args,
            )

            self.raise_for_status(url, response)

            return self.parse_response(response)
        except RequestException as error:
            raise APIError(type(self).__name__, url, error)

    def prepare_request_headers(self, headers):
        request_headers = {}
        if self.headers:
            request_headers.update(self.headers)
        if headers:
            request_headers.update(headers)
        return request_headers

    def prepare_request_query(self, query):
        request_query = {}
        if self.query:
            request_query.update(self.query)
        if query:
            request_query.update(query)
        return request_query

    def raise_for_status(self, url, response):
        try:
            response.raise_for_status()
        except RequestsHTTPError as error:
            error_class = self.map_http_error_class(error)
            raise error_class(type(self).__name__, url, error)

    def map_http_error_class(self, error):
        if error.response.status_code in HTTP_STATUS_CODE_ERRORS:
            return HTTP_STATUS_CODE_ERRORS[error.response.status_code]

        for status_range in HTTP_STATUS_CODE_CLASS_ERRORS:
            if error.response.status_code in status_range:
                return HTTP_STATUS_CODE_CLASS_ERRORS[status_range]

        return HTTPError

    def parse_response(self, response):
        # TODO: We shouldn't assume JSON and sniff the content type
        data = response.json()

        return ShuttleResponse(data)

class ShuttleResponse:

    def __init__(self, data):
        self.data = data

