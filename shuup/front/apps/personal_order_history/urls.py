from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    url(
        r"^order-history/re-order/(?P<pk>.+)/$",
        login_required(views.ReorderView.as_view()),
        name="reorder-order",
    ),
    url(
        r"^order-history/$",
        login_required(views.OrderListView.as_view()),
        name="personal-orders",
    ),
    url(
        r"^order-history/(?P<pk>.+)/$",
        login_required(views.OrderDetailView.as_view()),
        name="show-order",
    ),
]
