from http import HTTPStatus
from typing import Any, Dict, Iterable, List, Optional, Tuple, Type, Union

from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from shuup.admin.supplier_provider import get_supplier
from shuup.admin.utils.object_selector import get_object_selector_permission_name
from shuup.admin.utils.permissions import has_permission
from shuup.apps.provides import get_provide_objects
from shuup.core.models import (
    Carrier,
    Category,
    Contact,
    Product,
    ProductMode,
    Shop,
    ShopProduct,
    ShopProductVisibility,
    Supplier,
)
from shuup.utils.django_compat import force_text


def _field_exists(model, field):
    try:
        model._meta.get_field(field)
        return True
    except FieldDoesNotExist:
        return False


class MultiselectAjaxView(TemplateView):
    """
    This view is deprecated and it will be removed on version 3.
    """

    model = None
    search_fields: List[str] = []
    result_limit = 20

    def init_search_fields(self, cls):
        """
        Configure the fields to use for searching.

        If the `cls` object has a search_fields attribute, it will be used,
        otherwise, the class will be inspected and the attribute
        `name` or `translations__name` will mainly be used.

        Other fields will be used for already known `cls` instances.
        """
        if hasattr(cls, "search_fields"):
            self.search_fields = cls.search_fields
            return

        self.search_fields = []
        key = "%sname" % ("translations__" if hasattr(cls, "translations") else "")
        self.search_fields.append(key)

        if issubclass(cls, Carrier):
            self.search_fields.append("base_translations__name")
            self.search_fields.remove("name")
        if issubclass(cls, Contact):
            self.search_fields.append("email")
        if issubclass(cls, Product):
            self.search_fields.append("sku")
            self.search_fields.append("barcode")
        if issubclass(cls, ShopProduct):
            self.search_fields.append("product__translations__name")

        user_model = get_user_model()
        if issubclass(cls, user_model):
            if _field_exists(user_model, "username"):
                self.search_fields.append("username")
            if _field_exists(user_model, "email"):
                self.search_fields.append("email")
            if not _field_exists(user_model, "name"):
                self.search_fields.remove("name")

    def get_data(self, request, *args, **kwargs):  # noqa
        model_name = request.GET.get("model")
        if not model_name:
            return []

        cls = apps.get_model(model_name)
        qs = cls.objects.all()
        shop = request.shop

        # if shop is informed, make sure user has access to it
        if request.GET.get("shop"):
            query_shop = Shop.objects.get_for_user(request.user).filter(pk=request.GET["shop"]).first()
            if query_shop:
                shop = query_shop

        search_mode = request.GET.get("searchMode")
        qs = self._filter_query(request, cls, qs, shop, search_mode)
        self.init_search_fields(cls)
        if not self.search_fields:
            return [{"id": None, "name": _("Couldn't get selections for %s.") % model_name}]

        if request.GET.get("search"):
            query = Q()
            keyword = request.GET.get("search", "").strip()
            for field in self.search_fields:
                query |= Q(**{f"{field}__icontains": keyword})

            if issubclass(cls, Contact) or issubclass(cls, get_user_model()):
                query &= Q(is_active=True)

            qs = qs.filter(query)

        if search_mode and issubclass(cls, Product):
            if search_mode == "main":
                qs = qs.filter(
                    mode__in=[
                        ProductMode.SIMPLE_VARIATION_PARENT,
                        ProductMode.VARIABLE_VARIATION_PARENT,
                        ProductMode.NORMAL,
                    ]
                )
            elif search_mode == "parent_product":
                qs = qs.filter(
                    mode__in=[
                        ProductMode.SIMPLE_VARIATION_PARENT,
                        ProductMode.VARIABLE_VARIATION_PARENT,
                    ]
                )
            elif search_mode == "sellable_mode_only":
                qs = qs.exclude(
                    Q(
                        mode__in=[
                            ProductMode.SIMPLE_VARIATION_PARENT,
                            ProductMode.VARIABLE_VARIATION_PARENT,
                        ]
                    )
                    | Q(deleted=True)
                    | Q(shop_products__visibility=ShopProductVisibility.NOT_VISIBLE)
                ).filter(shop_products__purchasable=True)

        sales_units = request.GET.get("salesUnits")
        if sales_units and issubclass(cls, Product):
            qs = qs.filter(sales_unit__translations__symbol__in=sales_units.strip().split(","))

        qs = qs.distinct()
        return sorted(
            [{"id": obj.id, "name": force_text(obj)} for obj in qs[: self.result_limit]],
            key=lambda x: x["name"],
        )

    def _filter_query(self, request, cls, qs, shop, search_mode=None):
        # the supplier provider returned a valid supplier
        # make sure to filter the search by the current supplier
        supplier = get_supplier(request)

        if search_mode == "visible" and issubclass(cls, Category):
            qs = cls.objects.all_visible(self.request.customer, shop=self.request.shop)
        elif search_mode == "enabled" and issubclass(cls, Supplier):
            qs = cls.objects.enabled(shop=shop)
        elif hasattr(cls.objects, "all_except_deleted"):
            qs = cls.objects.all_except_deleted(shop=shop)
        elif hasattr(cls.objects, "get_for_user"):
            qs = cls.objects.get_for_user(self.request.user)

        if issubclass(cls, Product):
            qs = qs.filter(shop_products__shop=shop)

            if supplier:
                qs = qs.filter(shop_products__suppliers=supplier)

        related_fields = [
            models.OneToOneField,
            models.ForeignKey,
            models.ManyToManyField,
        ]

        # Get all relation fields and check whether this models has
        # relation to Shop mode, if so, filter by the current shop
        allowed_shop_fields = ["shop", "shops"]
        shop_related_fields = [
            field
            for field in cls._meta.get_fields()
            if type(field) in related_fields and field.related_model == Shop and field.name in allowed_shop_fields
        ]
        for shop_field in shop_related_fields:
            qs = qs.filter(**{shop_field.name: shop})

        if supplier:
            allowed_supplier_fields = ["supplier", "suppliers"]
            supplier_related_fields = [
                field
                for field in cls._meta.get_fields()
                if (
                    type(field) in related_fields
                    and field.related_model == Supplier
                    and field.name in allowed_supplier_fields
                )
            ]
            for supplier_field in supplier_related_fields:
                qs = qs.filter(**{supplier_field.name: supplier})

        return qs

    def get(self, request, *args, **kwargs):
        return JsonResponse({"results": self.get_data(request, *args, **kwargs)})


