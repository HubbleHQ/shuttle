
from .http import RequestsShuttleTransport

class ShuttleAPI:

    transport = RequestsShuttleTransport

    api_endpoint = None
    headers = {}
    query = {}
    request_content_type = "application/x-www-form-urlencoded"

    def __init__(self, **kwargs):
        if "api_endpoint" in kwargs:
            self.api_endpoint = kwargs["api_endpoint"]
        if "headers" in kwargs:
            self.headers = kwargs["headers"]
        if "query" in kwargs:
            self.query = kwargs["query"]
        if "request_content_type" in kwargs:
            self.request_content_type = kwargs["request_content_type"]

        self.http = self.transport(
            api_endpoint = self.api_endpoint,
            headers = self.headers,
            query = self.query,
            request_content_type = self.request_content_type,
            service_name = type(self).__name__,
        )

    def http_get(self, url, **kwargs):
        return self.http.get(url, **kwargs)

    def http_post(self, url, **kwargs):
        return self.http.post(url, **kwargs)

    def http_put(self, url, **kwargs):
        return self.http.put(url, **kwargs)

    def http_patch(self, url, **kwargs):
        return self.http.patch(url, **kwargs)

    def http_delete(self, url, **kwargs):
        return self.http.delete(url, **kwargs)

