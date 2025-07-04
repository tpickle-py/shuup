from django.http.response import HttpResponseRedirect
from django.views.generic.base import TemplateView

import shuup
from shuup.admin.dashboard import get_activity
from shuup.admin.dashboard.blocks import DashboardBlock
from shuup.admin.module_registry import get_modules
from shuup.admin.shop_provider import get_shop
from shuup.admin.utils.permissions import get_missing_permissions
from shuup.admin.utils.tour import is_tour_complete
from shuup.admin.utils.wizard import setup_wizard_complete
from shuup.core.telemetry import try_send_telemetry
from shuup.utils.django_compat import reverse


class DashboardView(TemplateView):
    template_name = "shuup/admin/dashboard/dashboard.jinja"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["version"] = shuup.__version__
        context["notifications"] = notifications = []
        context["blocks"] = blocks = []
        for module in get_modules():
            if not get_missing_permissions(self.request.user, module.get_required_permissions()):
                notifications.extend(module.get_notifications(request=self.request))
                blocks.extend(module.get_dashboard_blocks(request=self.request))

        # sort blocks by sort order and size, trying to make them fit better
        blocks.sort(key=lambda block: (block.sort_order, DashboardBlock.SIZES.index(block.size)))
        context["activity"] = get_activity(request=self.request)
        context["tour_key"] = "dashboard"
        context["tour_complete"] = is_tour_complete(get_shop(self.request), "dashboard", user=self.request.user)
        return context

    def get(self, request, *args, **kwargs):
        try_send_telemetry(request)
        if not setup_wizard_complete(request):
            return HttpResponseRedirect(reverse("shuup_admin:wizard"))
        elif request.shop.maintenance_mode:
            return HttpResponseRedirect(reverse("shuup_admin:home"))
        return super().get(request, *args, **kwargs)
