from shuup.core.basket.command_middleware import BaseBasketCommandMiddleware


class TestBasketCommandMiddleware(BaseBasketCommandMiddleware):
    def preprocess_kwargs(self, basket, request, command: str, kwargs: dict) -> dict:
        kwargs["extra"] = kwargs.get("extra") or {}
        kwargs["extra"]["extra"] = kwargs["extra"].get("extra") or {}
        kwargs["extra"]["extra"]["line_options"] = "works"
        return kwargs

    def postprocess_response(self, basket, request, command: str, kwargs: dict, response: dict) -> dict:
        response["it_works"] = True
        return response
