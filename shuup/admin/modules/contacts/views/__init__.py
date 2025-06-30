from .detail import ContactDetailView
from .edit import ContactEditView
from .list import ContactListView
from .mass_edit import ContactGroupMassEditView, ContactMassEditView
from .reset import ContactResetPasswordView

__all__ = [
    "ContactListView",
    "ContactDetailView",
    "ContactResetPasswordView",
    "ContactEditView",
    "ContactGroupMassEditView",
    "ContactMassEditView",
]
