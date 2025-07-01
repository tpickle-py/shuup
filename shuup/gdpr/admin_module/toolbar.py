from django.utils.translation import ugettext_lazy as _

from shuup.admin.toolbar import PostActionButton
from shuup.utils.django_compat import reverse


class AnonymizeContactToolbarButton(PostActionButton):
    def __init__(self, object, **kwargs):
        kwargs["icon"] = "fa fa-user-times"
        kwargs["text"] = _("Anonymize")
        kwargs["extra_css_class"] = "dropdown-item"
        kwargs["confirm"] = _(
            "This action will replace all contact personal data with random values making it "
            "impossible to be identified. The account will also be deactivated and any "
            "pending order(s) will be canceled. Are you sure?"
        )
        kwargs["name"] = "download"
        kwargs["value"] = "1"
        kwargs["post_url"] = reverse("shuup_admin:gdpr.anonymize", kwargs={"pk": object.pk})
        super().__init__(**kwargs)

    @staticmethod
    def visible_for_object(object):
        return True


class DownloadDataToolbarButton(PostActionButton):
    def __init__(self, object, **kwargs):
        kwargs["icon"] = "fa fa-cube"
        kwargs["text"] = _("Download data")
        kwargs["name"] = "download"
        kwargs["value"] = "1"
        kwargs["extra_css_class"] = "dropdown-item"
        kwargs["post_url"] = reverse("shuup_admin:gdpr.download_data", kwargs={"pk": object.pk})
        super().__init__(**kwargs)

    @staticmethod
    def visible_for_object(object):
        return True
