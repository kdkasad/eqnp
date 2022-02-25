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

class AbsoluteValue(Function):
    def __repr__(self):
        return f'|{self.value}|'

    def evaluate(self, vm: VariableMap = None):
        return abs(self.value.evaluate(vm))

    def differentiate(self, respectTo: str, vm: VariableMap = None):
        return Multiplication(
            Division(self, self.value),
            self.value.differentiate(respectTo, vm)
        )

    def simplify(self):
        self.value = self.value.simplify()

        # For constants > 0, return the constant
        if isinstance(self.value, Number) and self.value.evaluate() >= 0:
            return self.value

        # Even exponents are never negative
        if isinstance(self.value, Exponent) \
                and isinstance(self.value.right, Number) \
                and self.value.right.evaluate() % 2 == 0:
            return self.value

        return self

# Alias for AbsoluteValue
ABS = AbsoluteValue

# Define exports
__all__ = [
    'ABS',
    'AbsoluteValue',
    'Function',
]
