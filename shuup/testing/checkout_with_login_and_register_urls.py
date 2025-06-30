from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from shuup.front.views.checkout import CheckoutViewWithLoginAndRegister

urlpatterns = [
    url(r"^checkout/$", CheckoutViewWithLoginAndRegister.as_view(), name="checkout"),
    url(
        r"^checkout/(?P<phase>.+)/$",
        CheckoutViewWithLoginAndRegister.as_view(),
        name="checkout",
    ),
    path("admin/", admin.site.urls),
    url(r"^sa/", include("shuup.admin.urls", namespace="shuup_admin")),
    url(r"^", include("shuup.front.urls", namespace="shuup")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
