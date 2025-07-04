from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

"""
Modify these only for Shuup tests. For testing modify urls.py instead.
"""
urlpatterns = [
    path("admin/", admin.site.urls),
    path("sa/", include("shuup.admin.urls", namespace="shuup_admin")),
    path("", include("shuup.front.urls", namespace="shuup")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
