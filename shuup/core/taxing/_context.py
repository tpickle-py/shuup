class TaxingContext:
    def __init__(self, customer_tax_group=None, customer_tax_number=None, location=None):
        self.customer_tax_group = customer_tax_group
        self.customer_tax_number = customer_tax_number
        self.country_code = getattr(location, "country_code", None) or getattr(location, "country", None)
        self.region_code = getattr(location, "region_code", None)
        self.postal_code = getattr(location, "postal_code", None)
        self.location = location
