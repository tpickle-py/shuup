

class OrderInformation:
    order = 1
    title = "default"

    def __init__(self, order, **kwargs):
        self.order = order

    def provides_info(self):
        """
        Override to add business logic if the order should show this information row.
        """
        return self.information is not None

    @property
    def information(self):
        """
        Override this property to return wanted information about the order.
        """
        return None
