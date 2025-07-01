from django.template.loader import get_template
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from enumfields import Enum

from shuup.utils.django_compat import reverse


class DashboardItemSize(Enum):
    SMALL = 6
    MEDIUM = 9
    LARGE = 12


class DashboardItem:
    request = None
    template_name = "shuup/front/dashboard/dashboard_base.jinja"

    """
    Title shown in dashboard menu and in dashboard
    """
    title = _("Dashboard")

    """
    Sequence number of dashboard item
    """
    ordering = 0

    """
    The size of dashboard item block
    """
    size = DashboardItemSize.LARGE

    """
    Icon shown in menu and dashboard
    """
    icon = "fa fa-tachometer"

    """
    Text for dashboard

    If your dashboard item shows single object,
    `Edit` is just fine but if you are listing objects,
    `Show All` might be better.
    """
    view_text = _("Edit")

    _url = "shuup:dashboard"

    def __init__(self, request):
        self.request = request

    @property
    def url(self):
        return reverse(self._url)

    def get_context(self):
        """
        Get context for template

        This is usually overridden in subclasses.

        :return: Dict of context items
        :rtype: dict
        """
        return {"item": self, "request": self.request}

    def render(self):
        """
        Render the given template with context

        :return: Rendered template
        """
        template = get_template(self.template_name)
        return mark_safe(template.render(context=self.get_context()))

    @property
    def css_class(self):
        return f"col-md-{self.size}"  # type: ignore

    def show_on_menu(self):
        """
        Defines if the item is shown in the main dashboard menu

        :return: True or False if item should be shown in menu
        :rtype: bool
        """
        return True

    def show_on_dashboard(self):
        """
        Defines if the item is shown in dashboard

        :return: True or False if item should be shown in dashboard
        :rtype: bool
        """
        return True
