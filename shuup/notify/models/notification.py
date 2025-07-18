from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from enumfields import EnumIntegerField
from jsonfield.fields import JSONField

from shuup.core.fields import InternalIdentifierField
from shuup.notify.enums import Priority, RecipientType
from shuup.utils.django_compat import NoReverseMatch, is_anonymous, reverse


class NotificationManager(models.Manager):
    def for_user(self, user):
        """
        :type user: django.contrib.auth.models.AbstractUser
        """
        if not (user and not is_anonymous(user)):
            return self.none()

        q = Q(recipient_type=RecipientType.SPECIFIC_USER) & Q(recipient=user)

        if getattr(user, "is_superuser", False):
            q |= Q(recipient_type=RecipientType.ADMINS)

        return self.filter(q)

    def unread_for_user(self, user):
        return self.for_user(user).exclude(marked_read=True)


class Notification(models.Model):
    """
    A model for persistent notifications to be shown in the admin, etc.
    """

    shop = models.ForeignKey(on_delete=models.CASCADE, to="shuup.Shop", verbose_name=_("shop"))
    recipient_type = EnumIntegerField(RecipientType, default=RecipientType.ADMINS, verbose_name=_("recipient type"))
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        related_name="+",
        on_delete=models.SET_NULL,
        verbose_name=_("recipient"),
    )
    created_on = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=_("created on"))
    message = models.CharField(max_length=140, editable=False, default="", verbose_name=_("message"))
    identifier = InternalIdentifierField(unique=False)
    priority = EnumIntegerField(Priority, default=Priority.NORMAL, db_index=True, verbose_name=_("priority"))
    _data = JSONField(blank=True, null=True, editable=False, db_column="data")

    marked_read = models.BooleanField(db_index=True, editable=False, default=False, verbose_name=_("marked read"))
    marked_read_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        editable=False,
        related_name="+",
        on_delete=models.SET_NULL,
        verbose_name=_("marked read by"),
    )
    marked_read_on = models.DateTimeField(null=True, blank=True, verbose_name=_("marked read on"))

    objects = NotificationManager()

    def __init__(self, *args, **kwargs):
        url = kwargs.pop("url", None)
        super().__init__(*args, **kwargs)
        if url:
            self.url = url

    def save(self, *args, **kwargs):
        if self.recipient_type == RecipientType.SPECIFIC_USER and not self.recipient_id:
            raise ValueError("Error! With `RecipientType.SPECIFIC_USER`, recipient is required.")
        super().save(*args, **kwargs)

    def mark_read(self, user):
        if self.marked_read:
            return False
        self.marked_read = True
        self.marked_read_by = user
        self.marked_read_on = now()
        self.save(update_fields=("marked_read", "marked_read_by", "marked_read_on"))
        return True

    @property
    def is_read(self):
        return self.marked_read

    @property
    def data(self):
        if not self._data:
            self._data = {}
        return self._data

    @property
    def url(self):
        url = self.data.get("_url")
        if isinstance(url, dict):
            return reverse(**url)
        return url

    @url.setter
    def url(self, value):
        if self.pk:
            raise ValueError("Error! URL can't be set on a saved notification.")
        self.data["_url"] = value

    def set_reverse_url(self, **reverse_kwargs):
        if self.pk:
            raise ValueError("Error! URL can't be set on a saved notification.")

        try:
            reverse(**reverse_kwargs)
        except NoReverseMatch as err:  # pragma: no cover
            raise ValueError("Error! Invalid reverse URL parameters.") from err

        self.data["_url"] = reverse_kwargs
