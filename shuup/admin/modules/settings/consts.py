# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.

# Import constants from core to maintain backward compatibility
from shuup.core.constants import (
    ORDER_REFERENCE_NUMBER_LENGTH_FIELD,
    ORDER_REFERENCE_NUMBER_METHOD_FIELD,
    ORDER_REFERENCE_NUMBER_PREFIX_FIELD,
)

# Re-export for backward compatibility
__all__ = [
    "ORDER_REFERENCE_NUMBER_LENGTH_FIELD",
    "ORDER_REFERENCE_NUMBER_METHOD_FIELD",
    "ORDER_REFERENCE_NUMBER_PREFIX_FIELD",
]
