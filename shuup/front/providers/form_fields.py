import six


class FormFieldDefinition(object):
    """
    Simple definition for form fields

    provided by `shuup.front.providers.form_fields.FormFieldProvider`
    """

    # field name
    name = None

    # field object
    field = None

    def __init__(self, name, field, **kwargs):
        self.name = name
        self.field = field
        for k, v in six.iteritems(kwargs):
            setattr(self, k, v)


class FormFieldProvider(object):
    def __init__(self, **kwargs):
        for k, v in kwargs:
            setattr(self, k, v)

    def get_fields(self, **kwargs):
        """
        Get a list of field definitions

        :return: list of `FormFieldDefinition`s
        :rtype: list[shuup.front.providers.form_fields.FormFieldDefinition]
        """
        return []
