from django.utils.timezone import now

from .models import SavedViewConfig, SavedViewConfigStatus


def bump_xtheme_cache(*args, **kwargs):
    SavedViewConfig.objects.filter(status=SavedViewConfigStatus.PUBLIC).update(modified_on=now())