class ObjectSelectorView(TemplateView):
    """
    Base class for responding to searches from select2 components.
    """

    def get(self, request, *args, **kwargs):
        parameters = request.GET.dict()
        selector = parameters.pop("selector", "")
        if not selector:
            HttpResponse(_("Selector not found."), status=HTTPStatus.BAD_REQUEST)
        search_term = parameters.pop("q", "").strip()
        user = request.user
        shop = request.GET.get("shop")
        if shop:
            query_shop = Shop.objects.get_for_user(request.user).filter(pk=request.GET["shop"]).first()
            if query_shop:
                shop = query_shop
        else:
            shop = Shop.objects.get_for_user(request.user).first()
        supplier = get_supplier(request)

        if not (selector and search_term):
            return JsonResponse({}, status=HTTPStatus.BAD_REQUEST)  # Error 400

        for admin_object_selector_class in sorted(
            get_provide_objects("admin_object_selector"),
            key=lambda provides: provides.ordering,
        ):
            if not issubclass(admin_object_selector_class, BaseAdminObjectSelector):
                continue

            if not admin_object_selector_class.handles_selector(selector):
                continue

            admin_object_selector = admin_object_selector_class(selector, shop, user, supplier)

            if not admin_object_selector.has_permission():
                return JsonResponse({}, status=HTTPStatus.NOT_ACCEPTABLE)  # Error 406

            data = admin_object_selector.get_objects(search_term, **parameters)
            return JsonResponse({"results": data})

        return JsonResponse({}, status=HTTPStatus.NOT_FOUND)  # Error 404


class BaseAdminObjectSelector:
    search_limit = 20
    model: Optional[Type[Any]] = None

    def __init__(self, selector, shop, user, supplier=None, *args, **kwargs):
        self.selector = selector
        self.shop = shop
        self.user = user
        self.supplier = supplier

    @classmethod
    def get_selector_for_model(cls, model):
        return f"{model._meta.app_label}.{model._meta.model_name}"

    @classmethod
    def handles_selector(cls, selector) -> bool:
        return selector == cls.get_selector_for_model(cls.model)

    @classmethod
    def handle_subclass_selector(cls, selector, parent_model):
        try:
            app_name, model_name = selector.split(".")
            Model = apps.get_model(app_label=app_name, model_name=model_name)
            return isinstance(Model, type) and issubclass(Model, parent_model)
        except LookupError:
            return False

    def has_permission(self) -> bool:
        return has_permission(self.user, get_object_selector_permission_name(self.model))

    def get_objects(self, search_term, *args, **kwargs) -> Union[Iterable[Tuple[int, str]], List[Dict[str, Any]]]:
        raise NotImplementedError()
