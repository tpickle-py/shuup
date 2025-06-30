from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    url(
        r"^saved-carts/$",
        login_required(views.CartListView.as_view()),
        name="saved_cart.list",
    ),
    url(
        r"^saved-carts/save/$",
        login_required(views.CartSaveView.as_view()),
        name="saved_cart.save",
    ),
    url(
        r"^saved-carts/(?P<pk>\d+)/add/$",
        login_required(views.CartAddAllProductsView.as_view()),
        name="saved_cart.add_all",
    ),
    url(
        r"^saved-carts/(?P<pk>\d+)/delete/$",
        login_required(views.CartDeleteView.as_view()),
        name="saved_cart.delete",
    ),
    url(
        r"^saved-carts/(?P<pk>.+)/$",
        login_required(views.CartDetailView.as_view()),
        name="saved_cart.detail",
    ),
]
