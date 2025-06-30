from django.conf import settings


def get_shuup_volume_unit():
    """
    Return the volume unit that Shuup should use.

    :rtype: str
    """
    return "{}3".format(settings.SHUUP_LENGTH_UNIT)
