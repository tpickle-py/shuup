from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.http.response import JsonResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from shuup.core.shop_provider import get_shop
from shuup.utils.django_compat import MiddlewareMixin, force_text
from shuup.utils.excs import ExceptionalResponse, Problem


class ExceptionMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if isinstance(exception, ExceptionalResponse):
            return exception.response

        if isinstance(exception, (ValidationError, Problem)):
            status_code = 400
            if request.is_ajax():
                return JsonResponse(
                    {
                        "error": force_text(exception),
                        "code": getattr(exception, "code", None),
                    },
                    status=status_code,
                )
            return render(
                request,
                self._get_problem_templates(request),
                status=status_code,
                context={
                    "title": getattr(exception, "title", None) or _("Error!"),
                    "message": exception.message,
                    "exception": exception,
                },
            )

    def _get_problem_templates(self, request):
        templates = []
        try:
            app_name = force_text(request.resolver_match.app_name)
            namespace = force_text(request.resolver_match.namespace)
            templates.extend(
                [
                    f"{app_name}/problem.jinja",
                    "{}/problem.jinja".format(app_name.replace("_", "/")),
                    f"{namespace}/problem.jinja",
                    "{}/problem.jinja".format(namespace.replace("_", "/")),
                ]
            )
        except (AttributeError, NameError):  # No resolver match? :(
            pass
        templates.extend(
            [
                "shuup/front/problem.jinja",
                "problem.jinja",
                "problem.html",
            ]
        )
        return templates


class ShuupMiddleware(MiddlewareMixin):
    """
    Handle Shuup specific tasks for each request and response.

    * Sets the current shop according to the host name
      ``request.shop`` : :class:`shuup.core.models.Shop`
          Currently active Shop.
    """

    def process_request(self, request):
        request.shop = get_shop(request)

        if not request.shop:
            raise ImproperlyConfigured(_("No such shop is configured."))
