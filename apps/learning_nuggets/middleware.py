class AjaxRequestMiddleware:
    """
    Middleware to detect AJAX requests and set a flag in the request
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
        response = self.get_response(request)
        return response
