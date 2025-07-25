from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from enumfields import Enum
from enumfields.fields import EnumIntegerField
from filer.fields.image import FilerFileField

from shuup.core.fields import SeparatedValuesField, TaggedJSONField


class SnippetType:
    InlineJS = "inline_js"
    InlineCSS = "inline_css"
    InlineHTMLMarkup = "inline_html"
    InlineJinjaHTMLMarkup = "inline_jinja_html"


SnippetTypeChoices = [
    (SnippetType.InlineJS, _("Inline JavaScript")),
    (SnippetType.InlineCSS, _("Inline CSS")),
    (SnippetType.InlineHTMLMarkup, _("Inline HTML")),
    (SnippetType.InlineJinjaHTMLMarkup, _("Inline Jinja HTML")),
]


class SavedViewConfigQuerySet(models.QuerySet):  # doccov: ignore
    def appropriate(self, theme, shop, view_name, draft):
        """
        Get an "appropriate" `SavedViewConfig` for the parameters given.

        When draft mode is off:

        * A PUBLIC SavedViewConfig is returned, or a new one in CURRENT_DRAFT status.

        When draft mode is on:

        * A CURRENT_DRAFT SavedViewConfig is returned, if one exists.
        * If a PUBLIC SavedViewConfig exists, its data is copied into a new, unsaved CURRENT_DRAFT
          SavedViewConfig.

        :param theme: Theme instance.
        :type theme: shuup.xtheme.Theme
        :param view_name: View name string.
        :type view_name: str
        :param draft: Draft mode flag.
        :type draft: bool
        :return: SavedViewConfig (possibly not saved).
        :rtype: SavedViewConfig
        """
        svc_kwargs = {"theme_identifier": theme.identifier, "shop": shop, "view_name": view_name}
        svc_qs = SavedViewConfig.objects.filter(**svc_kwargs).order_by("-id")
        if draft:  # In draft mode? Try loading drafts first
            model = svc_qs.filter(status=SavedViewConfigStatus.CURRENT_DRAFT).first()
            if not model:  # No current draft?
                model = svc_qs.filter(status=SavedViewConfigStatus.PUBLIC).first()
                if model:  # "Copy" last public version to new draft and continue
                    model.pk = None
                    model.status = SavedViewConfigStatus.CURRENT_DRAFT
        else:  # Not in draft mode? Try loading a non-draft.
            model = svc_qs.filter(status=SavedViewConfigStatus.PUBLIC).first()

        if not model:  # Nothing loaded? Put ourselves in draft mode.
            model = SavedViewConfig(status=SavedViewConfigStatus.CURRENT_DRAFT, **svc_kwargs)
        return model


class SavedViewConfigStatus(Enum):
    """
    Stati for SavedViewConfigs.

    The lifecycle for SavedViewConfigs (SVCs) for a given (theme, view) pair is as follows:

    * Initially, there's zero SVCs.
    * When a placeholder layout is saved in edit mode, an SVC in the CURRENT_DRAFT status is
      saved.
    * When an SVC in CURRENT_DRAFT status is published, all other SVCs for the theme/view pair
      are "demoted" to being OLD_VERSIONs and the CURRENT_DRAFT SVC is promoted to being the
      PUBLIC one (and there should always be zero or one PUBLIC SavedViewConfigs per (theme, view) pair).
    * When an SVC in CURRENT_DRAFT status is reverted, it is simply deleted.
    * When an SVC has been published and edit mode is entered again, the current PUBLIC SVC
      is copied into a new CURRENT_DRAFT version.

    """

    CURRENT_DRAFT = 1
    OLD_VERSION = 2
    PUBLIC = 3

    class Labels:
        CURRENT_DRAFT = _("current draft")
        OLD_VERSION = _("old version")
        PUBLIC = _("public")


