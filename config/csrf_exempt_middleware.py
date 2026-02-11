# path to this file: "dml-marketing-middleware/config/csrf_exempt_middleware.py"

from django.utils.deprecation import MiddlewareMixin

class AdminCSRFExemptMiddleware(MiddlewareMixin):
    """
    Temporarily exempt /admin/ from CSRF checks.
    REMOVE THIS AFTER YOU'RE ABLE TO LOGIN!
    """
    def process_request(self, request):
        if request.path.startswith('/admin/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
