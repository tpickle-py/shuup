from shuup.core.models import Product
from shuup.core.utils.model_caching_descriptor import ModelCachingDescriptor


class ProductCachingObject(object):
    _descriptor = ModelCachingDescriptor("product", queryset=Product.objects.all())
    product = _descriptor.object_property
    product_id = _descriptor.id_property
