from .category_factory import CategoryFactory
from .company_factory import CompanyFactory

# Import from contact factory
from .contact_factory import (
    create_random_company,
    create_random_contact_group,
    create_random_person,
    create_random_user,
    get_default_customer_group,
    get_default_permission_group,
    get_default_staff_user,
)

# Import from order factory
from .order_factory import (
    add_product_to_order,
    create_default_order_statuses,
    create_empty_order,
    create_order_with_product,
    create_random_order,
    get_basket,
    get_completed_order_status,
    get_initial_order_status,
)
from .person_contact_factory import PersonContactFactory
from .product_factory import ProductFactory
from .product_type_factory import ProductTypeFactory
from .sales_unit_factory import SalesUnitFactory

# Import from service factory
from .service_factory import (
    get_custom_carrier,
    get_custom_payment_processor,
    get_default_payment_method,
    get_default_shipping_method,
    get_payment_method,
    get_payment_processor_with_checkout_phase,
    get_shipping_method,
)

# Import from shared utilities
# Import remaining functions from shared (to be moved to product/shop factories)
from .shared import (
    ATTR_SPECS,
    DEFAULT_CURRENCY,
    DEFAULT_IDENTIFIER,
    DEFAULT_NAME,
    _generate_product_image,
    _get_pricing_context,
    complete_product,
    create_attribute_with_options,
    create_package_product,
    create_product,
    create_random_address,
    create_random_product_attribute,
    default_by_identifier,
    get_address,
    get_all_seeing_key,
    get_currency,
    get_default_attribute_set,
    get_default_category,
    get_default_currency,
    get_default_manufacturer,
    get_default_product,
    get_default_product_type,
    get_default_sales_unit,
    get_default_shop,
    get_default_shop_product,
    get_default_supplier,
    get_faker,
    get_fractional_sales_unit,
    get_random_email,
    get_random_filer_image,
    get_shop,
    get_supplier,
)
from .shop_factory import ShopFactory
from .shop_product_factory import ShopProductFactory

# Import from tax factory
from .tax_factory import create_default_tax_rule, get_default_tax, get_default_tax_class, get_tax, get_test_tax
from .user_factory import UserFactory

# Add more as you break them out
FACTORY_CLASSES = [
    UserFactory,
    ShopFactory,
    ProductTypeFactory,
    SalesUnitFactory,
    CategoryFactory,
    ShopProductFactory,
    ProductFactory,
    # TODO: Add more factories as needed
]


__all__ = [
    "UserFactory",
    "ShopFactory",
    "ProductTypeFactory",
    "SalesUnitFactory",
    "CategoryFactory",
    "ShopProductFactory",
    "ProductFactory",
    "CompanyFactory",
    "PersonContactFactory",
    "ATTR_SPECS",
    "DEFAULT_CURRENCY",
    "DEFAULT_IDENTIFIER",
    "DEFAULT_NAME",
    "create_random_company",
    "create_random_contact_group",
    "create_random_order",
    "create_random_person",
    "create_random_product_attribute",
    "get_default_product_type",
    "get_default_supplier",
    "get_initial_order_status",
    "get_completed_order_status",
    "default_by_identifier",
    "get_default_attribute_set",
    "get_default_manufacturer",
    "get_tax",
    "create_default_tax_rule",
    "get_default_tax",
    "get_test_tax",
    "get_default_tax_class",
    "get_currency",
    "get_default_currency",
    "get_custom_payment_processor",
    "get_payment_processor_with_checkout_phase",
    "get_custom_carrier",
    "get_default_payment_method",
    "get_payment_method",
    "get_default_shipping_method",
    "get_shipping_method",
    "get_default_customer_group",
    "get_supplier",
    "get_default_shop",
    "get_shop",
    "get_random_filer_image",
    "complete_product",
    "create_product",
    "get_default_product",
    "get_default_shop_product",
    "get_default_sales_unit",
    "get_fractional_sales_unit",
    "get_default_category",
    "get_default_permission_group",
    "get_faker",
    "create_random_user",
    "get_default_staff_user",
    "get_random_email",
    "create_random_address",
    "get_address",
    "_generate_product_image",
    "create_attribute_with_options",
    "create_empty_order",
    "add_product_to_order",
    "create_order_with_product",
    "_get_pricing_context",
    "get_all_seeing_key",
    "get_basket",
    "create_package_product",
    "create_default_order_statuses",
]
__all__.extend(fclass.__name__ for fclass in FACTORY_CLASSES if fclass.__name__ not in __all__)  # type: ignore
