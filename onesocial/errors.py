class OneSocialError(Exception):
    """
    Базовый класс для ошибок OneSocial.

    code - код ошибки, str или None.
    message - описание ошибки, str.
    """
    def __init__(self, message, code=None):
        self.code = code
        self.message = message

    def __str__(self):
        if self.code:
            return "{}: {}".format(self.code, self.message)
        else:
            return self.message


class OneSocialOAuthError(OneSocialError):
    """
    Ошибка входа через соцсети.

    code - код ошибки, str или None.
    message - описание ошибки, str.
    """
    pass


class OneSocialAPIError(OneSocialError):
    """
    Ошибка API OneSocial (кроме API входа через соцсети).

    code - код ошибки, str или None.
    message - описание ошибки, str.
    """
    pass
