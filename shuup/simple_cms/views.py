from django.http import Http404
from django.http.response import HttpResponseRedirect
from django.utils.translation import get_language
from django.views.generic.detail import DetailView

from shuup.simple_cms.models import Page
from shuup.utils.django_compat import reverse


class PageView(DetailView):
    model = Page
    slug_field = "translations__url"
    slug_url_kwarg = "url"
    template_name = "shuup/simple_cms/page.jinja"
    context_object_name = "page"

    def get(self, request, *args, **kwargs):
        """
        Override normal get method to return correct page based on the active language and slug

        Cases:
            1. Page is not found: `raise Http404()` like django would.
            2. No translation in active language for the page: `raise Http404()`.
            3. Translation was found for active language, but the url doesn't match given url:
                `return HttpResponseRedirect` to the active languages url.
            4. If none of the upper matches: render page normally.
        """

        # get currently active language
        self.object = self.get_object()
        # set the chosen template
        if not self.object.has_translation(get_language()):
            # Page hasn't been translated into the current language; that's always a 404
            raise Http404()

        self.object.set_current_language(get_language())
        if self.object.url != self.kwargs[self.slug_url_kwarg]:  # Wrong URL, hm!
            return HttpResponseRedirect(reverse("shuup:cms_page", kwargs={"url": self.object.url}))

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_template_names(self):
        object = self.get_object()
        return [object.template_name]

    def get_queryset(self):
        if getattr(self.request.user, "is_superuser", False):
            # Superusers may see all pages despite their visibility status
            return self.model.objects.for_shop(self.request.shop).filter(deleted=False)
        return self.model.objects.visible(self.request.shop, user=self.request.user)
