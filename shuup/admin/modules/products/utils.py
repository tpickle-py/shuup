from shuup.core.models import ProductPackageLink


def clear_existing_package(parent_product):
    """
    Utility function for clearing existing package.
    """
    children = parent_product.get_package_child_to_quantity_map().keys()
    ProductPackageLink.objects.filter(parent=parent_product).delete()
    parent_product.verify_mode()
    parent_product.save()
    for child in children:
        child.verify_mode()
        child.save()
