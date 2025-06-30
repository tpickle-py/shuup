# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.

from shuup.utils.setup import Setup

from . import base_settings


def configure(setup):
    base_settings.configure(setup)
    # Add any development-specific overrides here if needed


globals().update(Setup.configure(configure))
