

from django.utils.translation import ugettext_lazy as _

from shuup.admin.base import Section


class MockContactSection(Section):
    identifier = "contact_mock_section"
    name = _("mock section title")
    icon = "fa-globe"
    template = "shuup_testing/_contact_mock_section.jinja"
    order = 9

    @classmethod
    def visible_for_object(cls, contact, request=None):
        return True

    @classmethod
    def get_context_data(cls, contact, request=None):
        context = {}
        context["mock_context"] = "mock section context data"
        return context
