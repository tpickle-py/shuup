from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from filer.models import Folder


@transaction.atomic()
def delete_folder(folder):
    """
    Delete a Filer folder and move files and subfolders up to the parent.

    :param folder: Folder.
    :type folder: filer.models.Folder
    :return: Success message.
    :rtype: str
    """
    parent_folder = folder.parent if folder.parent_id else None

    parent_name = parent_folder.name if parent_folder else _("Root")
    subfolders = list(folder.children.all())
    message_bits = []
    if subfolders:
        for subfolder in subfolders:
            subfolder.move_to(parent_folder, "last-child")
            subfolder.save()
        message_bits.append(_("{num} subfolders moved to {folder}.").format(num=len(subfolders), folder=parent_name))
    n_files = folder.files.count()
    if n_files:
        folder.files.update(folder=parent_folder)
        message_bits.append(_("{num} files moved to {folder}.").format(num=n_files, folder=parent_name))
    folder.delete()  # Possibly raises a `ProtectedError`, that's why the `atomic()` block.
    if subfolders:  # We had some subfolders to mangle, best rebuild now
        Folder._tree_manager.rebuild()

    message_bits.insert(0, _("Folder `%s` was deleted.") % folder.name)
    return "\n".join(message_bits)
