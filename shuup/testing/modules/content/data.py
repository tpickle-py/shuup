from django.utils.translation import gettext_lazy as _

ABOUT_US_KEY = "about_us"
PRIVACY_POLICY_KEY = "privacy_policy"
TERMS_AND_CONDITIONS_KEY = "terms_conditions"
REFUND_POLICY_KEY = "refund_policy"

CMS_PAGES = {
    ABOUT_US_KEY: {
        "name": _("About Us"),
        "template": "shuup/admin/content/data/about_us.jinja",
    },
    PRIVACY_POLICY_KEY: {
        "name": _("Privacy Policy"),
        "template": "shuup/admin/content/data/privacy_policy.jinja",
    },
    TERMS_AND_CONDITIONS_KEY: {
        "name": _("Terms and Conditions"),
        "template": "shuup/admin/content/data/terms_and_conditions.jinja",
    },
    REFUND_POLICY_KEY: {
        "name": _("Refund Policy"),
        "template": "shuup/admin/content/data/refund_policy.jinja",
    },
}

FOOTER_TEMPLATE = "shuup/admin/content/data/footer.jinja"

ORDER_CONFIRMATION = {
    "subject": _("{{ order.shop }} - Order {{ order.identifier }} Received"),
    "content_type": "html",
    "body_template": "shuup/admin/content/data/order_confirmation.jinja",
}
