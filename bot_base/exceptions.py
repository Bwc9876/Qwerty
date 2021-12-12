class SettingsInvalidError(ValueError):
    pass


class CogError(Exception):
    pass


class ImproperlyConfiguredCogError(CogError):
    pass


class NoCogDataError(CogError):
    pass
