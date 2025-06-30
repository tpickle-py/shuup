from shuup.front.views.product import ProductDetailView


class ProductPreviewView(ProductDetailView):
    template_name = "shuup/front/product/product_preview.jinja"

    def get_context_data(self, **kwargs):
        # By default the template rendering the basket add form
        # uses the `request.path` as its' `next` value.
        # This is fine if you are on product page but here in
        # preview, we cannot redirect back to `/xtheme/product_preview`.

        context = super().get_context_data(**kwargs)
        # Add `return_url` to context to avoid usage of `request.path`
        context["return_url"] = "/xtheme/products"
        return context


def product_preview(request):
    return ProductPreviewView.as_view()(request, pk=request.GET["id"])
