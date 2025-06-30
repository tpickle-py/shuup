from shuup.core.models import Category, Product, ShopProduct, Supplier
from shuup.utils.django_compat import reverse


def model_url(context, model, absolute=False, **kwargs):
    uri = None

    if isinstance(model, Product):
        supplier = kwargs.get("supplier") or context.get("supplier")

        # if the supplier was passed and it supplies the product, the URL can be supplier specific
        if (
            isinstance(supplier, Supplier)
            and ShopProduct.objects.filter(product=model, suppliers=supplier).exists()
        ):
            uri = reverse(
                "shuup:supplier-product",
                kwargs=dict(pk=model.pk, slug=model.slug, supplier_pk=supplier.pk),
            )
        else:
            uri = reverse("shuup:product", kwargs=dict(pk=model.pk, slug=model.slug))

    if isinstance(model, Category):
        uri = reverse("shuup:category", kwargs=dict(pk=model.pk, slug=model.slug))

    if hasattr(model, "pk") and model.pk and hasattr(model, "url"):
        uri = "/{}".format(model.url)

    if absolute:
        request = context.get("request")
        if not request:  # pragma: no cover
            raise ValueError(
                "Error! Unable to use `absolute=True` when request does not exist."
            )
        uri = request.build_absolute_uri(uri)

    return uri
