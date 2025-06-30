from django.core.exceptions import ValidationError


class ImporterError(ValidationError):
    pass
