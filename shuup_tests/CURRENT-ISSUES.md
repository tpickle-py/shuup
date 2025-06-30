FAILED shuup_tests/admin/test_attributes_view.py::test_attribute_edit_view - AttributeError: 'AttributeChoiceOptionFormSet' object has no attribute 'can_delete_extra'
FAILED shuup_tests/admin/test_media_module.py::test_media_view_images[False-0] - AttributeError: 'Folder' object has no attribute 'get_children'
FAILED shuup_tests/admin/test_media_module.py::test_media_view_images[True-1] - AttributeError: 'Folder' object has no attribute 'get_children'
FAILED shuup_tests/admin/test_media_module.py::test_new_folder - AttributeError: 'Folder' object has no attribute 'move_to'
FAILED shuup_tests/admin/test_media_module.py::test_get_folder - AttributeError: 'Folder' object has no attribute 'get_children'
FAILED shuup_tests/admin/test_media_module.py::test_upload_invalid_filetype - assert "extension 'exe' is not allowed" in 'File extension “exe” is not allowed. Allowed extensions are: pdf, ttf, eot, woff, woff2, otf.'
FAILED shuup_tests/admin/test_media_module.py::test_get_folders - AttributeError: type object 'Folder' has no attribute '_tree_manager'
FAILED shuup_tests/admin/test_media_module.py::test_get_folders_without_view_all_permission - AttributeError: type object 'Folder' has no attribute '_tree_manager'
FAILED shuup_tests/admin/test_media_module.py::test_deleting_mid_folder - AttributeError: type object 'Folder' has no attribute '_tree_manager'
FAILED shuup_tests/admin/test_media_module.py::test_delete_protected_folder - AttributeError: 'Folder' object has no attribute 'get_children'
FAILED shuup_tests/admin/test_media_module_multi_shop.py::test_media_view_images - AttributeError: 'Folder' object has no attribute 'get_children'
FAILED shuup_tests/admin/test_order_shipments.py::test_order_shipments - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/admin/test_password_reset.py::test_reset_admin_user_password_errors - assert 'The two password fields didn&#x27;t match.' in '<!doctype html>\n<html lang="en">\n    <head>\n        <meta charset="utf-8">\n        \n        <title>Default &dash; Reset Password\n        </title>\n\n        \n\n        <meta name="viewport" content="width=device-width, initial-scale=1.0">\n        <link rel="icon" type="image/x-icon" href="/static/shu...
FAILED shuup_tests/admin/test_service_behavior_components.py::test_behavior_add_save[PaymentMethodEditView-PaymentMethod-get_default_payment_method-payment_processor] - AttributeError: 'BehaviorFormSet' object has no attribute 'can_delete_extra'
FAILED shuup_tests/admin/test_service_behavior_components.py::test_behavior_add_save[ShippingMethodEditView-ShippingMethod-get_default_shipping_method-carrier] - AttributeError: 'BehaviorFormSet' object has no attribute 'can_delete_extra'
FAILED shuup_tests/admin/test_service_behavior_components.py::test_behavior_delete_save[PaymentMethodEditView-PaymentMethod-get_default_payment_method-payment_processor] - AttributeError: 'BehaviorFormSet' object has no attribute 'can_delete_extra'
FAILED shuup_tests/admin/test_service_behavior_components.py::test_behavior_delete_save[ShippingMethodEditView-ShippingMethod-get_default_shipping_method-carrier] - AttributeError: 'BehaviorFormSet' object has no attribute 'can_delete_extra'
FAILED shuup_tests/campaigns/test_basket_campaign_admin.py::test_rules_and_effects - AttributeError: 'BasketConditionsFormSet' object has no attribute 'can_delete_extra'
FAILED shuup_tests/campaigns/test_basket_campaigns.py::test_basket_campaign_module_case1 - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/campaigns/test_basket_campaigns.py::test_basket_category_discount - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/campaigns/test_basket_campaigns.py::test_basket_campaign_case2 - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/campaigns/test_basket_category_products_campaigns.py::test_category_products_effect_with_amount - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/campaigns/test_basket_category_products_campaigns.py::test_category_products_effect_with_percentage - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/campaigns/test_basket_product_conditions.py::test_basket_total_value_conditions - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/campaigns/test_catalog_campaign_admin.py::test_campaign_end_date - assert 'Campaign end date can&#39;t be before a start date.' in '<!doctype html>\n<html lang="en">\n    <head>\n        <meta charset="utf-8">\n        \n        <title>Default &dash; Catalog Campaign: Test Campaign\n            \n        </title>\n\n        \n\n        <meta name="viewport" content="width=device-width, initial-scale=1.0">\n        <link rel="ico...
FAILED shuup_tests/campaigns/test_discount_codes.py::test_campaign_with_coupons1 - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/campaigns/test_discount_codes.py::test_campaign_with_coupons2 - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/campaigns/test_effects.py::test_basket_free_product - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/campaigns/test_effects.py::test_basket_free_product_coupon - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/campaigns/test_effects.py::test_productdiscountamount - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/campaigns/test_effects.py::test_productdiscountamount_with_minimum_price[True] - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/campaigns/test_effects.py::test_productdiscountamount_with_minimum_price[False] - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/campaigns/test_effects.py::test_product_category_discount_amount_with_minimum_price - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/campaigns/test_effects.py::test_productdiscountamount_greater_then_products - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/campaigns/test_effects.py::test_product_category_discount_amount_greater_then_products[True] - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/campaigns/test_effects.py::test_product_category_discount_amount_greater_then_products[False] - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/campaigns/test_effects.py::test_product_category_discount_percentage_greater_then_products[True] - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/campaigns/test_effects.py::test_product_category_discount_percentage_greater_then_products[False] - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/campaigns/test_effects.py::test_discount_no_limits[True] - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/campaigns/test_effects.py::test_discount_no_limits[False] - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/campaigns/test_effects.py::test_undiscounted_effects[True] - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/campaigns/test_effects.py::test_undiscounted_effects[False] - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/campaigns/test_filters.py::test_productfilter_works - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/campaigns/test_supplier_campaigns.py::test_basket_campaign_with_multiple_supppliers - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/campaigns/test_supplier_campaigns.py::test_basket_campaign_with_multiple_supppliers_sharing_product - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/core/test_basket_commands.py::test_add_product - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/core/test_basket_commands.py::test_add_product_new_line - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/core/test_basket_commands.py::test_add_product_with_extra_parent_line - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/core/test_basket_commands.py::test_command_middleware - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/core/test_foreignkeys.py::test_shipping_method_removal - RecursionError: maximum recursion depth exceeded while calling a Python object
FAILED shuup_tests/core/test_foreignkeys.py::test_payment_method_removal - RecursionError: maximum recursion depth exceeded while calling a Python object
FAILED shuup_tests/core/test_foreignkeys.py::test_customer_tax_group_removal - RecursionError: maximum recursion depth exceeded while calling a Python object
FAILED shuup_tests/core/test_order_creator.py::test_order_customer_groups - RecursionError: maximum recursion depth exceeded while calling a Python object
FAILED shuup_tests/core/test_order_creator.py::test_order_creator_account_manager - RecursionError: maximum recursion depth exceeded
FAILED shuup_tests/core/test_order_languages.py::test_order_language_fallbacks[en] - AssertionError: assert 'bew' == 'en'
FAILED shuup_tests/core/test_order_languages.py::test_order_language_fallbacks[fi] - AssertionError: assert 'bew' == 'fi'
FAILED shuup_tests/core/test_order_languages.py::test_order_language_fallbacks[sv] - AssertionError: assert 'bew' == 'sv'
FAILED shuup_tests/core/test_order_languages.py::test_order_language_fallbacks[ja] - AssertionError: assert 'bew' == 'ja'
FAILED shuup_tests/core/test_order_languages.py::test_order_language_fallbacks[zh-hans] - AssertionError: assert 'bew' == 'zh-hans'
FAILED shuup_tests/core/test_order_languages.py::test_order_language_fallbacks[pt-br] - AssertionError: assert 'bew' == 'pt-br'
FAILED shuup_tests/core/test_order_languages.py::test_order_language_fallbacks[it] - AssertionError: assert 'bew' == 'it'
FAILED shuup_tests/core/test_products_in_shops.py::test_product_order_multiple - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/core/test_sales_unit.py::test_sales_unit_display_unit - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/core/test_template_tags.py::test_money_formatter_en - AssertionError: assert 'SEK29.99' == 'kr29.99'
FAILED shuup_tests/core/test_template_tags.py::test_money_formatter_digit_grouping - AssertionError: assert '\u200f12,345,678.00\xa0US$' == 'US$\xa012,345,678.00'
FAILED shuup_tests/core/test_units.py::test_unit_interface_init_without_args - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/core/test_units.py::test_unit_interface_init_from_internal_unit - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/core/test_units.py::test_unit_interface_render_quantity_pieces - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/core/test_units.py::test_unit_interface_render_quantity_small_display_prec - TypeError: ("Empty locale identifier value: None\n\nIf you didn't explicitly pass an empty value to a Babel function, this could be caused by there being no suitable locale environment variables for the API you tried to use.",)
FAILED shuup_tests/core/test_units.py::test_unit_interface_render_quantity_translations - TypeError: ("Empty locale identifier value: None\n\nIf you didn't explicitly pass an empty value to a Babel function, this could be caused by there being no suitable locale environment variables for the API you tried to use.",)
FAILED shuup_tests/core/test_units.py::test_unit_interface_render_quantity_internal_pieces - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/core/test_units.py::test_unit_interface_get_per_values - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/core/test_units.py::test_sales_unit_as_display_unit - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/core/test_units.py::test_sales_unit_as_display_unit_allow_bare_number - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/core/test_units.py::test_pieces_sales_unit - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/front/test_basket.py::test_basket - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/front/test_basket_commands.py::test_add_and_remove_and_clear - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/front/test_basket_commands.py::test_variation - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/front/test_basket_commands.py::test_complex_variation - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/front/test_basket_commands.py::test_basket_update - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/front/test_basket_commands.py::test_basket_partial_quantity_update - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/front/test_basket_commands.py::test_basket_partial_quantity_update_all_product_counts - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/front/test_basket_commands.py::test_basket_update_with_package_product - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/front/test_basket_commands.py::test_parallel_baskets - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/front/test_basket_line_descriptor.py::test_basket_line_descriptor - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/front/test_checkout_flow.py::test_basic_order_flow[False-True] - assert []
FAILED shuup_tests/front/test_checkout_flow.py::test_basic_order_flow[True-True] - assert []
FAILED shuup_tests/front/test_checkout_flow.py::test_basic_order_flow[False-False] - assert []
FAILED shuup_tests/front/test_checkout_flow.py::test_basic_order_flow[True-False] - assert []
FAILED shuup_tests/front/test_checkout_flow.py::test_order_flow_with_phases[get_default_shipping_method-None-_get_payment_method_with_phase-payment_data0-True] - assert []
FAILED shuup_tests/front/test_checkout_flow.py::test_order_flow_with_phases[get_default_shipping_method-None-_get_payment_method_with_phase-payment_data1-False] - assert []
FAILED shuup_tests/front/test_checkout_flow.py::test_order_flow_with_phases[_get_shipping_method_with_phase-shipping_data2-get_default_payment_method-None-False] - assert []
FAILED shuup_tests/front/test_checkout_flow.py::test_order_flow_with_phases[_get_shipping_method_with_phase-shipping_data3-_get_payment_method_with_phase-payment_data3-False] - assert []
FAILED shuup_tests/front/test_checkout_flow.py::test_checkout_empty_basket - assert []
FAILED shuup_tests/front/test_methods_phase.py::test_method_phase_basic[get_shipping_method-data0-id_shipping_method] - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/front/test_methods_phase.py::test_method_phase_basic[get_payment_method-data1-id_payment_method] - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/front/test_product_price.py::test_product_price_get_quantity_with_display_unit[0] - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/front/test_product_price.py::test_product_price_get_quantity_with_display_unit[2] - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/front/test_registration.py::test_company_registration[False-True] - KeyError: 'email'
FAILED shuup_tests/front/test_registration.py::test_company_registration[True-True] - KeyError: 'email'
FAILED shuup_tests/front/test_registration_multishop.py::test_registration_company_multiple_shops - KeyError: 'email'
FAILED shuup_tests/front/test_saved_carts.py::test_save_cart - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/front/test_saved_carts.py::test_cart_list - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/front/test_saved_carts.py::test_cart_detail - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/front/test_saved_carts.py::test_cart_delete - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/front/test_saved_carts.py::test_cart_add_all - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/front/test_saved_carts.py::test_cart_add_all_with_errors - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/front/test_stored_basket.py::test_stored_basket_list_view[False] - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/front/test_stored_basket.py::test_stored_basket_list_view[True] - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/front/test_stored_basket.py::test_stored_basket_detail_view - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/front/test_stored_basket.py::test_anonymous_stored_basket_detail_view - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/front/test_thumbnails_templatetag.py::test_thumbnailing_carbage - easy_thumbnails.engine.NoSourceGenerator: Tried 2 source generators with no success
FAILED shuup_tests/functional/test_order_edit_with_coupons.py::test_order_edit_with_coupon - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/functional/test_order_edit_with_coupons.py::test_campaign_with_non_active_coupon - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/functional/test_refunds.py::test_create_full_refund[True] - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/functional/test_refunds.py::test_create_full_refund[False] - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/functional/test_refunds.py::test_create_refund_line_by_line[True] - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/functional/test_refunds.py::test_create_refund_line_by_line[False] - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/functional/test_refunds.py::test_create_refund_amount[True] - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/functional/test_refunds.py::test_create_refund_amount[False] - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/gdpr/test_admin_module.py::test_gdpr_admin_download_data - AttributeError: 'HttpResponse' object has no attribute '_headers'
FAILED shuup_tests/gdpr/test_front_views.py::test_serialize_data - AttributeError: 'HttpResponse' object has no attribute '_headers'
FAILED shuup_tests/importer/test_admin.py::test_download_examples - AttributeError: 'HttpResponse' object has no attribute '_headers'
FAILED shuup_tests/notify/test_order_notifications.py::test_basic_order_flow_not_registered[False] - assert []
FAILED shuup_tests/notify/test_order_notifications.py::test_basic_order_flow_not_registered[True] - assert []
FAILED shuup_tests/notify/test_order_notifications.py::test_basic_order_flow_registered - assert []
FAILED shuup_tests/simple_cms/test_children.py::test_visible_children - assert 'Jan 1, 2000, 12:00:00 AM' in '<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="utf-8">\n    <meta http-equiv="X-UA-Compatible" content="IE=edge">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    \n\n    \n    \n    \n\n    <meta property="og:site_name" content="Default">\n    <meta property="og:url" content="ht...
FAILED shuup_tests/supplier_prices/test_checkout_flow.py::test_order_flow_with_multiple_suppliers - TypeError: Abstract models cannot be instantiated.
FAILED shuup_tests/utils/test_i18n.py::test_get_language_name_1 - AssertionError: assert 'mandariiniki...kertaistettu)' == 'yksinkertaistettu kiina'
FAILED shuup_tests/utils/test_i18n.py::test_existing_languages - AssertionError: assert True == False
FAILED shuup_tests/utils/test_i18n.py::test_remove_extinct_languages - AssertionError: assert {'arn', 'bew'...i', 'is', ...} == {'en', 'fi', 'is', 'sv'}
FAILED shuup_tests/xtheme/test_extenders.py::test_extender_renders_main_menu - AssertionError: assert 'Test Link to Front' in ['\n Log in\n\n', '\n Forgot your password?\n                    ', '\n New user? Register here!\n                    ', '\n EN\n                \n', 'English (English)', 'Finnish (suomi)', ...]
