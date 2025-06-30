import json

import jinja2
from django.conf import settings
from django_jinja import library

from shuup.compat import contextfunction
from shuup.gdpr.utils import get_active_consent_pages


class GDPRNamespace(object):
    def is_enabled(self, request, **kwargs):
        from shuup.gdpr.models import GDPRSettings

        return GDPRSettings.get_for_shop(request.shop).enabled

    def get_documents(self, request, **kwargs):
        return get_active_consent_pages(request.shop)

    @contextfunction
    def get_accepted_cookies(self, context, **kwargs):
        request = context["request"]
        if settings.SHUUP_GDPR_CONSENT_COOKIE_NAME in request.COOKIES:
            consent_cookies = request.COOKIES[settings.SHUUP_GDPR_CONSENT_COOKIE_NAME]
            return json.loads(consent_cookies).get("cookies")
        return []


library.global_function(name="gdpr", fn=GDPRNamespace())
