import time
import logging
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.http import HttpResponseTooManyRequests

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware for logging request information.
    """
    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            logger.info(
                f"Request: {request.method} {request.path} "
                f"Status: {response.status_code} "
                f"Duration: {duration:.2f}s"
            )
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Middleware for rate limiting requests.
    """
    def process_request(self, request):
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return None

        # Get the client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        # Create a unique key for the user/IP
        key = f'rate_limit:{ip}'

        # Get the current count
        count = cache.get(key, 0)

        # Check if the rate limit is exceeded
        if count >= settings.RATE_LIMIT:
            return HttpResponseTooManyRequests()

        # Increment the count
        cache.set(key, count + 1, settings.RATE_LIMIT_WINDOW)

        return None


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware for adding security headers to responses.
    """
    def process_response(self, request, response):
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response['Content-Security-Policy'] = "default-src 'self'"
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        return response


class ExceptionLoggingMiddleware(MiddlewareMixin):
    """
    Middleware for logging exceptions.
    """
    def process_exception(self, request, exception):
        logger.error(
            f"Exception occurred: {exception}",
            exc_info=True,
            extra={
                'request_method': request.method,
                'request_path': request.path,
                'request_user': getattr(request.user, 'username', None),
            }
        )
        return None


class CacheControlMiddleware(MiddlewareMixin):
    """
    Middleware for adding cache control headers.
    """
    def process_response(self, request, response):
        if request.method == 'GET':
            response['Cache-Control'] = 'public, max-age=31536000'
        else:
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        return response 