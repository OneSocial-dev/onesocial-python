from typing import Optional
from urllib.parse import urlencode

import requests

from .errors import OneSocialOAuthError


class TokenGrant:
    """
    Объект, содержащий токен доступа, выданный OneSocial, и его параметры.

    access_token - токен доступа, str.
    expires_in - срок действия токена с момента выдачи в секундах, int.
    """

    def __init__(self, *, access_token, token_type, expires_in):
        self.access_token = access_token
        self.token_type = token_type
        self.expires_in = expires_in


class OAuth:
    """
    Класс OAuth позволяет работать с API входа через соцсети OneSocial.

    Подробная документация: https://onesocial.dev/panel/docs/sociallogin/
    """

    CODE = 'code'
    TOKEN = 'token'

    def __init__(self, *, client_id=None, client_secret=None):
        """
        Client ID и Client Secret можно получить на странице настроек входа
        через соцсети: https://onesocial.dev/panel/oauthkeys/index/
        """
        self.client_id = client_id
        self.client_secret = client_secret

    def init(
                self, *,
                network: str = None,
                response_type: str = None,
                redirect_uri: str = None,
                state: Optional[str] = None,
            ) -> str:
        """
        Первый шаг в процессе аутентификации пользователя. Этот метод
        возвращает URL страницы, на которую следует направить пользователя
        для запуска аутентификации.

        network - идентификатор соцсети, str.
            См. список поддерживаемых соцсетей:
            https://onesocial.dev/panel/docs/sociallogin/#networks
        response_type - OAuth.CODE или OAuth.TOKEN.
            Этот параметр определяет режим работы OAuth. Для сайтов следует
            использовать OAuth.CODE. См. описание различий между двумя
            режимами:
            https://onesocial.dev/panel/docs/sociallogin/#modes
        redirect_uri - URI, на который следует перенаправить пользователя после
            авторизации, str. Домен этого URI должен быть указан в списке
            доменов в настройках пары ключей Client ID / Client Secret.
        state - любая произвольная строка, опционально, str. OneSocial
            скопирует ее в redirect_uri.

        Возвращает URI страницы запуска аутентификации, str.
        """
        url = 'https://onesocial.dev/api/sociallogin/init/{}/'.format(network)

        query = {
            'client_id': self.client_id,
            'response_type': response_type,
            'redirect_uri': redirect_uri,
        }

        if state:
            query['state'] = state

        return url + '?' + urlencode(query)

    def token(
                self, *,
                code: str = None,
                redirect_uri: str = None,
            ) -> TokenGrant:
        """
        Запрашивает токена доступа по коду авторизации.

        code - код авторизации, str.
        redirect_uri - Redirect URI, который был передан в метод init при
            запуске аутентификации.

        Возвращает объект TokenGrant.
        """
        resp = requests.post('https://onesocial.dev/api/sociallogin/token/', {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_secret': self.client_secret,
        })

        if resp.status_code < 200 or resp.status_code > 299:
            try:
                resp_json = resp.json()
                error = resp_json['error']
                error_description = resp_json['error_description']
            except ValueError:
                error = None
                error_description = resp.text

            raise OneSocialOAuthError(error_description, code=error)

        resp_json = resp.json()

        return TokenGrant(
            access_token=resp_json['access_token'],
            token_type=resp_json['token_type'],
            expires_in=resp_json['expires_in'],
        )