class SavedViewConfig(models.Model):
    theme_identifier = models.CharField(max_length=64, db_index=True, verbose_name=_("theme identifier"))
    shop = models.ForeignKey(
        on_delete=models.CASCADE,
        to="shuup.Shop",
        related_name="saved_views_config",
        null=True,
    )
    view_name = models.CharField(max_length=64, db_index=True, verbose_name=_("view name"))
    created_on = models.DateTimeField(auto_now_add=True, verbose_name=_("created on"))
    modified_on = models.DateTimeField(auto_now=True, editable=False, verbose_name=_("modified on"))
    status = EnumIntegerField(SavedViewConfigStatus, db_index=True, verbose_name=_("status"))
    _data = TaggedJSONField(db_column="data", default=dict, verbose_name=_("internal data"))
    objects = SavedViewConfigQuerySet.as_manager()

    @property
    def draft(self):
        return self.status == SavedViewConfigStatus.CURRENT_DRAFT

    def publish(self):
        if not self.draft:
            raise ValueError("Error! Unable to publish a non-draft view configuration.")
        self.__class__.objects.filter(
            shop=self.shop,
            theme_identifier=self.theme_identifier,
            view_name=self.view_name,
        ).update(status=SavedViewConfigStatus.OLD_VERSION)
        self.status = SavedViewConfigStatus.PUBLIC
        self.save()

    def revert(self):
        if not self.draft:
            raise ValueError("Error! Unable to revert a non-draft view configuration.")
        if self.pk:
            self.delete()

    def set_layout_data(self, layout_data_key, layout):
        if not layout:  # pragma: no cover
            self._data.setdefault("layouts", {}).pop(layout_data_key, None)
            return None
        if not self.draft:
            raise ValueError("Error! Unable to save things in non-draft mode.")
        if hasattr(layout, "serialize"):
            layout = layout.serialize()
        assert isinstance(layout, dict)
        self._data.setdefault("layouts", {})[layout_data_key] = layout

    def get_layout_data(self, layout_data_key):
        return self._data.get("layouts", {}).get(layout_data_key)

    def clear_layout_data(self, placeholder_name):
        if not self.draft:
            raise ValueError("Error! Unable to save things in non-draft mode")
        self._data.setdefault("layouts", {}).pop(placeholder_name, None)


class ThemeSettings(models.Model):
    theme_identifier = models.CharField(max_length=64, db_index=True, verbose_name=_("theme identifier"))
    shop = models.ForeignKey(
        on_delete=models.CASCADE,
        to="shuup.Shop",
        related_name="themes_settings",
        null=True,
    )
    active = models.BooleanField(db_index=True, default=False, verbose_name=_("active"))
    data = TaggedJSONField(db_column="data", default=dict, verbose_name=_("data"))

    class Meta:
        unique_together = ("theme_identifier", "shop")

    def activate(self):
        self.__class__.objects.filter(shop=self.shop).update(active=False)
        self.active = True
        self.save()

    def get_setting(self, key, default=None):
        return self.data.setdefault("settings", {}).get(key, default)

    def get_settings(self):
        return self.data.get("settings", {}).copy()

    def update_settings(self, update_values):
        self.data.setdefault("settings", {}).update(update_values)
        self.save()

    def __str__(self):
        return _("Theme configuration for %s") % self.theme_identifier


