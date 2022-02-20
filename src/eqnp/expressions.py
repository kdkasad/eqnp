#
# eqnp - expressions.py
#
# Copyright (C) 2022 Kian Kasad
#
# This file is made available under a modified BSD license. See the provided
# LICENSE file for more information.
#
# SPDX-License-Identifier: BSD-2-Clause-Patent
#

from abc import ABC, abstractmethod

class VariableMap:
    """
    Maps variables to their values.
    Currently is no more than a wrapper around a dict, but may be expanded upon
    later, so it exists in its own class.
    """
    def __init__(self, initialMap: dict):
        self.map = initialMap

    def set(self, name: str, value):
        """
        Set the value of a variable.

        name: name of variable (str)
        value: value of variable (Expression)
        """
        self.map[name] = value

    def remove(self, name: str):
        """
        Unsets a variable.
        """
        del self.map[name]

    def get(self, name: str):
        """
        Gets the value of a variable.
        """
        return self.map[name]

class Expression(ABC):
    """
    Expression base class.

    Everything in eqnp is represented as a tree of Expressions. Each elementary
    operation is its own Expression subclass, as well as Numbers and Variables.
    Functions may be implemented later, too.

    Note: Expression is an abstract class. Only its subclasses can be
    instantiated.
    """

    def __eq__(self, other) -> bool:
        if isinstance(other, type(self)):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    @abstractmethod
    def evaluate(self, vm: VariableMap = None):
        """
        Calculate the value of an expression.

        Any variable used in the expression tree being evaluated must be
        defined in the variable map.

        vm: (VariableMap) a map of variables to their values.
        """
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass

    @abstractmethod
    def differentiate(self, respectTo: str, vm: VariableMap):
        """
        Calculate the derivative of the expression tree with respect to a given
        variable.

        respectTo: (str) the variable to derive with respect to. E.g. if
        respectTo is 'x', the derivative of x will be 1 and every other
        variable/expression will be differentiated with respect to x.

        vm: (VariableMap) map of variables to their values. Same as for
        Expression.evaluate().

        Note: the returned result is not simplified.
        """
        pass

class Variable(Expression):
    """
    Represents a variable.
    """
    def __init__(self, name: str):
        self.name = name

    def evaluate(self, vm: VariableMap):
        # TODO: catch errors
        if vm == None:
            raise ValueError(f'No value for variable {self.name}')
        return vm.get(self.name).evaluate(vm)

    def __repr__(self) -> str:
        return self.name

    def differentiate(self, respectTo: str, vm: VariableMap) -> Expression:
        if self.name == respectTo:
            return Number(1)
        elif vm == None:
            raise ValueError(f'No value for variable {self.name}')
        else:
            return vm.get(self.name).differentiate(respectTo, vm)

class UnaryExpression(Expression, ABC):
    """
    Abstract class representing an expression with one child expression.
    """
    def __init__(self, value: Expression):
        self.value = value

    def __repr__(self):
        return f'{type(self).__name__}({self.value})'

class BinaryExpression(Expression, ABC):
    """
    Abstract class respresenting an expression with two child expressions.
    """
    def __init__(self, left: Expression, right: Expression):
        self.left = left
        self.right = right

    def __repr__(self):
        return f'{type(self).__name__}({self.left}, {self.right})'

class Number(Expression):
    """
    Represents a constant number. Can be an integer or a floating-point number.
    """
    def __init__(self, value):
        self.value = value

    def evaluate(self, vm: VariableMap = None):
        return self.value

    def __repr__(self):
        return str(self.value)

    def __eq__(self, other):
        # Allow comparison with a plain number type
        if isinstance(other, int) or isinstance(other, float):
            return self.value == other
        return super().__eq__(other)

    def differentiate(self, respectTo: str, vm: VariableMap) -> Expression:
        return Number(0)

class Addition(BinaryExpression):
    """
    Represents the addition operation.

    Evaluating an addition expression returns the sum of the two child
    expressions' evaluations.
    """
    def evaluate(self, vm: VariableMap = None):
        return self.left.evaluate(vm) + self.right.evaluate(vm)

    def differentiate(self, respectTo: str, vm: VariableMap) -> Expression:
        return Addition(
            self.left.differentiate(respectTo, vm),
            self.right.differentiate(respectTo, vm)
        )

    def simplify(self, vm: VariableMap = None):
        self.left = self.left.simplify(vm)
        self.right = self.right.simplify(vm)

        # Simplify x/a + y/a to (x-y)/a
        if isinstance(self.left, Division) and isinstance(self.right, Division) \
                and self.left.right.evaluate(vm) == self.right.right.evaluate(vm):
            return Division(Addition(self.left.left, self.right.left), self.left.right)

        return self

    def __eq__(self, other) -> bool:
        # (a + b) == (b + a)
        if isinstance(other, type(self)):
            return (self.left == other.left and self.right == other.right) \
                or (self.left == other.right and self.right == other.left)
        return super().__eq__(other)

