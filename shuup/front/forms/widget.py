import six
from django.forms import HiddenInput, Widget
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from filer.models import File


class PictureDnDUploaderWidget(Widget):
    def __init__(
        self,
        attrs=None,
        kind="images",
        upload_path="/contacts",
        clearable=False,
        browsable=True,
        upload_url=None,
        dropzone_attrs=None,
    ):
        if dropzone_attrs is None:
            dropzone_attrs = {}
        self.kind = kind
        self.upload_path = upload_path
        self.clearable = clearable
        self.dropzone_attrs = dropzone_attrs

        super().__init__(attrs)

    def _get_file_attrs(self, file):
        if not file:
            return []
        try:
            thumbnail = file.easy_thumbnails_thumbnailer.get_thumbnail(
                {
                    "size": (120, 120),
                    "crop": True,
                    "upscale": True,
                    "subject_location": file.subject_location,
                }
            )
        except Exception:
            thumbnail = None
        data = {
            "id": file.id,
            "name": file.label,
            "size": file.size,
            "url": file.url,
            "thumbnail": (thumbnail.url if thumbnail else None),
            "date": file.uploaded_at.isoformat(),
        }
        return [f"data-{key}='{val}'" for key, val in six.iteritems(data) if val is not None]

    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        pk_input = HiddenInput().render(name, value, attrs)
        file_attrs = [
            f"data-upload_path='{self.upload_path}'",
            f"data-add_remove_links='{self.clearable}'",
            "data-dropzone='true'",
        ]
        if self.kind:
            file_attrs.append(f"data-kind='{self.kind}'")

        if self.dropzone_attrs:
            # attributes passed here will be converted into keys with dz_ prefix
            # `{max-filesize: 1}` will be converted into `data-dz_max-filesize="1"`
            file_attrs.extend([f'data-dz_{k}="{force_text(v)}"' for k, v in self.dropzone_attrs.items()])

        if value:
            file = File.objects.filter(pk=value).first()
            file_attrs += self._get_file_attrs(file)
        return mark_safe(
            "<div id='{}-dropzone' class='dropzone {}' {}>{}</div>".format(
                attrs.get("id", "dropzone"),
                "has-file" if value else "",
                " ".join(file_attrs),
                pk_input,
            )
        )
