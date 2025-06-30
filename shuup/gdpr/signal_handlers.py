from django.db.models.signals import post_save

from .models import GDPRSettings, get_setting


def handle_settings_post_save(sender, instance, **kwargs):
    get_setting.cache_clear()


post_save.connect(
    handle_settings_post_save,
    sender=GDPRSettings,
    dispatch_uid="shuup_gdpr:handle_settings_post_save",
)
