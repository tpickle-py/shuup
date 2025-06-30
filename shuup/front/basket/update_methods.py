

import six
from django.contrib import messages

from shuup.core.basket.update_methods import BasketUpdateMethods as CoreBasketUpdateMethods


class BasketUpdateMethods(CoreBasketUpdateMethods):
    def _handle_orderability_error(self, line, error):
        error_texts = ", ".join(six.text_type(sub_error) for sub_error in error)
        message = "Warning! {}: {}".format(
            line.get("text") or line.get("name"),
            error_texts,
        )
        messages.warning(self.request, message)
