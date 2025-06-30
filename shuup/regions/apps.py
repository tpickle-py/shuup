import shuup.apps


class AppConfig(shuup.apps.AppConfig):
    name = "shuup.regions"
    provides = {
        "xtheme_resource_injection": [
            "shuup.regions.resources:add_front_resources",
        ],
    }
