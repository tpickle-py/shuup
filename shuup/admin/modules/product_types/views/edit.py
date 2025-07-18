from django.utils.translation import gettext_lazy as _

from shuup.admin.forms.fields import ObjectSelect2MultipleField
from shuup.admin.toolbar import PostActionButton, get_default_edit_toolbar
from shuup.admin.utils.views import CreateOrUpdateView
from shuup.core.models import Attribute, ProductType
from shuup.utils.django_compat import reverse_lazy
from shuup.utils.multilanguage_model_form import MultiLanguageModelForm


class ProductTypeForm(MultiLanguageModelForm):
    attributes = ObjectSelect2MultipleField(
        model=Attribute,
        required=False,
        help_text=_(
            "Select attributes that go with your product type. These are defined in Products Settings - Attributes."
        ),
    )

    class Meta:
        model = ProductType
        exclude = ()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.instance.pk:
            choices = [(a.pk, a.name) for a in self.instance.attributes.all()]
            self.fields["attributes"].initial = [pk for pk, name in choices]

    def save(self, commit=True):
        obj = super().save(commit=commit)
        obj.attributes.clear()
        obj.attributes.set(self.cleaned_data["attributes"])
        return self.instance


class ProductTypeEditView(CreateOrUpdateView):
    model = ProductType
    form_class = ProductTypeForm
    template_name = "shuup/admin/product_types/edit.jinja"
    context_object_name = "product_type"

    def get_toolbar(self):
        product_type = self.get_object()
        save_form_id = self.get_save_form_id()
        delete_url = (
            reverse_lazy("shuup_admin:product_type.delete", kwargs={"pk": product_type.pk}) if product_type.pk else None
        )
        toolbar = get_default_edit_toolbar(self, save_form_id)
        if not delete_url:
            return toolbar
        toolbar.append(
            PostActionButton(
                post_url=delete_url,
                text=_("Delete"),
                icon="fa fa-trash",
                extra_css_class="btn-danger",
                confirm=_(
                    "Are you sure you wish to delete %s? Warrning: all related products will disappear "
                    "from storefront until new value for product type is set!"
                )
                % product_type,  # noqa
                required_permissions=(),
            )
        )
        return toolbar
