from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = "shuup/front/index.jinja"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # TODO: dispatch_hook("get_context_data", view=self, context=context)
        return context
