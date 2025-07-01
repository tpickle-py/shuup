from django.conf import settings


def has_installed(app):
    """
    Returns whether the `app` is installed in Django,
    it means, it is in `INSTALLED_APPS` settings

    :param app: the application identifier like `shuup.front`
    :type app: str
    """
    return app in getattr(settings, "INSTALLED_APPS", [])
