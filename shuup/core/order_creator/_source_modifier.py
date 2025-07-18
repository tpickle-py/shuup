from shuup.apps.provides import load_module_instances


def get_order_source_modifier_modules():
    """
    Get a list of configured order source modifier module instances.

    :rtype: list[OrderSourceModifierModule]
    """
    return load_module_instances("SHUUP_ORDER_SOURCE_MODIFIER_MODULES", "order_source_modifier_module")


def is_code_usable(order_source, code):
    return any(module.can_use_code(order_source, code) for module in get_order_source_modifier_modules())


class OrderSourceModifierModule:
    def get_new_lines(self, order_source, lines):
        """
        Get new lines to be added to order source.

        :type order_source: shuup.core.order_creator.OrderSource
        :type lines: list[shuup.core.order_creator.SourceLine]
        :rtype: Iterable[shuup.core.order_creator.SourceLine]
        """
        return []

    def can_use_code(self, order_source, code):
        return False

    def use_code(self, order, code):
        pass

    def clear_codes(self, order):
        pass
