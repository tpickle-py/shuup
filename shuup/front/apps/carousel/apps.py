import shuup.apps


class AppConfig(shuup.apps.AppConfig):
    name = "shuup.front.apps.carousel"
    label = "carousel"
    default_auto_field = "django.db.models.BigAutoField"
    provides = {
        "admin_module": ["shuup.front.apps.carousel.admin_module:CarouselModule"],
        "xtheme_plugin": [
            "shuup.front.apps.carousel.plugins:CarouselPlugin",
            "shuup.front.apps.carousel.plugins:BannerBoxPlugin",
        ],
    }

    def ready(self):
        from shuup.utils.djangoenv import has_installed

        if has_installed("shuup.xtheme"):
            from django.db.models.signals import post_save

            from shuup.xtheme.cache import bump_xtheme_cache

            from .models import Carousel, Slide

            post_save.connect(bump_xtheme_cache, sender=Carousel)
            post_save.connect(bump_xtheme_cache, sender=Slide)
