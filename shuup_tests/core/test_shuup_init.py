# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from django.core.management import call_command
from django.utils.translation import activate

import pytest

from shuup.core.models import Currency, Shop, Supplier


@pytest.mark.django_db
def test_shuup_init():
    activate("en")

    # Clean up extra currencies from previous tests to ensure test isolation
    default_currency = Currency.objects.filter(code="EUR").first()
    if default_currency:
        # Keep only the default EUR currency, delete others
        Currency.objects.exclude(id=default_currency.id).delete()
    else:
        # If no EUR currency, keep only the first one and delete others
        first_currency = Currency.objects.first()
        if first_currency:
            Currency.objects.exclude(id=first_currency.id).delete()

    assert Currency.objects.count() == 1
    assert Shop.objects.filter(identifier="default").exists()  # Tests init
    assert not Supplier.objects.first()
    call_command("shuup_init")
    assert Supplier.objects.first()
    assert Currency.objects.count() == 7
