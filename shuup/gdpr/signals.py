from django.dispatch import Signal

anonymization_requested = Signal(
    providing_args=[
        "shop",
        "contact",
        "user",
    ],
    use_caching=True,
)
