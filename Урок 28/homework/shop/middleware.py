import logging
import time

from django.http import HttpRequest, HttpResponse

logger = logging.getLogger("shop")


class RequestTimeMiddleware:
    """Час запиту."""

    def __init__(self, get_response) -> None:
        """Ініціалізація."""
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Обробка запиту."""
        start = time.time()
        response = self.get_response(request)
        duration = time.time() - start
        logger.info(
            "%s %s %s %s %.3f с",
            request.user,
            request.method,
            request.path,
            response.status_code,
            duration,
        )
        response["X-Request-Time"] = f"{duration:.3f}"
        return response
