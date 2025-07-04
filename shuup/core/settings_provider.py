from django.conf import settings

from shuup.apps.provides import get_provide_objects


class BaseSettingsProvider:
    provided_settings = []

    def offers(self, setting_key):
        return bool(setting_key in self.provided_settings)

    def get_setting_value(self, setting_key):
        return None


class ShuupSettings:
    @classmethod
    def get_setting(cls, setting_key):
        for provider_cls in get_provide_objects("shuup_settings_provider"):
            provider = provider_cls()
            if provider.offers(setting_key):
                return provider.get_setting_value(setting_key)
        return getattr(settings, setting_key)
