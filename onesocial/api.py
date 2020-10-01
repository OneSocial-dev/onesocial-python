from typing import Optional

import requests

from .errors import OneSocialAPIError


class BaseAPI:
    def __init__(self, *, access_token):
        self.access_token = access_token

    def _raise_if_error(self, resp):
        if resp.status_code < 200 or resp.status_code > 299:
            try:
                resp_json = resp.json()
                error_code = resp_json['error_code']
                error_description = resp_json['error_description']
            except ValueError:
                error_code = None
                error_description = resp.text

            raise OneSocialAPIError(error_description, code=error_code)

    def _get_authorization_headers(self):
        return {
            'Authorization': 'Bearer {}'.format(self.access_token),
        }


class UserProfile:
    """
    Профиль пользователя социальной сети.

    Связка network и uid уникальна для каждого аккаунта во всех соцсетях.

    Обязательные поля:

    network - идентификатор соцсети, str.
        См. список поддерживаемых соцсетей:
        https://onesocial.dev/panel/docs/sociallogin/#networks
    uid - ID аккаунта в соцсети, str.
    username - латинизированный юзернейм, который можно использовать
        на сайте, str.
    human_name - Имя Фамилия, str. Если соцсеть не предоставляет имя и фамилию
        пользователя, это поле повторяет username.

    Необязательные поля:

    email - email, str. Может отсутствовать, если не указан в аккаунте
        пользователя или если пользователя запретил доступ к своему email.
    picture - URL аватара, str. Может отсутствовать, если в профиле
        не указан аватар.
    """
    def __init__(
                self, *,
                network: str = None,
                uid: str = None,
                username: str = None,
                human_name: str = None,
                email: Optional[str] = None,
                picture: Optional[str] = None,
            ):
        self.network = network
        self.uid = uid
        self.username = username
        self.human_name = human_name
        self.email = email
        self.picture = picture


class UsersAPI(BaseAPI):
    def me(self):
        """
        Возвращает профиль аккаунта, под которым авторизован клиент.

        https://onesocial.dev/panel/docs/users-api/#get-me
        """
        resp = requests.get(
            'https://onesocial.dev/api/users/me/',
            headers=self._get_authorization_headers(),
        )
        self._raise_if_error(resp)

        resp_json = resp.json()
        return UserProfile(
            network=resp_json['network'],
            uid=resp_json['uid'],
            username=resp_json['username'],
            human_name=resp_json['human_name'],
            email=resp_json['email'],
            picture=resp_json['picture'],
        )
