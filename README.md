# Hubble Shuttle 🚀

[![CircleCI build status](https://circleci.com/gh/HubbleHQ/shuttle.svg?style=svg&circle-token=db1939f52993f462688a0a10ffa554b41ef1211b)](https://circleci.com/gh/HubbleHQ/shuttle)

> Note: This project is pre-1.0 release. We are still working on integrating it in production
> systems here at HubbleHQ, and as a result, the API is not stable and might change before
> 1.0 release. This also means that not all HTTP features are currently supported (for example,
> cookies), but we are actively adding support for these.

Hubble Shuttle is an abstraction layer that makes it easy to write REST API clients.

It enbraces convention over configuration, and abstracts a lot of common patterns to simplify
writing API clients.

For example, writing a simple client for a sample user service is as simple as:

```python
class UserAPI(ShuttleAPI):

    api_endpoint = "https://user-service.example.com/"
    query = {
        "api_key": "my_api_key"
    }

    def get_user(self, user_id):
        # Returns a dict object `{ "id": 123, ... }`
        return self.http_get(f"/users/{user_id}").data
```

Shuttle will take care of building the full URL of the resource, inject API keys,
parse the response from the server based on content type, extracts the response based
on content encoding, and handles HTTP and networking errors.

## Installation

```
pip install hubble_shuttle
```

### Supported Python versions

Shuttle is build and tested with Python 3.9.

## Client-level configuration

Creating an API client only requires you to extend the `ShuttleAPI` class, and provide some configuration
parameters:

```python
class MyClientAPI(ShuttleAPI):

    # The root endpoint for our API.
    api_endpoint = "https://myservice/"

    # Headers to send with every request to the API, for example, authorization headers.
    headers = {
      "Header-Name": "header value"
    }

    # Query parameters to send with every request to the API, for example, API keys.
    query = {
      "query_param": "param value"
    }

```

## Making HTTP requests

The `ShuttleAPI` class provides methods to allow you to make HTTP requests against you API, in
the form of `http_X` instance methods, where `X` is the HTTP verb you'd like to use.

A simple GET request can be made like so:

```python
def get_user(self, user_id):
    response = self.http_get(f"/users/{id}")
    return response.data
```

If the HTTP server returns a successful (2xx) status code, the `http_X` methods will return a response object. If
the server returns a client error (4xx) or server error (5xx), the `http_X` methods will raise a `HTTPError`.

When making an individual request, it is possible to override any client-level header or query parameter that
was set on the class. For example:

```python
class ConflictingHeaderAPI(ShuttleAPI):

    api_endpoint = "https://user-service.example.com/"
    headers = { "Authorization": "Bearer default_api_key" }

    def get_user_profile(self, user_auth_token):
        # The request will contain the user_auth_token, overriding the default set at the client level
        return self.http_get("/me", headers={ "Authorization": f"Bearer {user_auth_token}" })

```

### Adding locale information

Some requests need to be localised. Shuttle supports this in its constructor using a `locale`
kwarg, which is passed on as the `Accept-Language` header.

```python
class MyClientApi(ShuttleApi):
    # ...
    pass

api = MyClientApi(locale="en-us")
```

### Sending a request body

When making a POST, PUT, or PATCH request, it is possible to embed a request body. The request
body will be automatically encoded based on request content type, if it is set. If the content
type isn't explicitely set, `application/x-www-form-urlencoded` is used as a default.

```python
def create_user(self):
    # Sends a POST request to `/users` with body `username=foo&email=foo@example.com`
    self.http_post("/users", data={"username": "foo", "email": "foo@example.com"})
```

You can also send the body in another format if you prefer:

```python
def create_user(self):
    # Sends a POST request to `/users` with body `{"username":"foo","email":"foo@example.com"}`
    self.http_post("/users", content_type="application/json", data={"username": "foo", "email": "foo@example.com"})
```

Shuttle supports the following content types for sending a request body:
* `application/x-www-form-urlencoded` (default)
* `application/json`

Specifying an unknown content type will result in a `ValueError` being raised.

If the API you are contacting always expects the request body to be another content type than the
default `application/x-www-form-urlencoded`, it is possible to change it for a whole client too:

```python
class UserAPI(ShuttleAPI):

    request_content_type = "application/json"

    def create_user(self):
        # Sends a POST request to `/users` with body `{"username":"foo","email":"foo@example.com"}`
        self.http_post("/users", data={"username": "foo", "email": "foo@example.com"})
```


### Response format

The response object contains information returned by the HTTP backend. You can access:

* `data`: the body of the HTTP response, parsed based on its content type. Shuttle supports:
  * `text/plain`: `response.data` will be a Unicode string, containing the response body.
  * `application/json`: `response.data` will be a Python dict or array representing the JSON object.
  * For any other content type, Shuttle will return a binary string containing the raw response body.
* `status_code`: the status code from the HTTP response.

### Error handling

For any client error (4xx) or server error (5xx) status code, Shuttle will raise an error of type `HTTPError` instead
of returning a response object.

Depending on the status code, Shuttle will return a subclass of `HTTPError` to make it easier to respond to specific status
codes. For example, returning `None` when the server returns a `404 (Not found)` error is straight-forward:

```python
def get_user(self, user_id):
    try:
        return self.http_get(f"/users/{id}").data
    except NotFoundError:
        return None
```

The errors class tree is as follows:
* `HTTPError` (representing either 4xx or 5xx HTTP error)
  * `HTTPClientError` (representing any type of 4xx error)
    * `BadRequestError` (400 HTTP error)
    * `NotFoundError` (404 HTTP error)
  * `HTTPServerError` (representing any type of 5xx error)
    * `InternalServerError` (500 HTTP error)

For non-HTTP error (networking, DNS resolution errors, ...), Shuttle will return an `APIError`.

All errors are in the `hubble_shuttle.exceptions` module.

## Contributing

Pull requests in Github are accepted and the best way to contribute to Shuttle.

### Testing

We require pull requests to have comprehensive tests coverage, and for all the tests to be passing.

Tests are run against all the supported Python versions, using Docker. You can run the test suite using Docker:
```
# Builds and sets up the Docker containers
make dev-build

# Runs the test suite inside Docker
make dev-test
```

### Deploying to PyPi

1. Ensure you're listed as a contributing member for the package in Pypi and if you want to do a test deploy in test PyPi as well. They use separate users, so you may need to sign up again. We don't seem to use organisations in PyPi so you need adding to the project directly.
2. Update the version number in `pyproject.toml` use semantic version as it makes sense, e.g. minor version changes for minor updates
3. Run `make build` to get a build - you don't need to anything with this version but look in the `dist/` directory to make sure the version and name all look correct.
4. Run `make test-deploy` this will build and attempt an upload to the test PyPi
 1. Before being uploaded it will ask you to enter a token.
 2. To generate a token go to https://test.pypi.org/, login -> account settings -> scroll down -> api tokens -> generate a new one with access to the project. If you don't see the project then go back to point 1.
 3. Copy the token into the prompt from `make test-deploy`
 4. Check test pypi has the updated version.
5. Run `make deploy` for a production release and follow the same steps as the test but on the proper PyPi.
