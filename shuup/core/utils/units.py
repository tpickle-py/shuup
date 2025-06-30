from django.conf import settings


def get_shuup_volume_unit():
    """
    Return the volume unit that Shuup should use.

    :rtype: str
    """
    return f"{settings.SHUUP_LENGTH_UNIT}3"
