# apps/learning_nuggets/tests/test_middleware.py
from django.http import HttpResponse
from django.test import RequestFactory
from django.test import TestCase

from apps.learning_nuggets.middleware import AjaxRequestMiddleware


class AjaxRequestMiddlewareTests(TestCase):
    """
    Tests for the AjaxRequestMiddleware which detects AJAX requests.
    """

    def setUp(self):
        """
        Set up the test environment.
        Create a request factory and a simple view function.
        """
        self.factory = RequestFactory()

        # Create a simple middleware callable for testing
        def get_response(request):
            # Simple view that returns the is_ajax flag value
            return HttpResponse(str(request.is_ajax))

        self.middleware = AjaxRequestMiddleware(get_response)

    def test_ajax_request_detection(self):
        """
        Test that the middleware correctly identifies an AJAX request.
        """
        # Create a request with X-Requested-With header
        request = self.factory.get("/test-url/")
        request.headers = {"X-Requested-With": "XMLHttpRequest"}

        # Process the request through the middleware
        response = self.middleware(request)

        # Check that is_ajax was set to True
        self.assertEqual(response.content.decode(), "True")
        self.assertTrue(request.is_ajax)

    def test_non_ajax_request_detection(self):
        """
        Test that the middleware correctly identifies a non-AJAX request.
        """
        # Create a request without X-Requested-With header
        request = self.factory.get("/test-url/")
        request.headers = {}

        # Process the request through the middleware
        response = self.middleware(request)

        # Check that is_ajax was set to False
        self.assertEqual(response.content.decode(), "False")
        self.assertFalse(request.is_ajax)

    def test_with_different_header_value(self):
        """
        Test that the middleware correctly handles a request with a different
        X-Requested-With header value.
        """
        # Create a request with incorrect X-Requested-With header
        request = self.factory.get("/test-url/")
        request.headers = {"X-Requested-With": "SomethingElse"}

        # Process the request through the middleware
        response = self.middleware(request)

        # Check that is_ajax was set to False
        self.assertEqual(response.content.decode(), "False")
        self.assertFalse(request.is_ajax)

    def test_with_multiple_headers(self):
        """
        Test that the middleware works correctly with multiple headers present.
        """
        # Create a request with multiple headers including X-Requested-With
        request = self.factory.get("/test-url/")
        request.headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Process the request through the middleware
        response = self.middleware(request)

        # Check that is_ajax was set to True
        self.assertEqual(response.content.decode(), "True")
        self.assertTrue(request.is_ajax)

    def test_case_sensitivity(self):
        """
        Test that the middleware is case-sensitive for the X-Requested-With header value.
        """
        # Create a request with differently cased X-Requested-With header
        request = self.factory.get("/test-url/")
        request.headers = {"X-Requested-With": "xmlhttprequest"}  # lowercase

        # Process the request through the middleware
        response = self.middleware(request)

        # Check that is_ajax was set to False (should be case-sensitive)
        self.assertEqual(response.content.decode(), "False")
        self.assertFalse(request.is_ajax)
