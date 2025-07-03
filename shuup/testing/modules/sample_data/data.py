from django.utils.translation import gettext_lazy as _

BUSINESS_SEGMENTS = {
    "default": {
        "name": _("Default"),
        "categories": [
            {
                "name": _("Default"),
                "description": _("Cosmetics and perfumes"),
                "image": "default/category01.jpg",
            }
        ],
        "products": [
            {
                "name": _("USpicy Makeup Brushes"),
                "description": _("Professional 10 pieces makeup brush set with soft oval toothbrush design"),
                "image": "default/product01.jpg",
            },
            {
                "name": _("Precision Eyelash Curler"),
                "description": _("Precision Eyelash Curler is the professional choice of makeup artists everywhere."),
                "image": "default/product02.jpg",
            },
            {
                "name": _("PureMoist Lipstick"),
                "description": _(
                    "PureMoist Lipstick has a moisturizing formula designed to quench, comfort and protect lips."
                ),
                "image": "default/product03.jpg",
            },
            {
                "name": _("Clinique Happy"),
                "description": _("A hint of citrus. A wealth of flowers. A mix of emotions."),
                "image": "default/product04.jpg",
            },
            {
                "name": _("Tommy Girld by Tommy Hilfiger Perfume"),
                "description": _("A refreshing and energetic floral - with low notes of sandalwood and heather."),
                "image": "default/product05.jpg",
            },
            {
                "name": _("Bvlgari Omnia Crystalline Eau de Toilette"),
                "description": _(
                    "Give yourself over to this fragrance as intoxicating and pure as a woman's soul is fragile."
                ),
                "image": "default/product06.jpg",
            },
            {
                "name": _("Still Jennifer Lopez Perfume"),
                "description": _(
                    "Be driven with vitality and confidence, as you wear the Jennifer Lopez Still fragrance."
                ),
                "image": "default/product07.jpg",
            },
            {
                "name": _("La Vie Est Belle"),
                "description": _("A captivating new scent joins the La vie est belle path to happiness."),
                "image": "default/product08.jpg",
            },
            {
                "name": _("Smooth Viking Beard Brush"),
                "description": _("Just a beard brush."),
                "image": "default/product09.jpg",
            },
            {
                "name": _("Beard & Stash Oil"),
                "description": _("This oil is natural, and is made with the perfect combination of oils."),
                "image": "default/product10.jpg",
            },
        ],
        "carousel": {
            "name": _("Sample Carousel"),
            "width": 1000,
            "height": 400,
            "slides": [
                {"title": "You awesome again.", "image": "default/banner01.jpg"},
                {
                    "title": "The best cosmetics in the world.",
                    "image": "default/banner02.jpg",
                },
            ],
        },
    }
}
