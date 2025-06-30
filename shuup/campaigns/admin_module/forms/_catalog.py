from shuup.campaigns.models.campaigns import CatalogCampaign

from ._base import BaseCampaignForm


class CatalogCampaignForm(BaseCampaignForm):
    class Meta(BaseCampaignForm.Meta):
        model = CatalogCampaign
        exclude = BaseCampaignForm.Meta.exclude + ["filters", "coupon"]
