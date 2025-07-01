from shuup.apps import AppConfig


class SimpleSearchAppConfig(AppConfig):
    name = "shuup.front.apps.simple_search"
    verbose_name = "Shuup Frontend - Simple Search"
    label = "shuup_front_simple_search"

    provides = {
        "front_urls": ["shuup.front.apps.simple_search.urls:urlpatterns"],
        "front_extend_product_list_form": [
            "shuup.front.apps.simple_search.forms.FilterProductListByQuery",
        ],
        "front_template_helper_namespace": ["shuup.front.apps.simple_search.template_helpers:TemplateHelpers"],
    }


default_app_config = "shuup.front.apps.simple_search.SimpleSearchAppConfig"
