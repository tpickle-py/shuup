

import six


class ModelCachingDescriptor:
    def __init__(self, name, queryset):
        self.name = name
        self.id_name = f"_{name}_id"
        self.object_name = f"_{name}_cache"
        self.queryset = queryset
        self.id_property = property(self.get_id, self.set_id)
        self.object_property = property(self.get_object, self.set_object)

    def _clear(self, instance):
        setattr(instance, self.id_name, None)
        setattr(instance, self.object_name, None)

    def set_id(self, instance, value):
        if not value:
            self._clear(instance)
        elif isinstance(value, six.integer_types):
            setattr(instance, self.id_name, value)
            current_cached = self._get_cached_object(instance)
            if current_cached and current_cached.pk != self.get_id(instance):
                setattr(instance, self.object_name, None)
        else:
            raise TypeError(
                f"Error! Can't assign ID `{value!r}` in a `ModelCachingDescriptor({self.name})`."
            )

    def get_id(self, instance):
        return getattr(instance, self.id_name, None)

    def set_object(self, instance, value):
        if not value:
            self._clear(instance)
        elif isinstance(value, self.queryset.model):
            if not value.pk:
                raise ValueError(
                    f"Error! Can't assign unsaved model `{value!r}` in a `ModelCachingDescriptor({self.name})`."
                )
            setattr(instance, self.id_name, value.pk)
            setattr(instance, self.object_name, value)
        else:
            raise TypeError(
                f"Error! Can't assign object `{value!r}` in a `ModelCachingDescriptor({self.name})`."
            )

    def get_object(self, instance):
        if not self.get_id(instance):
            return None
        value = self._get_cached_object(instance)
        if value is None:
            value = self._cache_object(instance)
        return value

    def _cache_object(self, instance):
        object = self.queryset.get(pk=self.get_id(instance))
        setattr(instance, self.object_name, object)
        setattr(instance, self.id_name, object.pk)
        return object

    def _get_cached_object(self, instance):
        return getattr(instance, self.object_name, None)
