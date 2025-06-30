from django.conf.urls import url

from shuup.simple_cms.views import PageView

urlpatterns = [
    url(r"^(?P<url>.*)/$", PageView.as_view(), name="cms_page"),
]
