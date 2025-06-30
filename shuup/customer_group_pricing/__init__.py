from django.utils.translation import ugettext_lazy as _

import shuup.apps


# TODO: Document how to create custom pricing modules (Refs SHUUP-514)
class CustomerGroupPricingAppConfig(shuup.apps.AppConfig):
    name = __name__
    verbose_name = _("Shuup Customer Group Pricing")
    label = "shuup_customer_group_pricing"
    default_auto_field = "django.db.models.BigAutoField"
    provides = {
        "pricing_module": [__name__ + ".module:CustomerGroupPricingModule"],
        "discount_module": [__name__ + ".module:CustomerGroupDiscountModule"],
        "admin_product_form_part": [
            __name__ + ".admin_form_part:CustomerGroupPricingFormPart",
            __name__ + ".admin_form_part:CustomerGroupPricingDiscountFormPart",
        ],
    }

    def ready(self):
        # connect signals
        import shuup.customer_group_pricing.signal_handers  # noqa F401


default_app_config = __name__ + ".CustomerGroupPricingAppConfig"
