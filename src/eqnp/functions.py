#
# eqnp - functions.py
#
# Copyright (C) 2022 Kian Kasad
#
# This file is made available under a modified BSD license. See the provided
# LICENSE file for more information.
#
# SPDX-License-Identifier: BSD-2-Clause-Patent
#

from abc import ABC, abstractmethod
from .expressions import *

class Function(UnaryExpression, ABC):
    pass

# Define exports
__all__ = [
    'Function',
]
