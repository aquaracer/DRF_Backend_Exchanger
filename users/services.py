import logging
from typing import Any

import requests
from rest_framework import status

from common.exceptions import HTTPException

logger = logging.getLogger(__name__)


def get_api_response(url: str, timeout: int) -> dict[str, Any]:
    """Get-запрос, c подключенным логгированием и покрытый исключениями"""

    try:
        response = requests.get(url, timeout=timeout)
        return response.json()

    except requests.exceptions.HTTPError as error_http:
        status_code = error_http.response.status_code if error_http.response else None
        message = str(error_http)
        logger.error(f"HTTP Error: {status_code} - {message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message
        ) from error_http

    except requests.exceptions.ConnectionError as error_connection:
        message = str(error_connection)
        logger.error(f"Connection Error: {message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message
        ) from error_connection

    except requests.exceptions.Timeout as error_timeout:
        message = str(error_timeout)
        logger.error(f"Timeout Error: {message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message
        ) from error_timeout

    except Exception as error:
        message = str(error)
        logger.exception(f"Unexpected error: {message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message
        ) from error
