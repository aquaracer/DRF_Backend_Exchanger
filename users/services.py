import requests, logging
from rest_framework.request import Request

from .models import User, UserAdditionalInfo

logger = logging.getLogger('__name__')


def signup_user(self, request: Request) -> None:
    """Регистрация пользователя"""

    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    userinfo = serializer.validated_data.pop('userinfo')
    userinfo['user'] = User.objects.create_user(**serializer.validated_data)
    UserAdditionalInfo.objects.create(**userinfo)


def advanced_get_request(url: str, timeout: int) -> dict:
    """Get-запрос, c подключенным логгированием и покрытый исключениями"""

    _response = {
        'response': None,
        'error': False,
        'error_message': None
    }

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.RequestException as error_request:
        logger.error(msg={'Another Error': error_request})
        _response['error'] = True
        _response['error_message'] = error_request
        return _response
    except requests.exceptions.HTTPError as error_http:
        logger.error(msg={'Http Error': error_http})
        _response['error'] = True
        _response['error_message'] = error_http
        return _response
    except requests.exceptions.ConnectionError as error_connection:
        logger.error(msg={'Error Connecting': error_connection})
        _response['error'] = True
        _response['error_message'] = error_connection
        return _response
    except requests.exceptions.Timeout as error_timeout:
        logger.error(msg={'Timeout Error': error_timeout})
        _response['error'] = True
        _response['error_message'] = error_timeout
        return _response

    _response['response'] = response
    return _response
