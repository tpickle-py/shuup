import parler.models
import six
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.managers import TranslatableManager, TranslatableQuerySet
from polymorphic.base import PolymorphicModelBase
from polymorphic.managers import PolymorphicManager, PolymorphicQuerySet
from polymorphic.models import PolymorphicModel

from shuup.utils import text
from shuup.utils.django_compat import force_text


class RecursionSafeForeignKey(models.ForeignKey):
    """
    Custom ForeignKey that prevents infinite recursion in field comparisons.

    The recursion issue occurs when Django's polymorphic queries trigger field comparisons
    that create infinite loops during deletion cascades and complex queries.
    """

    def __eq__(self, other):
        # Simple comparison based on field attributes to prevent recursion
        if not isinstance(other, models.ForeignKey):
            return False
        return (
            self.name == getattr(other, "name", None)
            and self.related_model == getattr(other, "related_model", None)
            and type(self) == type(other)
        )

    def __hash__(self):
        # Ensure consistent hashing for field comparisons
        try:
            return hash((type(self), self.name, str(self.related_model)))
        except (TypeError, AttributeError):
            # Fallback if any attribute causes issues
            return hash((type(self), id(self)))

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"


class ShuupModel(models.Model):
    """
    Shuup Model.
    """

    identifier_attr = "identifier"

    def __repr__(self):
        identifier = getattr(self, self.identifier_attr, None)
        if identifier:
            identifier_suf = f"-{text.force_ascii(identifier)}"
        else:
            identifier_suf = ""
        return f"<{type(self).__name__}:{self.pk}{identifier_suf}>"

    class Meta:
        abstract = True


class TranslatableShuupModel(ShuupModel, parler.models.TranslatableModel):
    name_attr = "name"

    def __str__(self):
        name = self.safe_translation_getter(self.name_attr, any_language=True)
        if name is not None:
            # Ensure no lazy objects are returned
            name = force_text(name)
        if not name:
            # Ensure no empty value is returned
            identifier = getattr(self, self.identifier_attr, None)
            suffix = f" {identifier}" if identifier else ""
            if self._meta.verbose_name:
                return f"{suffix}{self._meta.verbose_name}"
            return f"{suffix}{type(self).__name__}"
        return name

    class Meta:
        abstract = True


class PolymorphicShuupModel(PolymorphicModel, ShuupModel):
    """
    Shuup polymorphic model with recursion-safe polymorphic type field.
    """

    # Override the polymorphic_ctype field with our recursion-safe version
    polymorphic_ctype = RecursionSafeForeignKey(
        "contenttypes.ContentType",
        null=True,
        editable=False,
        on_delete=models.CASCADE,
        related_name="polymorphic_%(app_label)s.%(class)s_set+",
    )

    class Meta:
        abstract = True


class _PolyTransQuerySet(TranslatableQuerySet, PolymorphicQuerySet):
    pass


class _PolyTransManager(PolymorphicManager, TranslatableManager):
    queryset_class = _PolyTransQuerySet


class PolyTransModelBase(PolymorphicModelBase):
    def get_inherited_managers(self, attrs):
        parent = super()
        result = []
        for base_name, key, manager in parent.get_inherited_managers(attrs):
            if base_name == "PolymorphicModel":
                model = manager.model
                if key == "objects":
                    manager = _PolyTransManager()
                    manager.model = model
                elif key == "base_objects":
                    manager = parler.models.TranslatableManager()
                    manager.model = model
            result.append((base_name, key, manager))
        return result


class PolymorphicTranslatableShuupModel(
    six.with_metaclass(PolyTransModelBase, PolymorphicShuupModel, TranslatableShuupModel)
):
    objects = _PolyTransManager()

    class Meta:
        abstract = True


class ChangeProtected:
    protected_fields = None
    unprotected_fields = []
    change_protect_message = _("The following fields are protected and can not be changed.")

    def clean(self, *args, **kwargs):
        super().clean(*args, **kwargs)
        if self.pk:
            changed_protected_fields = self._get_changed_protected_fields()
            if changed_protected_fields and self._are_changes_protected():
                message = "{change_protect_message}: {fields}".format(
                    change_protect_message=self.change_protect_message,
                    fields=", ".join(sorted(changed_protected_fields)),
                )
                raise ValidationError(message)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def _are_changes_protected(self):
        """
        Check if changes of this object should be protected.

        This can be overridden in the subclasses to make it possible to
        avoid change protection e.g. if object is not in use yet.

        The base class implementation just returns True.
        """
        return True

    def _get_changed_protected_fields(self):
        if self.protected_fields is not None:
            protected_fields = self.protected_fields
        else:
            protected_fields = [
                x.name for x in self._meta.get_fields() if not x.is_relation and x.name not in self.unprotected_fields
            ]
        in_db = type(self).objects.get(pk=self.pk)
        return [field for field in protected_fields if getattr(self, field) != getattr(in_db, field)]
