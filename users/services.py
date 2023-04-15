from .models import  User, UserAdditionalInfo
import requests, logging

logger = logging.getLogger('__name__')

def signup_user(self, request):
    """Регистрация пользователя"""

    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    userinfo = serializer.validated_data.pop('userinfo')
    userinfo['user'] = User.objects.create_user(**serializer.validated_data)
    UserAdditionalInfo.objects.create(**userinfo)


def advanced_get_request(url, timeout):
    _response = {
        'response': None,
        'error': False,
        'error_message': None
    }

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.RequestException as err:
        logger.error(msg={'Another Error': err})
        _response['error'] = True
        _response['error_message'] = err
        return _response
    except requests.exceptions.HTTPError as errh:
        logger.error(msg={'Http Error': errh})
        _response['error'] = True
        _response['error_message'] = errh
        return _response
    except requests.exceptions.ConnectionError as errc:
        logger.error(msg={'Error Connecting': errc})
        _response['error'] = True
        _response['error_message'] = errc
        return _response
    except requests.exceptions.Timeout as errt:
        logger.error(msg={'Timeout Error': errt})
        _response['error'] = True
        _response['error_message'] = errt
        return _response

    _response['response'] = response
    return _response
