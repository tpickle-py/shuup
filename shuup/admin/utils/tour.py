from shuup import configuration


def is_tour_complete(shop, tour_key, user=None):
    """
    Check if the tour is complete

    :param tour_key: The tour key.
    :type field: str
    :return: whether tour is complete
    :rtype: Boolean
    """
    user_id = user.pk if user else "-"
    return configuration.get(
        shop, f"shuup_{tour_key}_{user_id}_tour_complete", False
    )


def set_tour_complete(shop, tour_key, complete=True, user=None):
    user_id = user.pk if user else "-"
    return configuration.set(
        shop, f"shuup_{tour_key}_{user_id}_tour_complete", complete
    )
