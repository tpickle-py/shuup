from django.http import JsonResponse
from django.views.generic import TemplateView, View


class MenuView(TemplateView):
    template_name = "shuup/admin/base/_main_menu.jinja"


class MenuToggleView(View):
    def post(self, request, *args, **kwargs):
        request.session["menu_open"] = not bool(request.session.get("menu_open", True))
        return JsonResponse({"success": True})