class Font(models.Model):
    shop = models.ForeignKey(
        "shuup.Shop",
        verbose_name=_("Shop"),
        related_name="admin_fonts",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=128, verbose_name=_("name"), help_text=_("Font family name"))
    css_value = models.CharField(
        max_length=128,
        blank=True,
        verbose_name=_("Font Family CSS Property"),
        help_text=_("(Optional) Input css font family property directly. Ex: font-family: Roboto;"),
    )

    woff = FilerFileField(
        verbose_name=_("WOFF Font"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="xtheme_woff_fonts",
    )
    woff2 = FilerFileField(
        verbose_name=_("WOFF2 Font"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="xtheme_woff2_fonts",
    )
    ttf = FilerFileField(
        verbose_name=_("TTF font"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="xtheme_ttf_fonts",
    )
    svg = FilerFileField(
        verbose_name=_("SVG font"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="xtheme_svg_fonts",
    )
    eot = FilerFileField(
        verbose_name=_("EOT font"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="xtheme_eot_fonts",
    )

    class Meta:
        verbose_name = _("Font Family")
        verbose_name_plural = _("Font Families")
        unique_together = ("shop", "name")

    def __str__(self):
        return self.name

    def get_font_sources(self):
        font_sources = []

        if self.eot:
            font_sources.append(f"url('{self.eot.url}?#iefix') format('embedded-opentype')")
        if self.woff:
            font_sources.append(f"url('{self.woff.url}') format('woff')")
        if self.woff2:
            font_sources.append(f"url('{self.woff2.url}') format('woff2')")
        if self.ttf:
            font_sources.append(f"url('{self.ttf.url}') format('truetype')")
        if self.svg:
            font_sources.append(f"url('{self.svg.url}#svgFontName') format('svg')")

        return font_sources


class AdminThemeSettings(models.Model):
    shop = models.OneToOneField(on_delete=models.CASCADE, to="shuup.Shop", related_name="admin_theme_settings")
    primary_color = models.CharField(
        max_length=7,
        default="#07B0F2",
        verbose_name=_("primary color"),
        validators=[MinLengthValidator(7)],
        blank=True,
    )
    secondary_color = models.CharField(
        max_length=7,
        default="#041E40",
        verbose_name=_("secondary color"),
        validators=[MinLengthValidator(7)],
        blank=True,
    )
    text_color = models.CharField(
        max_length=7,
        default="#384850",
        verbose_name=_("text color"),
        validators=[MinLengthValidator(7)],
        blank=True,
    )
    success_color = models.CharField(
        max_length=7,
        default="#27ae60",
        verbose_name=_("success color"),
        validators=[MinLengthValidator(7)],
        blank=True,
    )
    danger_color = models.CharField(
        max_length=7,
        default="#e74c3c",
        verbose_name=_("danger color"),
        validators=[MinLengthValidator(7)],
        blank=True,
    )
    admin_header_font = models.ForeignKey(
        Font,
        null=True,
        blank=True,
        related_name="admin_header_font",
        on_delete=models.SET_NULL,
    )
    admin_body_font = models.ForeignKey(
        Font,
        null=True,
        blank=True,
        related_name="admin_body_font",
        on_delete=models.SET_NULL,
    )
    base_font_size = models.CharField(max_length=10, default="0.9rem", verbose_name=_("base font size"), blank=True)
    active = models.BooleanField(db_index=True, default=False, verbose_name=_("active"))

    def __str__(self):
        return _("Admin Theme configuration for %s") % self.shop

    def colored_name(self, field):
        return format_html(
            '<span style="color: ;">{}</span>',
            self[field],
        )

    @classmethod
    def object(cls):
        return cls._default_manager.all().first()

    def save(self, *args, **kwargs):
        self.pk = self.id = 1
        return super().save(*args, **kwargs)


class Snippet(models.Model):
    """
    Inject snippet code globally filtering by themes if configured.
    """

    name = models.CharField(max_length=50, verbose_name=_("snippet name"), default=_("Untitled"))
    shop = models.ForeignKey(on_delete=models.CASCADE, to="shuup.Shop", related_name="snippets")
    location = models.CharField(max_length=64, verbose_name=_("location"))
    snippet_type = models.CharField(max_length=20, verbose_name=_("snippet type"), choices=SnippetTypeChoices)
    snippet = models.TextField(verbose_name=_("snippet"))
    # list of theme identifiers that will be have this sniipet injected, if None, it means all themes
    themes = SeparatedValuesField(
        verbose_name=_("themes"),
        blank=True,
        null=True,
        help_text=_(
            "Select the themes that will have this snippet injected. Leave the field blank to inject in all themes."
        ),
    )

    class Meta:
        verbose_name = _("Snippet")
        verbose_name_plural = _("Snippets")

    def __str__(self):
        return self.name
