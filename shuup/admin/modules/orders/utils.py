"""
Order utilities and helper classes.
"""


class OrderInformation:
    """Helper class for order information display."""

    def __init__(self, order):
        self._order = order
        self._provides_info = []
        self.title = "Order Information"
        self.information = ""

    def add_info(self, info_dict):
        """Add information to the order display."""
        self._provides_info.append(info_dict)

    def get_info(self):
        """Get all order information."""
        return self._provides_info

    def provides_info(self):
        """Check if this instance provides information."""
        return bool(self._provides_info)

    @property
    def order(self):
        """Order ordering for sorting."""
        return 0
