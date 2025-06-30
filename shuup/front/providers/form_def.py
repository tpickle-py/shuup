import six


class FormDefinition:
    """
    Simple Form definition class

    These objects are to be returned when using `FormDefProvider`.
    """

    form_name = None
    form_class = None
    required = False

    def __init__(self, name, form_class, **kwargs):
        self.form_name = name
        self.form_class = form_class
        self.required = False
        for k, v in six.iteritems(kwargs):
            setattr(self, k, v)


class FormDefProvider:
    """Provider to provide list of `FormDefinition`s"""

    # the form group / form instantiating this object
    source = None
    request = None

    def __init__(self, source, request, **kwargs):
        self.source = source
        self.request = request
        for k, v in kwargs:
            setattr(self, k, v)

    def get_definitions(self, **kwargs):
        """
        :return: list of `FormDefinition`s
        :rtype: list[shuup.front.providers.form_def.FormDefinition]
        """
        return []
