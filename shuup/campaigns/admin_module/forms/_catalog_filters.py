from shuup.campaigns.models.catalog_filters import CategoryFilter, ProductFilter, ProductTypeFilter

from ._base import BaseRuleModelForm


class ProductTypeFilterForm(BaseRuleModelForm):
    class Meta(BaseRuleModelForm.Meta):
        model = ProductTypeFilter


class ProductFilterForm(BaseRuleModelForm):
    class Meta(BaseRuleModelForm.Meta):
        model = ProductFilter


class CategoryFilterForm(BaseRuleModelForm):
    class Meta(BaseRuleModelForm.Meta):
        model = CategoryFilter
