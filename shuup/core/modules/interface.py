import six

from shuup.apps.provides import get_provide_specs_and_objects
from shuup.utils.importing import load
from shuup.utils.text import force_ascii


class ModuleNotFound(ValueError):
    pass


class ModuleInterface:
    _cached_modules_impl = None
    module_options_field = "module_data"  # May be overridden on class level
    module_provides_key = None

    def _load_modules(self):
        enabled_supplier_modules = self.supplier_modules.all()
        loaded_modules = []
        options = getattr(self, self.module_options_field, None) or {}

        for supplier_module in enabled_supplier_modules:
            impls = self.get_module_implementation_map()
            if supplier_module.module_identifier not in impls:
                raise ModuleNotFound(f"Invalid module identifier {supplier_module.name!r} in {force_ascii(repr(self))}")
            spec = impls[supplier_module.module_identifier]
            module = load(
                spec,
                context_explanation=f"Loading module for {force_ascii(repr(self))}",
            )
            loaded_modules.append(module(self, options))

        return loaded_modules

    @property
    def modules(self):
        if not getattr(self, "_cached_modules_impl", None):
            self._cached_modules_impl = self._load_modules()
        return self._cached_modules_impl

    @classmethod
    def get_module_implementation_map(cls):
        """
        Get a dict that maps module spec identifiers (short strings) into actual spec names.

        As an example::

            {"Eggs": "foo_package.bar_module:EggsClass"}

        :rtype: dict[str, str]
        """
        identifier_to_spec = {}
        for spec, module in six.iteritems(get_provide_specs_and_objects(cls.module_provides_key)):
            if module.identifier:
                identifier_to_spec[module.identifier] = spec
        return identifier_to_spec
