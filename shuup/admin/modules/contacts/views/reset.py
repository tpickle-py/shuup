from django.utils.translation import gettext_lazy as _

from shuup.admin.modules.contacts.utils import check_contact_permission
from shuup.admin.modules.users.views.password import UserResetPasswordView
from shuup.admin.utils.urls import get_model_url
from shuup.core.models import Contact
from shuup.utils.excs import Problem


class ContactResetPasswordView(UserResetPasswordView):
    def get_contact(self):
        contact = Contact.objects.get(pk=self.kwargs[self.pk_url_kwarg])
        check_contact_permission(self.request, contact)
        return contact

    def get_object(self, queryset=None):
        contact = self.get_contact()
        user = getattr(contact, "user", None)
        if not user:
            raise Problem(_("The contact does not have an associated user."))
        return user

    def get_success_url(self):
        return get_model_url(self.get_contact())
