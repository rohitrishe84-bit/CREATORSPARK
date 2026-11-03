import time
import uuid
import logging

logger = logging.getLogger('creatorspark.requests')
logging.basicConfig(level=logging.INFO)

class RequestLoggingMiddleware:
    """
    Logs incoming HTTP requests and responses, tracking latency, status,
    and injecting an X-Request-ID correlation header.
    Never logs sensitive payloads, credentials, or session cookies.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
        request.request_id = request_id
        start_time = time.time()

        response = self.get_response(request)

        duration_ms = round((time.time() - start_time) * 1000, 2)
        response['X-Request-ID'] = request_id

        # Skip noisy static / favicon requests in standard logs
        if not request.path.startswith('/static/'):
            user_repr = f"user={request.user.id}" if request.user.is_authenticated else "anon"
            logger.info(
                f"[{request_id}] {request.method} {request.path} -> {response.status_code} "
                f"({duration_ms}ms) [{user_repr}]"
            )

        return response
