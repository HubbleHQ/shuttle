import re
import requests
from requests.exceptions import RequestException
from requests.exceptions import HTTPError as RequestsHTTPError
from urllib.parse import urljoin

from .exceptions import *

class RequestsShuttleTransport:

    def __init__(self, **kwargs):
        self.api_endpoint = kwargs["api_endpoint"]
        if not self.api_endpoint.endswith('/'):
            self.api_endpoint += '/'


        self.headers = kwargs["headers"]
        self.query = kwargs["query"]
        self.request_content_type = kwargs["request_content_type"]

        if "service_name" in kwargs:
            self.service_name = kwargs["service_name"]
        else:
            self.service_name = type(self).__name__

    def get(self, url, **kwargs):
        return self._http_request("get", url, **kwargs)

    def post(self, url, **kwargs):
        return self._http_request("post", url, **kwargs)

    def put(self, url, **kwargs):
        return self._http_request("put", url, **kwargs)

    def patch(self, url, **kwargs):
        return self._http_request("patch", url, **kwargs)

    def delete(self, url, **kwargs):
        return self._http_request("delete", url, **kwargs)

    def _http_request(self, method, url, **kwargs):
        try:
            response = requests.request(
                method,
                self._prepare_request_url(url),
                **self._prepare_request_args(**kwargs),
            )

            self._raise_for_status(url, response)

            return self._parse_response(response)
        except RequestException as error:
            raise APIError(self.service_name, url, error)

    def _prepare_request_url(self, url):
        while url.startswith('/'):
            url = url[1:]

        return urljoin(
            self.api_endpoint,
            url
        )

    def _prepare_request_args(self, **kwargs):
        request_args = {}

        request_headers = self._prepare_request_headers(kwargs.get("headers", {}))
        if request_headers:
            request_args.update({"headers": request_headers})

        request_query = self._prepare_request_query(kwargs.get("query", {}))
        if request_query:
            request_args.update({"params": request_query})

        if "data" in kwargs:
            content_type = kwargs.get("content_type", self.request_content_type)
            if content_type == "application/x-www-form-urlencoded":
                request_args.update({"data": kwargs["data"]})
            elif content_type == "application/json":
                request_args.update({"json": kwargs["data"]})
            else:
                raise ValueError("Unknown content type for request: {}".format(content_type))

        return request_args

    def _prepare_request_headers(self, headers):
        request_headers = {}
        if self.headers:
            request_headers.update(self.headers)
        if headers:
            request_headers.update(headers)
        return request_headers

    def _prepare_request_query(self, query):
        request_query = {}
        if self.query:
            request_query.update(self.query)
        if query:
            request_query.update(query)
        return request_query

    def _raise_for_status(self, url, response):
        try:
            response.raise_for_status()
        except RequestsHTTPError as error:
            error_class = self._map_http_error_class(error)
            raise error_class(self.service_name, url, error, self._parse_response(response))

    def _map_http_error_class(self, error):
        if error.response.status_code in HTTP_STATUS_CODE_ERRORS:
            return HTTP_STATUS_CODE_ERRORS[error.response.status_code]

        for status_range in HTTP_STATUS_CODE_CLASS_ERRORS:
            if error.response.status_code in status_range:
                return HTTP_STATUS_CODE_CLASS_ERRORS[status_range]

        return HTTPError

    def _parse_response(self, response):
        content_type = response.headers.get('Content-Type', '')
        if re.match(r"^application/json( ?;.+)?$", content_type):
            data = response.json()
        elif re.match(r"^text/plain( ?;.+)?$", content_type):
            data = response.text
        else:
            data = response.content

        return ShuttleResponse(data, response.status_code)

class ShuttleResponse:

    def __init__(self, data, status_code):
        self.data = data
        self.status_code = status_code

