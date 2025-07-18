from shuup.apps import AppConfig
from shuup.apps.settings import validate_templates_configuration


class ShuupAdminAppConfig(AppConfig):
    name = "shuup.admin"
    verbose_name = "Shuup Admin"
    label = "shuup_admin"
    required_installed_apps = ["bootstrap3"]
    provides = {
        "admin_product_form_part": [
            "shuup.admin.modules.products.views.edit.ProductBaseFormPart",
            "shuup.admin.modules.products.views.edit.ShopProductFormPart",
            "shuup.admin.modules.products.views.edit.ProductAttributeFormPart",
            "shuup.admin.modules.products.views.edit.ProductImageMediaFormPart",
            "shuup.admin.modules.products.views.edit.ProductMediaFormPart",
        ],
        "admin_attribute_form_part": [
            "shuup.admin.modules.attributes.form_parts.AttributeBaseFormPart",
            "shuup.admin.modules.attributes.form_parts.AttributeChoiceOptionsFormPart",
        ],
        "admin_module": [
            "shuup.admin.modules.system:SystemModule",
            "shuup.admin.modules.products:ProductModule",
            "shuup.admin.modules.product_types:ProductTypeModule",
            "shuup.admin.modules.media:MediaModule",
            "shuup.admin.modules.orders:OrderModule",
            "shuup.admin.modules.orders:OrderStatusModule",
            "shuup.admin.modules.taxes:TaxModule",
            "shuup.admin.modules.categories:CategoryModule",
            "shuup.admin.modules.contacts:ContactModule",
            "shuup.admin.modules.contact_groups:ContactGroupModule",
            "shuup.admin.modules.contact_group_price_display:ContactGroupPriceDisplayModule",
            "shuup.admin.modules.currencies:CurrencyModule",
            "shuup.admin.modules.customers_dashboard:CustomersDashboardModule",
            "shuup.admin.modules.permission_groups:PermissionGroupModule",
            "shuup.admin.modules.users:UserModule",
            "shuup.admin.modules.service_providers:ServiceProviderModule",
            "shuup.admin.modules.services:PaymentMethodModule",
            "shuup.admin.modules.services:ShippingMethodModule",
            "shuup.admin.modules.attributes:AttributeModule",
            "shuup.admin.modules.sales_units:DisplayUnitModule",
            "shuup.admin.modules.sales_units:SalesUnitModule",
            "shuup.admin.modules.sales_dashboard:SalesDashboardModule",
            "shuup.admin.modules.shops:ShopModule",
            "shuup.admin.modules.manufacturers:ManufacturerModule",
            "shuup.admin.modules.suppliers:SupplierModule",
            "shuup.admin.modules.support:ShuupSupportModule",
            "shuup.admin.modules.settings.SettingsModule",
            "shuup.admin.modules.labels:LabelsModule",
            "shuup.admin.modules.menu:YourAdminMenuModule",
            "shuup.admin.modules.menu:SuperUserAdminMenuModule",
            "shuup.admin.modules.menu:StaffAdminMenuModule",
            "shuup.admin.modules.menu:SupplierAdminMenuModule",
        ],
        "admin_shop_form_part": ["shuup.admin.modules.settings.form_parts.OrderConfigurationFormPart"],
        "service_provider_admin_form": [
            "shuup.admin.modules.service_providers.forms:CustomCarrierForm",
            "shuup.admin.modules.service_providers.forms:CustomPaymentProcessorForm",
        ],
        "carrier_wizard_form_def": [
            "shuup.admin.modules.service_providers.wizard_form_defs:ManualShippingWizardFormDef"
        ],
        "payment_processor_wizard_form_def": [
            "shuup.admin.modules.service_providers.wizard_form_defs:ManualPaymentWizardFormDef"
        ],
        "service_behavior_component_form": [
            "shuup.admin.modules.services.forms:FixedCostBehaviorComponentForm",
            "shuup.admin.modules.services.forms:WaivingCostBehaviorComponentForm",
            "shuup.admin.modules.services.forms:WeightLimitsBehaviorComponentForm",
            "shuup.admin.modules.services.forms:GroupAvailabilityBehaviorComponentForm",
            "shuup.admin.modules.services.forms.StaffOnlyBehaviorComponentForm",
            "shuup.admin.modules.services.forms.OrderTotalLimitBehaviorComponentForm",
            "shuup.admin.modules.services.forms.CountryLimitBehaviorComponentForm",
        ],
        "service_behavior_component_form_part": [
            "shuup.admin.modules.services.weight_based_pricing.WeightBasedPricingFormPart"
        ],
        "admin_order_section": [
            "shuup.admin.modules.orders.sections:BasicDetailsOrderSection",
            "shuup.admin.modules.orders.sections:PaymentOrderSection",
            "shuup.admin.modules.orders.sections:LogEntriesOrderSection",
            "shuup.admin.modules.orders.sections:ShipmentSection",
            "shuup.admin.modules.orders.sections:AdminCommentSection",
            "shuup.admin.modules.orders.sections:OrderHistorySection",
        ],
        "admin_contact_section": [
            "shuup.admin.modules.contacts.sections:BasicInfoContactSection",
            "shuup.admin.modules.contacts.sections:AddressesContactSection",
            "shuup.admin.modules.contacts.sections:OrdersContactSection",
            "shuup.admin.modules.contacts.sections:MembersContactSection",
        ],
        "admin_product_section": ["shuup.admin.modules.products.sections:ProductOrdersSection"],
        "admin_order_toolbar_action_item": [
            "shuup.admin.modules.orders.toolbar:CreatePaymentAction",
            "shuup.admin.modules.orders.toolbar:SetPaidAction",
            "shuup.admin.modules.orders.toolbar:CreateRefundAction",
            "shuup.admin.modules.orders.toolbar:EditAddresses",
        ],
        "admin_model_url_resolver": ["shuup.admin.utils.urls.get_model_url"],
        "admin_browser_config_provider": ["shuup.admin.browser_config:DefaultBrowserConfigProvider"],
        "admin_supplier_form_part": [
            "shuup.admin.modules.suppliers.form_parts.SupplierBaseFormPart",
            "shuup.admin.modules.suppliers.form_parts.SupplierContactAddressFormPart",
        ],
        "user_list_mass_actions_provider": [
            "shuup.admin.modules.users.mass_actions.UserMassActionProvider",
        ],
        "admin_object_selector": [
            "shuup.admin.modules.attributes.object_selector.AttributeAdminObjectSelector",
            "shuup.admin.modules.categories.object_selector.CategoryAdminObjectSelector",
            "shuup.admin.modules.contacts.object_selector.ContactAdminObjectSelector",
            "shuup.admin.modules.contacts.object_selector.PersonContactAdminObjectSelector",
            "shuup.admin.modules.contacts.object_selector.CompanyContactAdminObjectSelector",
            "shuup.admin.modules.manufacturers.object_selector.ManufacturerAdminObjectSelector",
            "shuup.admin.modules.permission_groups.object_selector.PermissionGroupAdminObjectSelector",
            "shuup.admin.modules.product_types.object_selector.ProductTypeAdminObjectSelector",
            "shuup.admin.modules.products.object_selector.ProductAdminObjectSelector",
            "shuup.admin.modules.products.object_selector.ShopProductAdminObjectSelector",
            "shuup.admin.modules.services.object_selector.CarrierAdminObjectSelector",
            "shuup.admin.modules.services.object_selector.PaymentMethodAdminObjectSelector",
            "shuup.admin.modules.services.object_selector.ShippingMethodAdminObjectSelector",
            "shuup.admin.modules.shops.object_selector.ShopAdminObjectSelector",
            "shuup.admin.modules.suppliers.object_selector.SupplierAdminObjectSelector",
            "shuup.admin.modules.taxes.object_selector.CustomerTaxGroupAdminObjectSelector",
            "shuup.admin.modules.taxes.object_selector.TaxAdminObjectSelector",
            "shuup.admin.modules.taxes.object_selector.TaxClassAdminObjectSelector",
            "shuup.admin.modules.users.object_selector.UserAdminObjectSelector",
        ],
    }

    def ready(self):
        import shuup.admin.signal_handling  # noqa (F401)

        validate_templates_configuration()


default_app_config = "shuup.admin.ShuupAdminAppConfig"
