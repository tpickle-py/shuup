import json

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.db.transaction import atomic
from django.http import HttpResponseRedirect
from django.http.response import JsonResponse
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy
from django.views.generic import TemplateView
from filer.models import File, Folder

from shuup.admin.form_part import FormPartsViewMixin, SaveFormPartsMixin
from shuup.admin.modules.media.form_parts import MediaFolderBaseFormPart
from shuup.admin.shop_provider import get_shop
from shuup.admin.toolbar import get_default_edit_toolbar
from shuup.admin.utils.permissions import has_permission
from shuup.admin.utils.views import CreateOrUpdateView
from shuup.core.models import MediaFile, MediaFolder
from shuup.utils.excs import Problem
from shuup.utils.filer import (
    UploadFileForm,
    UploadImageForm,
    ensure_media_file,
    ensure_media_folder,
    filer_file_from_upload,
    filer_file_to_json_dict,
    filer_folder_to_json_dict,
    filer_image_from_upload,
    get_or_create_folder,
    subfolder_of_users_root,
)


def _is_folder_shared(folder):
    if not settings.SHUUP_ENABLE_MULTIPLE_SHOPS:
        return False

    media_folder = MediaFolder.objects.filter(folder=folder).first()
    if not media_folder:
        return True
    return bool(media_folder.shops.count() != 1)


def _get_folder_query_filter(shop, user=None):
    query = Q(Q(Q(media_folder__isnull=True) | Q(media_folder__shops__isnull=True) | Q(media_folder__shops=shop)))
    if user and not has_permission(user, "media.view-all"):
        root_folders = Folder.objects.filter(media_folder__owners=user)
        folders = []
        for root_folder in root_folders:
            for root_media_folder in root_folder.media_folder.all():
                folders.extend(root_media_folder.get_all_children())

        query &= Q(Q(media_folder__visible=True) | Q(id__in=[folder.id for folder in folders]))
    return query


def _get_folder_query(shop, user=None, folder=None):
    queryset = Folder.objects.filter(_get_folder_query_filter(shop, user))
    if folder:
        queryset = queryset.filter(id=folder.id)
    return queryset


def _is_file_shared(file):
    if not settings.SHUUP_ENABLE_MULTIPLE_SHOPS:
        return False

    media_file = MediaFile.objects.filter(file=file).first()
    if not media_file:
        return True
    return bool(media_file.shops.count() != 1)


def _get_file_query(shop, folder=None):
    query = Q(is_public=True)
    query &= Q(Q(media_file__isnull=True) | Q(media_file__shops__isnull=True) | Q(media_file__shops=shop))
    queryset = File.objects.filter(query)
    if folder:
        queryset = queryset.filter(folder=folder)
    return queryset


def get_folder_name(folder):
    return folder.name if folder else _("Root")


class MediaBrowserView(TemplateView):
    """
    A view for browsing media.

    Most of this is just a JSON API that the Javascript (`static_src/media/browser`) uses.
    """

    template_name = "shuup/admin/media/browser.jinja"
    title = gettext_lazy("Browse Media")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["browser_config"] = {
            "filter": self.filter,
            "disabledMenus": self.disabledMenus,
        }
        return context

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.filter = request.GET.get("filter")
        self.disabledMenus = request.GET.get("disabledMenus", "").split(",")
        action = request.GET.get("action")
        handler = getattr(self, f"handle_get_{action}", None)
        if handler:
            return handler(request.GET)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action") or request.GET.get("action")
        if action == "upload":
            return media_upload(request, *args, **kwargs)

        # Instead of normal POST variables, the Mithril `m.request()`
        # method passes data as a JSON payload (which is a good idea,
        # as it allows shedding the legacy of form data), so we need
        # to parse that.

        data = json.loads(request.body.decode("utf-8"))
        action = data.get("action")
        handler = getattr(self, f"handle_post_{action}", None)
        if handler:
            try:
                return handler(data)
            except ObjectDoesNotExist as odne:
                return JsonResponse({"error": force_str(odne)}, status=400)
            except Problem as prob:
                return JsonResponse({"error": force_str(prob)})
        else:
            return JsonResponse({"error": f"Error! Unknown action `{action}`."})

    def _create_folder(self, name, parent, shop):
        folder = Folder.objects.create(name=name)
        if parent:
            folder.move_to(parent, "last-child")
            folder.save()

        ensure_media_folder(shop, folder)
        return JsonResponse(
            {
                "success": True,
                "folder": filer_folder_to_json_dict(folder, (), self.user),
            }
        )


def _process_form(request, folder):
    try:
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
            filer_file = filer_image_from_upload(request, path=folder, upload_data=request.FILES["file"])
        elif not request.FILES["file"].content_type.startswith("image/"):
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                filer_file = filer_file_from_upload(request, path=folder, upload_data=request.FILES["file"])

        if not form.is_valid():
            return JsonResponse({"error": form.errors}, status=400)

        ensure_media_file(get_shop(request), filer_file)
    except Exception as exc:
        return JsonResponse({"error": force_str(exc)}, status=500)

    return JsonResponse(
        {
            "file": filer_file_to_json_dict(filer_file),
            "message": _("%(file)s uploaded to %(folder)s.")
            % {"file": filer_file.label, "folder": get_folder_name(folder)},
        }
    )


def media_upload(request, *args, **kwargs):
    shop = get_shop(request)
    try:
        folder_id = int(request.POST.get("folder_id") or request.GET.get("folder_id") or 0)
        path = request.POST.get("path") or request.GET.get("path") or None
        if folder_id != 0:
            folder = _get_folder_query(shop, request.user).get(pk=folder_id)
        elif path:
            folder = get_or_create_folder(shop, path, request.user)
        else:
            folder = None  # Root folder upload. How bold!
    except Exception as exc:
        return JsonResponse({"error": f"Error! Invalid folder `{force_str(exc)}`."}, status=400)

    if subfolder_of_users_root(request.user, folder) or has_permission(request.user, "media.upload-to-folder"):
        return _process_form(request, folder)

    return JsonResponse(
        {"error": _("You do not have permission to upload content to this folder")},
        status=400,
    )


class MediaFolderEditView(SaveFormPartsMixin, FormPartsViewMixin, CreateOrUpdateView):
    model = MediaFolder
    template_name = "shuup/admin/media/edit.jinja"
    context_object_name = "media_folder"
    base_form_part_classes = [MediaFolderBaseFormPart]
    form_part_class_provide_key = "admin_media_folder_form_part"

    def dispatch(self, request, *args, **kwargs):
        if has_permission(request.user, "media.edit-access"):
            return super().dispatch(request, *args, **kwargs)

        messages.warning(request, _("You don't have access to preform this action."))
        return reverse("shuup_admin:media.browse")

    def post(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        return HttpResponseRedirect(reverse("shuup_admin:media.browse"))

    def get_toolbar(self):
        return get_default_edit_toolbar(self, self.get_save_form_id())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.object.folder.name
        return context

    @atomic
    def form_valid(self, form):
        return self.save_form_parts(form)

    def get_queryset(self):
        return MediaFolder.objects.all()
