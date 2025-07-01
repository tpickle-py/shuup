from django.http import HttpRequest

from shuup.core.basket.objects import BaseBasket


class BaseBasketCommandMiddleware:
    """
    A basket command middleware to pre-process the kwargs and post-process the response.
    """

    def preprocess_kwargs(self, basket: BaseBasket, request: HttpRequest, command: str, kwargs: dict) -> dict:
        """
        Mutate the `kwargs` that will be passed to the `handler`.
        It is possible to raise a `ValidationError` exception if required.
        """
        return kwargs

    def postprocess_response(
        self,
        basket: BaseBasket,
        request: HttpRequest,
        command: str,
        kwargs: dict,
        response: dict,
    ) -> dict:
        """
        Mutate the `response` before it is returned by the command dispatcher.
        """
        return response
