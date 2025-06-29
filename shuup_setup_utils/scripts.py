# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
"""
Scripts for Shuup setup utilities.
"""
from .resource_building import Options, build_resources


def build_resources_main():
    """Main entry point for building resources."""
    options = Options()
    options.ci = True  # Set CI flag by default
    build_resources(options)


if __name__ == "__main__":
    build_resources_main()
