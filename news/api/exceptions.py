# news/api/exceptions.py
import logging

from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler

from ..services import DomainError

logger = logging.getLogger(__name__)


def _error_response(code, message, http_status):
    return Response(
        {'success': False, 'error': {'code': code, 'message': message}},
        status=http_status,
    )


def api_exception_handler(exc, context):
    """Every response the API sends back is either
    ``{"success": true, "data": ...}`` or
    ``{"success": false, "error": {"code": ..., "message": ...}}`` — never a
    raw Python exception message or traceback.
    """
    if isinstance(exc, DomainError):
        return _error_response('DOMAIN_RULE_VIOLATION', str(exc), status.HTTP_400_BAD_REQUEST)

    response = exception_handler(exc, context)
    if response is not None:
        code = getattr(exc, 'default_code', exc.__class__.__name__.upper())
        message = response.data.get('detail', 'Request could not be processed.') if isinstance(response.data, dict) else str(response.data)
        response.data = {'success': False, 'error': {'code': str(code).upper(), 'message': str(message)}}
        return response

    if isinstance(exc, Http404):
        return _error_response('NOT_FOUND', 'Resource not found.', status.HTTP_404_NOT_FOUND)

    # Anything else is unexpected: log it fully server-side, tell the client
    # nothing beyond "something went wrong".
    logger.exception("Unhandled API exception", exc_info=exc)
    return _error_response('INTERNAL_ERROR', 'An unexpected error occurred.', status.HTTP_500_INTERNAL_SERVER_ERROR)