class Subtraction(BinaryExpression):
    """
    Represents the subtraction operation.

    Evaluating an subtraction expression returns the difference of the two
    child expressions' evaluations.
    """
    def evaluate(self, vm: VariableMap = None):
        return self.left.evaluate(vm) - self.right.evaluate(vm)

    def differentiate(self, respectTo: str, vm: VariableMap) -> Expression:
        return Subtraction(
            self.left.differentiate(respectTo, vm),
            self.right.differentiate(respectTo, vm)
        )

    def simplify(self, vm: VariableMap = None):
        self.left = self.left.simplify(vm)
        self.right = self.right.simplify(vm)

        # Simplify x/a - y/a to (x-y)/a
        if isinstance(self.left, Division) and isinstance(self.right, Division) \
                and self.left.right.evaluate(vm) == self.right.right.evaluate(vm):
            return Division(Subtraction(self.left.left, self.right.left), self.left.right)

        return self

class Multiplication(BinaryExpression):
    """
    Represents the multiplication operation.

    Evaluating an multiplication expression returns the product of the two
    child expressions' evaluations.
    """
    def evaluate(self, vm: VariableMap = None):
        return self.left.evaluate(vm) * self.right.evaluate(vm)

    def differentiate(self, respectTo: str, vm: VariableMap) -> Expression:
        return Addition(
            Multiplication(
                self.left,
                self.right.differentiate(respectTo, vm)
            ),
            Multiplication(
                self.right,
                self.left.differentiate(respectTo, vm)
            )
        )

    def simplify(self, vm: VariableMap = None):
        self.left = self.left.simplify(vm)
        self.right = self.right.simplify(vm)

        # Identities
        if self.left == 0 or self.right == 0:
            return Number(0)
        if self.left == 1:
            return self.right
        if self.right == 1:
            return self.left

        # Simplify y*(x/y) to x
        if isinstance(self.left, Division) and self.left.right.evaluate(vm) == self.right.evaluate(vm):
            return self.left.left
        if isinstance(self.right, Division) and self.right.right.evaluate(vm) == self.left.evaluate(vm):
            return self.right.left

        # Simplify x^a * x^b to x^(a+b)
        if isinstance(self.left, Exponent) and isinstance(self.right, Exponent) \
                and self.left.left.evaluate(vm) == self.right.left.evaluate(vm):
            return Exponent(self.left.left, Addition(self.left.right, self.right.right))

        return self

    def __eq__(self, other) -> bool:
        # (a * b) == (b * a)
        if isinstance(other, type(self)):
            return (self.left == other.left and self.right == other.right) \
                or (self.left == other.right and self.right == other.left)
        return super().__eq__(other)

class Division(BinaryExpression):
    """
    Represents the division operation.

    Evaluating an division expression returns the result of the first
    child expression's evaluation divided by that of the second child
    expression.
    """
    def evaluate(self, vm: VariableMap = None):
        return self.left.evaluate(vm) / self.right.evaluate(vm)

    def differentiate(self, respectTo: str, vm: VariableMap) -> Expression:
        return Division(
            Subtraction(
                Multiplication(
                    self.left.differentiate(respectTo, vm),
                    self.right
                ),
                Multiplication(
                    self.left,
                    self.right.differentiate(respectTo, vm)
                )
            ),
            Exponent(
                self.right,
                Number(2)
            )
        )

    def simplify(self, vm: VariableMap = None):
        self.left = self.left.simplify()
        self.right = self.right.simplify()

        # Identities
        if self.left == 0:
            return Number(0)
        if self.right == 1:
            return self.left

        # Simplify (x*y)/y to x
        if isinstance(self.left, Multiplication) and self.left.left == self.right:
            return self.left
        if isinstance(self.left, Multiplication) and self.left.right == self.right:
            return self.left

        # Simplify (x^a) / (x^b) to x^(a-b)
        if isinstance(self.left, Exponent) and isinstance(self.right, Exponent) \
                and self.left.left.evaluate(vm) == self.right.left.evaluate(vm):
            return Exponent(self.left.left, Subtraction(self.left.right, self.right.right))

        return self

class Exponent(BinaryExpression):
    """
    Represents the exponentiation operation.

    Evaluating an exponent expression returns the value of the first child
    expression's value to the power of the second child expression's value.
    """
    def evaluate(self, vm: VariableMap = None):
        return self.left.evaluate(vm) ** self.right.evaluate(vm)

    def differentiate(self, respectTo: str, vm: VariableMap) -> Expression:
        return Multiplication(
            Multiplication(
                self.right,
                Exponent(
                    self.left,
                    Subtraction(
                        self.right,
                        Number(1)
                    )
                )
            ),
            self.left.differentiate(respectTo, vm)
        )

    def simplify(self, vm: VariableMap = None):
        self.left = self.left.simplify(vm)
        self.right = self.right.simplify(vm)

        # Simplify (x^a)^b to x^(ab)
        if isinstance(self.left, Exponent):
            return Exponent(self.left.left, Multiplication(self.left.right, self.right))

        return self

def Root(base: Expression, num: Expression) -> Expression:
    """
    Provides the root expression.
    This is merely an alias for num^(1/base), or
    Exponent(num, Division(1, base)).
    """
    return Exponent(
        num,
        Division(
            Number(1),
            base
        )
    )
