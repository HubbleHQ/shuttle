
class APIError(IOError):

    def __init__(self, service_name, source, original_error):
        self.original_error = original_error
        self.service_name = service_name
        self.source = source

class HTTPError(APIError):

    def __init__(self, service_name, source, original_error):
        super().__init__(service_name, source, original_error)
        self.internal_status_code = original_error.response.status_code
        self.response = original_error.response.json()

# For 4xx class errors
class HTTPClientError(HTTPError):
    pass

# For 5xx class errors
class HTTPServerError(HTTPError):
    pass

# For 400 HTTP errors
class BadRequestError(HTTPClientError):
    pass

# For 404 HTTP errors
class NotFoundError(HTTPClientError):
    pass

# For 500 HTTP errors
class InternalServerError(HTTPServerError):
    pass

HTTP_STATUS_CODE_CLASS_ERRORS = {
    range(400, 500): HTTPClientError,
    range(500, 600): HTTPServerError,
}

HTTP_STATUS_CODE_ERRORS = {
    400: BadRequestError,
    404: NotFoundError,
    500: InternalServerError,
}

