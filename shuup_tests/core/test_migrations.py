# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from django.core.management import call_command

import pytest
from six import StringIO


@pytest.mark.django_db
def test_makemigrations():
    out = StringIO()
    call_command("makemigrations", "--dry-run", stdout=out)
    assert "No changes detected" in out.getvalue()
