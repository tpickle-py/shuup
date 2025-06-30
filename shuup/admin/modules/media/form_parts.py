
from shuup.admin.form_part import FormPart, TemplatedFormDef
from shuup.admin.modules.media.forms import MediaFolderForm


class MediaFolderBaseFormPart(FormPart):
    priority = 1

    def get_form_defs(self):
        yield TemplatedFormDef(
            "media_form",
            MediaFolderForm,
            template_name="shuup/admin/media/edit_folder.jinja",
            required=False,
            kwargs={
                "instance": self.object,
            },
        )

    def form_valid(self, form):
        self.object = form["media_form"].save()
