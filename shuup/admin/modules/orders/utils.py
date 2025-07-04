"""
Order utilities and helper classes.
"""


class OrderInformation:
    """Helper class for order information display."""

    def __init__(self, order):
        self.order = order
        self.provides_info = []

    def add_info(self, info_dict):
        """Add information to the order display."""
        self.provides_info.append(info_dict)

    def get_info(self):
        """Get all order information."""
        return self.provides_info
