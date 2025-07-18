from django.conf import settings

from shuup.admin.form_part import FormPart, TemplatedFormDef
from shuup.admin.modules.categories.forms import CategoryBaseForm, CategoryProductForm
from shuup.core.models import Category


class CategoryBaseFormPart(FormPart):
    priority = -1000  # Show this first, no matter what

    def get_form_defs(self):
        yield TemplatedFormDef(
            "base",
            CategoryBaseForm,
            template_name="shuup/admin/categories/_edit_base_form.jinja",
            required=True,
            kwargs={
                "instance": self.object,
                "request": self.request,
                "languages": settings.LANGUAGES,
            },
        )

    def form_valid(self, form):
        rebuild = "parent" in form["base"].changed_data
        self.object = form["base"].save()
        if rebuild:
            Category.objects.rebuild()


class CategoryProductFormPart(FormPart):
    priority = 1
    name = "products"

    def get_form_defs(self):
        if not self.object.pk:
            return

        shop = self.request.shop
        yield TemplatedFormDef(
            self._get_form_name(shop),
            CategoryProductForm,
            template_name="shuup/admin/categories/_edit_products_form.jinja",
            required=True,
            kwargs={"shop": shop, "category": self.object},
        )

    def _get_form_name(self, shop):
        return f"{shop.pk}_{self.name}"

    def form_valid(self, form):
        for shop in self.object.shops.all():
            form_name = self._get_form_name(shop)
            if form_name in form.forms:
                form[self._get_form_name(shop)].save()
