from unittest import TestCase
from unittest.mock import MagicMock, patch

import hubble_shuttle
from hubble_shuttle import ShuttleAPI


class ShuttleAPITestClient(ShuttleAPI):
    api_endpoint = "http://test_http_server/"


class ShuttleAPITest(TestCase):

    def test_response_headers(self):
        response = ShuttleAPITestClient().http_get("/response-headers", query={"Test-Header": "test-value"})
        self.assertEqual("test-value", response.headers["Test-Header"], "Returns the expected header value")
        self.assertEqual("test-value", response.headers.get("Test-Header"), "Behaves like a dict")

    def test_response_headers_are_read_only(self):
        response = ShuttleAPITestClient().http_get("/response-headers", query={"Test-Header": "test-value"})

        with self.assertRaises(TypeError) as cm:
            response.headers["Test-Header"] = "another-value"

        self.assertEqual("test-value", response.headers["Test-Header"], "Doesn't change the values after an attempted write")

    def test_get_request(self):
        response = ShuttleAPITestClient().http_get("/get")
        self.assertEqual('http://test_http_server/get', response.data['url'], "Parses the JSON response")
        self.assertEqual({}, response.data['args'], "Doesn't include any query params")

    def test_get_request_status_code(self):
        response = ShuttleAPITestClient().http_get("/status/200")
        self.assertEqual(200, response.status_code, "Returns the HTTP status code")
        response = ShuttleAPITestClient().http_get("/status/201")
        self.assertEqual(201, response.status_code, "Returns the HTTP status code")

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

    def test_get_gzip_content_encoding(self):
        response = ShuttleAPITestClient().http_get("/gzip")
        self.assertEqual(response.data['gzipped'], True, "Decodes the gzipped response content")

    def test_get_request_with_class_headers(self):
        client = ShuttleAPITestClient(headers={"Foo": "Bar"})
        response = client.http_get("/get")
        self.assertEqual("Bar", response.data['headers']['Foo'], "Sends the client-level headers")

    def test_get_request_with_request_headers(self):
        client = ShuttleAPITestClient()
        response = client.http_get("/get", headers={"Foo": "Bar"})
        self.assertEqual("Bar", response.data['headers']['Foo'], "Sends the request-level headers")

    def test_get_request_with_class_and_request_headers(self):
        client = ShuttleAPITestClient(headers={"Foo": "Bar"})
        response = client.http_get("/get", headers={"Bar": "Baz"})
        self.assertEqual("Bar", response.data['headers']['Foo'], "Sends the client-level headers")
        self.assertEqual("Baz", response.data['headers']['Bar'], "Sends the request-level headers")

    def test_get_request_with_class_and_request_headers_conflict(self):
        client = ShuttleAPITestClient(headers={"Foo": "Bar"})
        response = client.http_get("/get", headers={"Foo": "Baz"})
        self.assertEqual("Baz", response.data['headers']['Foo'], "Sends the request-level headers")

    def test_get_request_with_class_query_param(self):
        client = ShuttleAPITestClient(query={"foo": "bar"})
        response = client.http_get("/get")
        self.assertEqual("bar", response.data['args']['foo'], "Sends the client-level parameters")

    def test_get_request_with_request_query_param(self):
        client = ShuttleAPITestClient()
        response = client.http_get("/get", query={"foo": "bar"})
        self.assertEqual("bar", response.data['args']['foo'], "Sends the request-level parameters")

    def test_get_request_with_class_and_request_query_param(self):
        client = ShuttleAPITestClient(query={"foo": "bar"})
        response = client.http_get("/get", query={"bar": "baz"})
        self.assertEqual("bar", response.data['args']['foo'], "Sends the client-level parameters")
        self.assertEqual("baz", response.data['args']['bar'], "Sends the request-level parameters")

    def test_get_request_with_class_and_request_query_param_conflict(self):
        client = ShuttleAPITestClient(query={"foo": "bar"})
        response = client.http_get("/get", query={"foo": "baz"})
        self.assertEqual("baz", response.data['args']['foo'], "Sends the request-level parameters")

    def test_get_generic_networking_error(self):
        client = ShuttleAPITestClient(api_endpoint='http://test_http_server:1234')
        with self.assertRaises(hubble_shuttle.exceptions.APIError) as cm:
            client.http_get("/get")
        self.assertEqual("ShuttleAPITestClient", cm.exception.service_name, "Sets the service name")
        self.assertEqual("/get", cm.exception.source, "Sets the error source")

    def test_get_400_http_error(self):
        with self.assertRaises(hubble_shuttle.exceptions.BadRequestError) as cm:
            ShuttleAPITestClient().http_get("/status/400")
        self.assertEqual(400, cm.exception.internal_status_code, "Returns the error status code")
        self.assertEqual("ShuttleAPITestClient", cm.exception.service_name, "Sets the service name")
        self.assertEqual("/status/400", cm.exception.source, "Sets the error source")

    def test_get_404_http_error(self):
        with self.assertRaises(hubble_shuttle.exceptions.NotFoundError) as cm:
            ShuttleAPITestClient().http_get("/status/404")
        self.assertEqual(404, cm.exception.internal_status_code, "Returns the error status code")
        self.assertEqual("ShuttleAPITestClient", cm.exception.service_name, "Sets the service name")
        self.assertEqual("/status/404", cm.exception.source, "Sets the error source")

    def test_get_409_http_error(self):
        with self.assertRaises(hubble_shuttle.exceptions.ConflictError) as cm:
            ShuttleAPITestClient().http_get("/status/409")
        self.assertEqual(409, cm.exception.internal_status_code, "Returns the error status code")
        self.assertEqual("ShuttleAPITestClient", cm.exception.service_name, "Sets the service name")
        self.assertEqual("/status/409", cm.exception.source, "Sets the error source")

    def test_get_499_http_error(self):
        with self.assertRaises(hubble_shuttle.exceptions.HTTPClientError) as cm:
            ShuttleAPITestClient().http_get("/status/499")
        self.assertEqual(499, cm.exception.internal_status_code, "Returns the error status code")
        self.assertEqual("ShuttleAPITestClient", cm.exception.service_name, "Sets the service name")
        self.assertEqual("/status/499", cm.exception.source, "Sets the error source")

    def test_get_500_http_error(self):
        with self.assertRaises(hubble_shuttle.exceptions.InternalServerError) as cm:
            ShuttleAPITestClient().http_get("/status/500")
        self.assertEqual(500, cm.exception.internal_status_code, "Returns the error status code")
        self.assertEqual("ShuttleAPITestClient", cm.exception.service_name, "Sets the service name")
        self.assertEqual("/status/500", cm.exception.source, "Sets the error source")

    def test_get_599_http_error(self):
        with self.assertRaises(hubble_shuttle.exceptions.HTTPServerError) as cm:
            ShuttleAPITestClient().http_get("/status/599")
        self.assertEqual(599, cm.exception.internal_status_code, "Returns the error status code")
        self.assertEqual("ShuttleAPITestClient", cm.exception.service_name, "Sets the service name")
        self.assertEqual("/status/599", cm.exception.source, "Sets the error source")

    def test_get_with_request_data(self):
        with self.assertRaises(TypeError):
            ShuttleAPITestClient().http_get("/get", data={"foo": "bar"})

    def test_get_unknown_kwarg(self):
        with self.assertRaises(TypeError):
            ShuttleAPITestClient().http_get("/get", foo="bar")

    def test_post_request(self):
        response = ShuttleAPITestClient().http_post("/post")
        self.assertEqual('http://test_http_server/post', response.data['url'], "Parses the JSON response")
        self.assertEqual({}, response.data['args'], "Doesn't include any query params")

    def test_post_request_no_body(self):
        response = ShuttleAPITestClient().http_post("/post")
        self.assertEqual("", response.data['data'], "Doesn't send any content body")
        self.assertEqual({}, response.data['form'], "Doesn't send any form data")

    def test_post_request_with_data(self):
        response = ShuttleAPITestClient().http_post("/post", data={"foo": "bar", "bar": "baz"})
        self.assertEqual({"foo": "bar", "bar": "baz"}, response.data['form'], "Sends the data in form format")
        self.assertEqual("application/x-www-form-urlencoded", response.data['headers']['Content-Type'], "Sets the appropriate content type header")

    def test_post_request_with_data_form_urlencoded(self):
        response = ShuttleAPITestClient().http_post("/post", content_type="application/x-www-form-urlencoded", data={"foo": "bar", "bar": "baz"})
        self.assertEqual({"foo": "bar", "bar": "baz"}, response.data['form'], "Sends the data in form format")
        self.assertEqual("application/x-www-form-urlencoded", response.data['headers']['Content-Type'], "Sets the appropriate content type header")

    def test_post_request_with_data_json(self):
        response = ShuttleAPITestClient().http_post("/post", content_type="application/json", data={"foo": "bar", "bar": "baz"})
        self.assertEqual({"foo": "bar", "bar": "baz"}, response.data['json'], "Sends the data in JSON format")
        self.assertEqual("application/json", response.data['headers']['Content-Type'], "Sets the appropriate content type header")

    def test_post_request_with_data_unknown_content_type(self):
        with self.assertRaises(ValueError) as cm:
            ShuttleAPITestClient().http_post("/post", content_type="application/bad-content-type", data={"foo": "bar", "bar": "baz"})
        self.assertEqual(str(cm.exception), "Unknown content type for request: application/bad-content-type", "Indicates the invalid content type")

    def test_post_request_with_data_client_request_content_type(self):
        client = ShuttleAPITestClient(request_content_type="application/json")
        response = client.http_post("/post", data={"foo": "bar", "bar": "baz"})
        self.assertEqual({"foo": "bar", "bar": "baz"}, response.data['json'], "Sends the data in JSON format")
        self.assertEqual("application/json", response.data['headers']['Content-Type'], "Sets the appropriate content type header")

    def test_post_request_status_code(self):
        response = ShuttleAPITestClient().http_post("/status/200")
        self.assertEqual(200, response.status_code, "Returns the HTTP status code")
        response = ShuttleAPITestClient().http_post("/status/201")
        self.assertEqual(201, response.status_code, "Returns the HTTP status code")

    def test_post_request_with_class_headers(self):
        client = ShuttleAPITestClient(headers={"Foo": "Bar"})
        response = client.http_post("/post")
        self.assertEqual("Bar", response.data['headers']['Foo'], "Sends the client-level headers")

    def test_post_request_with_request_headers(self):
        client = ShuttleAPITestClient()
        response = client.http_post("/post", headers={"Foo": "Bar"})
        self.assertEqual("Bar", response.data['headers']['Foo'], "Sends the request-level headers")

    def test_post_request_with_class_and_request_headers(self):
        client = ShuttleAPITestClient(headers={"Foo": "Bar"})
        response = client.http_post("/post", headers={"Bar": "Baz"})
        self.assertEqual("Bar", response.data['headers']['Foo'], "Sends the client-level headers")
        self.assertEqual("Baz", response.data['headers']['Bar'], "Sends the request-level headers")

    def test_post_request_with_class_and_request_headers_conflict(self):
        client = ShuttleAPITestClient(headers={"Foo": "Bar"})
        response = client.http_post("/post", headers={"Foo": "Baz"})
        self.assertEqual("Baz", response.data['headers']['Foo'], "Sends the request-level headers")

    def test_post_request_with_class_query_param(self):
        client = ShuttleAPITestClient(query={"foo": "bar"})
        response = client.http_post("/post")
        self.assertEqual("bar", response.data['args']['foo'], "Sends the client-level parameters")

    def test_post_request_with_request_query_param(self):
        client = ShuttleAPITestClient()
        response = client.http_post("/post", query={"foo": "bar"})
        self.assertEqual("bar", response.data['args']['foo'], "Sends the request-level parameters")

    def test_post_request_with_class_and_request_query_param(self):
        client = ShuttleAPITestClient(query={"foo": "bar"})
        response = client.http_post("/post", query={"bar": "baz"})
        self.assertEqual("bar", response.data['args']['foo'], "Sends the client-level parameters")
        self.assertEqual("baz", response.data['args']['bar'], "Sends the request-level parameters")

    def test_post_request_with_class_and_request_query_param_conflict(self):
        client = ShuttleAPITestClient(query={"foo": "bar"})
        response = client.http_post("/post", query={"foo": "baz"})
        self.assertEqual("baz", response.data['args']['foo'], "Sends the request-level parameters")

    def test_post_generic_networking_error(self):
        client = ShuttleAPITestClient(api_endpoint='http://test_http_server:1234')
        with self.assertRaises(hubble_shuttle.exceptions.APIError) as cm:
            client.http_post("/post")
        self.assertEqual("ShuttleAPITestClient", cm.exception.service_name, "Sets the service name")
        self.assertEqual("/post", cm.exception.source, "Sets the error source")

    def test_post_400_http_error(self):
        with self.assertRaises(hubble_shuttle.exceptions.BadRequestError) as cm:
            ShuttleAPITestClient().http_post("/status/400")
        self.assertEqual(400, cm.exception.internal_status_code, "Returns the error status code")
        self.assertEqual("ShuttleAPITestClient", cm.exception.service_name, "Sets the service name")
        self.assertEqual("/status/400", cm.exception.source, "Sets the error source")

    def test_post_404_http_error(self):
        with self.assertRaises(hubble_shuttle.exceptions.NotFoundError) as cm:
            ShuttleAPITestClient().http_post("/status/404")
        self.assertEqual(404, cm.exception.internal_status_code, "Returns the error status code")
        self.assertEqual("ShuttleAPITestClient", cm.exception.service_name, "Sets the service name")
        self.assertEqual("/status/404", cm.exception.source, "Sets the error source")

    def test_post_499_http_error(self):
        with self.assertRaises(hubble_shuttle.exceptions.HTTPClientError) as cm:
            ShuttleAPITestClient().http_post("/status/499")
        self.assertEqual(499, cm.exception.internal_status_code, "Returns the error status code")
        self.assertEqual("ShuttleAPITestClient", cm.exception.service_name, "Sets the service name")
        self.assertEqual("/status/499", cm.exception.source, "Sets the error source")

    def test_post_500_http_error(self):
        with self.assertRaises(hubble_shuttle.exceptions.InternalServerError) as cm:
            ShuttleAPITestClient().http_post("/status/500")
        self.assertEqual(500, cm.exception.internal_status_code, "Returns the error status code")
        self.assertEqual("ShuttleAPITestClient", cm.exception.service_name, "Sets the service name")
        self.assertEqual("/status/500", cm.exception.source, "Sets the error source")

    def test_post_599_http_error(self):
        with self.assertRaises(hubble_shuttle.exceptions.HTTPServerError) as cm:
            ShuttleAPITestClient().http_post("/status/599")
        self.assertEqual(599, cm.exception.internal_status_code, "Returns the error status code")
        self.assertEqual("ShuttleAPITestClient", cm.exception.service_name, "Sets the service name")
        self.assertEqual("/status/599", cm.exception.source, "Sets the error source")

    def test_post_unknown_kwarg(self):
        with self.assertRaises(TypeError):
            ShuttleAPITestClient().http_post("/post", foo="bar")

    def test_put_request(self):
        response = ShuttleAPITestClient().http_put("/put")
        self.assertEqual('http://test_http_server/put', response.data['url'], "Parses the JSON response")
        self.assertEqual({}, response.data['args'], "Doesn't include any query params")

    def test_put_request_no_body(self):
        response = ShuttleAPITestClient().http_put("/put")
        self.assertEqual("", response.data['data'], "Doesn't send any content body")
        self.assertEqual({}, response.data['form'], "Doesn't send any form data")

    def test_put_request_with_data(self):
        response = ShuttleAPITestClient().http_put("/put", data={"foo": "bar", "bar": "baz"})
        self.assertEqual({"foo": "bar", "bar": "baz"}, response.data['form'], "Sends the data in form format")
        self.assertEqual("application/x-www-form-urlencoded", response.data['headers']['Content-Type'], "Sets the appropriate content type header")

    def test_put_request_with_data_form_urlencoded(self):
        response = ShuttleAPITestClient().http_put("/put", content_type="application/x-www-form-urlencoded", data={"foo": "bar", "bar": "baz"})
        self.assertEqual({"foo": "bar", "bar": "baz"}, response.data['form'], "Sends the data in form format")
        self.assertEqual("application/x-www-form-urlencoded", response.data['headers']['Content-Type'], "Sets the appropriate content type header")

    def test_put_request_with_data_json(self):
        response = ShuttleAPITestClient().http_put("/put", content_type="application/json", data={"foo": "bar", "bar": "baz"})
        self.assertEqual({"foo": "bar", "bar": "baz"}, response.data['json'], "Sends the data in JSON format")
        self.assertEqual("application/json", response.data['headers']['Content-Type'], "Sets the appropriate content type header")

    def test_put_request_with_data_unknown_content_type(self):
        with self.assertRaises(ValueError) as cm:
            ShuttleAPITestClient().http_put("/put", content_type="application/bad-content-type", data={"foo": "bar", "bar": "baz"})
        self.assertEqual(str(cm.exception), "Unknown content type for request: application/bad-content-type", "Indicates the invalid content type")

    def test_put_request_with_data_client_request_content_type(self):
        client = ShuttleAPITestClient(request_content_type="application/json")
        response = client.http_put("/put", data={"foo": "bar", "bar": "baz"})
        self.assertEqual({"foo": "bar", "bar": "baz"}, response.data['json'], "Sends the data in JSON format")
        self.assertEqual("application/json", response.data['headers']['Content-Type'], "Sets the appropriate content type header")

    def test_put_request_status_code(self):
        response = ShuttleAPITestClient().http_put("/status/200")
        self.assertEqual(200, response.status_code, "Returns the HTTP status code")
        response = ShuttleAPITestClient().http_put("/status/201")
        self.assertEqual(201, response.status_code, "Returns the HTTP status code")

    def test_put_request_with_class_headers(self):
        client = ShuttleAPITestClient(headers={"Foo": "Bar"})
        response = client.http_put("/put")
        self.assertEqual("Bar", response.data['headers']['Foo'], "Sends the client-level headers")

    def test_put_request_with_request_headers(self):
        client = ShuttleAPITestClient()
        response = client.http_put("/put", headers={"Foo": "Bar"})
        self.assertEqual("Bar", response.data['headers']['Foo'], "Sends the request-level headers")

    def test_put_request_with_class_and_request_headers(self):
        client = ShuttleAPITestClient(headers={"Foo": "Bar"})
        response = client.http_put("/put", headers={"Bar": "Baz"})
        self.assertEqual("Bar", response.data['headers']['Foo'], "Sends the client-level headers")
        self.assertEqual("Baz", response.data['headers']['Bar'], "Sends the request-level headers")

    def test_put_request_with_class_and_request_headers_conflict(self):
        client = ShuttleAPITestClient(headers={"Foo": "Bar"})
        response = client.http_put("/put", headers={"Foo": "Baz"})
        self.assertEqual("Baz", response.data['headers']['Foo'], "Sends the request-level headers")

    def test_put_request_with_class_query_param(self):
        client = ShuttleAPITestClient(query={"foo": "bar"})
        response = client.http_put("/put")
        self.assertEqual("bar", response.data['args']['foo'], "Sends the client-level parameters")

    def test_put_request_with_request_query_param(self):
        client = ShuttleAPITestClient()
        response = client.http_put("/put", query={"foo": "bar"})
        self.assertEqual("bar", response.data['args']['foo'], "Sends the request-level parameters")

    def test_put_request_with_class_and_request_query_param(self):
        client = ShuttleAPITestClient(query={"foo": "bar"})
        response = client.http_put("/put", query={"bar": "baz"})
        self.assertEqual("bar", response.data['args']['foo'], "Sends the client-level parameters")
        self.assertEqual("baz", response.data['args']['bar'], "Sends the request-level parameters")

    def test_put_request_with_class_and_request_query_param_conflict(self):
        client = ShuttleAPITestClient(query={"foo": "bar"})
        response = client.http_put("/put", query={"foo": "baz"})
        self.assertEqual("baz", response.data['args']['foo'], "Sends the request-level parameters")

    def test_put_generic_networking_error(self):
        client = ShuttleAPITestClient(api_endpoint='http://test_http_server:1234')
        with self.assertRaises(hubble_shuttle.exceptions.APIError) as cm:
            client.http_put("/put")
        self.assertEqual("ShuttleAPITestClient", cm.exception.service_name, "Sets the service name")
        self.assertEqual("/put", cm.exception.source, "Sets the error source")

    def test_put_400_http_error(self):
        with self.assertRaises(hubble_shuttle.exceptions.BadRequestError) as cm:
            ShuttleAPITestClient().http_put("/status/400")
        self.assertEqual(400, cm.exception.internal_status_code, "Returns the error status code")
        self.assertEqual("ShuttleAPITestClient", cm.exception.service_name, "Sets the service name")
        self.assertEqual("/status/400", cm.exception.source, "Sets the error source")

    def test_put_404_http_error(self):
        with self.assertRaises(hubble_shuttle.exceptions.NotFoundError) as cm:
            ShuttleAPITestClient().http_put("/status/404")
        self.assertEqual(404, cm.exception.internal_status_code, "Returns the error status code")
        self.assertEqual("ShuttleAPITestClient", cm.exception.service_name, "Sets the service name")
        self.assertEqual("/status/404", cm.exception.source, "Sets the error source")

    def test_put_499_http_error(self):
        with self.assertRaises(hubble_shuttle.exceptions.HTTPClientError) as cm:
            ShuttleAPITestClient().http_put("/status/499")
        self.assertEqual(499, cm.exception.internal_status_code, "Returns the error status code")
        self.assertEqual("ShuttleAPITestClient", cm.exception.service_name, "Sets the service name")
        self.assertEqual("/status/499", cm.exception.source, "Sets the error source")

    def test_put_500_http_error(self):
        with self.assertRaises(hubble_shuttle.exceptions.InternalServerError) as cm:
            ShuttleAPITestClient().http_put("/status/500")
        self.assertEqual(500, cm.exception.internal_status_code, "Returns the error status code")
        self.assertEqual("ShuttleAPITestClient", cm.exception.service_name, "Sets the service name")
        self.assertEqual("/status/500", cm.exception.source, "Sets the error source")

    def test_put_599_http_error(self):
        with self.assertRaises(hubble_shuttle.exceptions.HTTPServerError) as cm:
            ShuttleAPITestClient().http_put("/status/599")
        self.assertEqual(599, cm.exception.internal_status_code, "Returns the error status code")
        self.assertEqual("ShuttleAPITestClient", cm.exception.service_name, "Sets the service name")
        self.assertEqual("/status/599", cm.exception.source, "Sets the error source")

    def test_put_unknown_kwarg(self):
        with self.assertRaises(TypeError):
            ShuttleAPITestClient().http_put("/put", foo="bar")

    def test_patch_request(self):
        response = ShuttleAPITestClient().http_patch("/patch")
        self.assertEqual('http://test_http_server/patch', response.data['url'], "Parses the JSON response")
        self.assertEqual({}, response.data['args'], "Doesn't include any query params")

    def test_patch_request_no_body(self):
        response = ShuttleAPITestClient().http_patch("/patch")
        self.assertEqual("", response.data['data'], "Doesn't send any content body")
        self.assertEqual({}, response.data['form'], "Doesn't send any form data")

    def test_patch_request_with_data(self):
        response = ShuttleAPITestClient().http_patch("/patch", data={"foo": "bar", "bar": "baz"})
        self.assertEqual({"foo": "bar", "bar": "baz"}, response.data['form'], "Sends the data in form format")
        self.assertEqual("application/x-www-form-urlencoded", response.data['headers']['Content-Type'], "Sets the appropriate content type header")

    def test_patch_request_with_data_form_urlencoded(self):
        response = ShuttleAPITestClient().http_patch("/patch", content_type="application/x-www-form-urlencoded", data={"foo": "bar", "bar": "baz"})
        self.assertEqual({"foo": "bar", "bar": "baz"}, response.data['form'], "Sends the data in form format")
        self.assertEqual("application/x-www-form-urlencoded", response.data['headers']['Content-Type'], "Sets the appropriate content type header")

    def test_patch_request_with_data_json(self):
        response = ShuttleAPITestClient().http_patch("/patch", content_type="application/json", data={"foo": "bar", "bar": "baz"})
        self.assertEqual({"foo": "bar", "bar": "baz"}, response.data['json'], "Sends the data in JSON format")
        self.assertEqual("application/json", response.data['headers']['Content-Type'], "Sets the appropriate content type header")

    def test_patch_request_with_data_unknown_content_type(self):
        with self.assertRaises(ValueError) as cm:
            ShuttleAPITestClient().http_patch("/patch", content_type="application/bad-content-type", data={"foo": "bar", "bar": "baz"})
        self.assertEqual(str(cm.exception), "Unknown content type for request: application/bad-content-type", "Indicates the invalid content type")

    def test_patch_request_with_data_client_request_content_type(self):
        client = ShuttleAPITestClient(request_content_type="application/json")
        response = client.http_patch("/patch", data={"foo": "bar", "bar": "baz"})
        self.assertEqual({"foo": "bar", "bar": "baz"}, response.data['json'], "Sends the data in JSON format")
        self.assertEqual("application/json", response.data['headers']['Content-Type'], "Sets the appropriate content type header")

    def test_patch_request_status_code(self):
        response = ShuttleAPITestClient().http_patch("/status/200")
        self.assertEqual(200, response.status_code, "Returns the HTTP status code")
        response = ShuttleAPITestClient().http_patch("/status/201")
        self.assertEqual(201, response.status_code, "Returns the HTTP status code")

    def test_patch_request_with_class_headers(self):
        client = ShuttleAPITestClient(headers={"Foo": "Bar"})
        response = client.http_patch("/patch")
        self.assertEqual("Bar", response.data['headers']['Foo'], "Sends the client-level headers")

    def test_patch_request_with_request_headers(self):
        client = ShuttleAPITestClient()
        response = client.http_patch("/patch", headers={"Foo": "Bar"})
        self.assertEqual("Bar", response.data['headers']['Foo'], "Sends the request-level headers")

    def test_patch_request_with_class_and_request_headers(self):
        client = ShuttleAPITestClient(headers={"Foo": "Bar"})
        response = client.http_patch("/patch", headers={"Bar": "Baz"})
        self.assertEqual("Bar", response.data['headers']['Foo'], "Sends the client-level headers")
        self.assertEqual("Baz", response.data['headers']['Bar'], "Sends the request-level headers")

    def test_patch_request_with_class_and_request_headers_conflict(self):
        client = ShuttleAPITestClient(headers={"Foo": "Bar"})
        response = client.http_patch("/patch", headers={"Foo": "Baz"})
        self.assertEqual("Baz", response.data['headers']['Foo'], "Sends the request-level headers")

    def test_patch_request_with_class_query_param(self):
        client = ShuttleAPITestClient(query={"foo": "bar"})
        response = client.http_patch("/patch")
        self.assertEqual("bar", response.data['args']['foo'], "Sends the client-level parameters")

    def test_patch_request_with_request_query_param(self):
        client = ShuttleAPITestClient()
        response = client.http_patch("/patch", query={"foo": "bar"})
        self.assertEqual("bar", response.data['args']['foo'], "Sends the request-level parameters")

    def test_patch_request_with_class_and_request_query_param(self):
        client = ShuttleAPITestClient(query={"foo": "bar"})
        response = client.http_patch("/patch", query={"bar": "baz"})
        self.assertEqual("bar", response.data['args']['foo'], "Sends the client-level parameters")
        self.assertEqual("baz", response.data['args']['bar'], "Sends the request-level parameters")

    def test_patch_request_with_class_and_request_query_param_conflict(self):
        client = ShuttleAPITestClient(query={"foo": "bar"})
        response = client.http_patch("/patch", query={"foo": "baz"})
        self.assertEqual("baz", response.data['args']['foo'], "Sends the request-level parameters")

    def test_patch_generic_networking_error(self):
        client = ShuttleAPITestClient(api_endpoint='http://test_http_server:1234')
        with self.assertRaises(hubble_shuttle.exceptions.APIError) as cm:
            client.http_patch("/patch")
        self.assertEqual("ShuttleAPITestClient", cm.exception.service_name, "Sets the service name")
        self.assertEqual("/patch", cm.exception.source, "Sets the error source")

    def test_patch_400_http_error(self):
        with self.assertRaises(hubble_shuttle.exceptions.BadRequestError) as cm:
            ShuttleAPITestClient().http_patch("/status/400")
        self.assertEqual(400, cm.exception.internal_status_code, "Returns the error status code")
        self.assertEqual("ShuttleAPITestClient", cm.exception.service_name, "Sets the service name")
        self.assertEqual("/status/400", cm.exception.source, "Sets the error source")

    def test_patch_404_http_error(self):
        with self.assertRaises(hubble_shuttle.exceptions.NotFoundError) as cm:
            ShuttleAPITestClient().http_patch("/status/404")
        self.assertEqual(404, cm.exception.internal_status_code, "Returns the error status code")
        self.assertEqual("ShuttleAPITestClient", cm.exception.service_name, "Sets the service name")
        self.assertEqual("/status/404", cm.exception.source, "Sets the error source")

    def test_patch_499_http_error(self):
        with self.assertRaises(hubble_shuttle.exceptions.HTTPClientError) as cm:
            ShuttleAPITestClient().http_patch("/status/499")
        self.assertEqual(499, cm.exception.internal_status_code, "Returns the error status code")
        self.assertEqual("ShuttleAPITestClient", cm.exception.service_name, "Sets the service name")
        self.assertEqual("/status/499", cm.exception.source, "Sets the error source")

    def test_patch_500_http_error(self):
        with self.assertRaises(hubble_shuttle.exceptions.InternalServerError) as cm:
            ShuttleAPITestClient().http_patch("/status/500")
        self.assertEqual(500, cm.exception.internal_status_code, "Returns the error status code")
        self.assertEqual("ShuttleAPITestClient", cm.exception.service_name, "Sets the service name")
        self.assertEqual("/status/500", cm.exception.source, "Sets the error source")

    def test_patch_599_http_error(self):
        with self.assertRaises(hubble_shuttle.exceptions.HTTPServerError) as cm:
            ShuttleAPITestClient().http_patch("/status/599")
        self.assertEqual(599, cm.exception.internal_status_code, "Returns the error status code")
        self.assertEqual("ShuttleAPITestClient", cm.exception.service_name, "Sets the service name")
        self.assertEqual("/status/599", cm.exception.source, "Sets the error source")

    def test_patch_unknown_kwarg(self):
        with self.assertRaises(TypeError):
            ShuttleAPITestClient().http_patch("/patch", foo="bar")

    def test_delete_request(self):
        response = ShuttleAPITestClient().http_delete("/delete")
        self.assertEqual('http://test_http_server/delete', response.data['url'], "Parses the JSON response")
        self.assertEqual({}, response.data['args'], "Doesn't include any query params")

    def test_delete_request_status_code(self):
        response = ShuttleAPITestClient().http_delete("/status/200")
        self.assertEqual(200, response.status_code, "Returns the HTTP status code")
        response = ShuttleAPITestClient().http_delete("/status/201")
        self.assertEqual(201, response.status_code, "Returns the HTTP status code")

    def test_delete_request_with_class_headers(self):
        client = ShuttleAPITestClient(headers={"Foo": "Bar"})
        response = client.http_delete("/delete")
        self.assertEqual("Bar", response.data['headers']['Foo'], "Sends the client-level headers")

    def test_delete_request_with_request_headers(self):
        client = ShuttleAPITestClient()
        response = client.http_delete("/delete", headers={"Foo": "Bar"})
        self.assertEqual("Bar", response.data['headers']['Foo'], "Sends the request-level headers")

    def test_delete_request_with_class_and_request_headers(self):
        client = ShuttleAPITestClient(headers={"Foo": "Bar"})
        response = client.http_delete("/delete", headers={"Bar": "Baz"})
        self.assertEqual("Bar", response.data['headers']['Foo'], "Sends the client-level headers")
        self.assertEqual("Baz", response.data['headers']['Bar'], "Sends the request-level headers")

    def test_delete_request_with_class_and_request_headers_conflict(self):
        client = ShuttleAPITestClient(headers={"Foo": "Bar"})
        response = client.http_delete("/delete", headers={"Foo": "Baz"})
        self.assertEqual("Baz", response.data['headers']['Foo'], "Sends the request-level headers")

    def test_delete_request_with_class_query_param(self):
        client = ShuttleAPITestClient(query={"foo": "bar"})
        response = client.http_delete("/delete")
        self.assertEqual("bar", response.data['args']['foo'], "Sends the client-level parameters")

    def test_delete_request_with_request_query_param(self):
        client = ShuttleAPITestClient()
        response = client.http_delete("/delete", query={"foo": "bar"})
        self.assertEqual("bar", response.data['args']['foo'], "Sends the request-level parameters")

    def test_delete_request_with_class_and_request_query_param(self):
        client = ShuttleAPITestClient(query={"foo": "bar"})
        response = client.http_delete("/delete", query={"bar": "baz"})
        self.assertEqual("bar", response.data['args']['foo'], "Sends the client-level parameters")
        self.assertEqual("baz", response.data['args']['bar'], "Sends the request-level parameters")

    def test_delete_request_with_class_and_request_query_param_conflict(self):
        client = ShuttleAPITestClient(query={"foo": "bar"})
        response = client.http_delete("/delete", query={"foo": "baz"})
        self.assertEqual("baz", response.data['args']['foo'], "Sends the request-level parameters")

    def test_delete_generic_networking_error(self):
        client = ShuttleAPITestClient(api_endpoint='http://test_http_server:1234')
        with self.assertRaises(hubble_shuttle.exceptions.APIError) as cm:
            client.http_delete("/delete")
        self.assertEqual("ShuttleAPITestClient", cm.exception.service_name, "Sets the service name")
        self.assertEqual("/delete", cm.exception.source, "Sets the error source")

    def test_delete_400_http_error(self):
        with self.assertRaises(hubble_shuttle.exceptions.BadRequestError) as cm:
            ShuttleAPITestClient().http_delete("/status/400")
        self.assertEqual(400, cm.exception.internal_status_code, "Returns the error status code")
        self.assertEqual("ShuttleAPITestClient", cm.exception.service_name, "Sets the service name")
        self.assertEqual("/status/400", cm.exception.source, "Sets the error source")

    def test_delete_404_http_error(self):
        with self.assertRaises(hubble_shuttle.exceptions.NotFoundError) as cm:
            ShuttleAPITestClient().http_delete("/status/404")
        self.assertEqual(404, cm.exception.internal_status_code, "Returns the error status code")
        self.assertEqual("ShuttleAPITestClient", cm.exception.service_name, "Sets the service name")
        self.assertEqual("/status/404", cm.exception.source, "Sets the error source")

    def test_delete_499_http_error(self):
        with self.assertRaises(hubble_shuttle.exceptions.HTTPClientError) as cm:
            ShuttleAPITestClient().http_delete("/status/499")
        self.assertEqual(499, cm.exception.internal_status_code, "Returns the error status code")
        self.assertEqual("ShuttleAPITestClient", cm.exception.service_name, "Sets the service name")
        self.assertEqual("/status/499", cm.exception.source, "Sets the error source")

    def test_delete_500_http_error(self):
        with self.assertRaises(hubble_shuttle.exceptions.InternalServerError) as cm:
            ShuttleAPITestClient().http_delete("/status/500")
        self.assertEqual(500, cm.exception.internal_status_code, "Returns the error status code")
        self.assertEqual("ShuttleAPITestClient", cm.exception.service_name, "Sets the service name")
        self.assertEqual("/status/500", cm.exception.source, "Sets the error source")

    def test_delete_599_http_error(self):
        with self.assertRaises(hubble_shuttle.exceptions.HTTPServerError) as cm:
            ShuttleAPITestClient().http_delete("/status/599")
        self.assertEqual(599, cm.exception.internal_status_code, "Returns the error status code")
        self.assertEqual("ShuttleAPITestClient", cm.exception.service_name, "Sets the service name")
        self.assertEqual("/status/599", cm.exception.source, "Sets the error source")

    def test_delete_with_request_data(self):
        with self.assertRaises(TypeError):
            ShuttleAPITestClient().http_delete("/delete", data={"foo": "bar"})

    def test_delete_unknown_kwarg(self):
        with self.assertRaises(TypeError):
            ShuttleAPITestClient().http_delete("/delete", foo="bar")

