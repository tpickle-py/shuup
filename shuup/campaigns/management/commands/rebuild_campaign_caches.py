from itertools import chain

from django.core.management.base import BaseCommand

from shuup.campaigns.models import (
    BasketCampaign,
    CatalogCampaign,
    CatalogFilter,
    CategoryFilter,
    ProductFilter,
    ProductTypeFilter,
)
from shuup.campaigns.models.matching import update_matching_catalog_filters


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.resave_campaigns()
        self.rebuild_cache()

    def rebuild_cache(self):
        filters = list(
            chain(
                ProductTypeFilter.objects.all(),
                ProductFilter.objects.all(),
                CategoryFilter.objects.all(),
                CatalogFilter.objects.all(),
            )
        )

        entry_count = len(filters)

        for i, entry in enumerate(filters):
            update_matching_catalog_filters(entry)
            print("Recaching filter %d / %d..." % (i + 1, entry_count))  # noqa

    def resave_campaigns(self):
        campaigns = list(chain(BasketCampaign.objects.all(), CatalogCampaign.objects.all()))

        entry_count = len(campaigns)

        for i, entry in enumerate(campaigns):
            entry.save()
            print("Recaching campaign %d / %d..." % (i + 1, entry_count))  # noqa
