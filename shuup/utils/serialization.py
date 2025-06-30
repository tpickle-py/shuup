
import django.core.serializers.json
from django.utils.functional import Promise

from shuup.utils.django_compat import force_text


class ExtendedJSONEncoder(django.core.serializers.json.DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, Promise):
            return force_text(o)
        return super(ExtendedJSONEncoder, self).default(o)
