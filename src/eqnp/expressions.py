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
    def __hash__(self):
        pass

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

    @abstractmethod
    def simplify(self):
        """
        Attempts to simplify the expression as much as possible
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

    def __hash__(self):
        return hash(self.name)

    def differentiate(self, respectTo: str, vm: VariableMap) -> Expression:
        if self.name == respectTo:
            return Number(1)
        elif vm == None:
            raise ValueError(f'No value for variable {self.name}')
        else:
            return vm.get(self.name).differentiate(respectTo, vm)

    def simplify(self):
        return self

class UnaryExpression(Expression, ABC):
    """
    Abstract class representing an expression with one child expression.
    """
    def __init__(self, value: Expression):
        self.value = value

    def __repr__(self):
        return f'{type(self).__name__}({self.value})'

    def __hash__(self):
        return hash(self.value)

class BinaryExpression(Expression, ABC):
    """
    Abstract class respresenting an expression with two child expressions.
    """
    def __init__(self, left: Expression, right: Expression):
        self.left = left
        self.right = right

    def __repr__(self):
        return f'{type(self).__name__}({self.left}, {self.right})'

    def __hash__(self):
        return hash((self.left, self.right))

class MultiOperandExpression(Expression, ABC):
    """
    Abstract class representing an expression with two or more child
    expressions. Should only be used for expressions in which the order of
    operands does not matter, e.g. addition and multiplication.
    """
    def __init__(self, *args):
        if len(args) < 2:
            raise TypeError('MultiOperandExpression.__init__() requires at least two operands')
        self.operands = list(args)

    def __repr__(self):
        return f'{type(self).__name__}({", ".join([str(x) for x in self.operands])})'

    def __eq__(self, other) -> bool:
        """
        Checks if all the operands in this object are contained in the other
        object. Order does not matter.
        """
        if isinstance(other, type(self)):
            if len(self.operands) != len(other.operands):
                return False
            return set(self.operands) == set(other.operands)
        return super().__eq__(other)

    def __hash__(self):
        return hash(tuple(self.operands))

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

    def __eq__(self, other) -> bool:
        # Allow comparison with a plain number type
        if isinstance(other, int) or isinstance(other, float):
            return self.value == other
        return super().__eq__(other)

    def __hash__(self):
        return hash(self.value)

    def differentiate(self, respectTo: str, vm: VariableMap) -> Expression:
        return Number(0)

    def simplify(self):
        return self

class Addition(MultiOperandExpression):
    """
    Represents the addition operation.

    Evaluating an addition expression returns the sum of the two child
    expressions' evaluations.
    """
    def evaluate(self, vm: VariableMap = None):
        return sum(self.operands)

    def differentiate(self, respectTo: str, vm: VariableMap) -> Expression:
        return Addition(*[x.differentiate(respectTo, vm) for x in self.operands])

    def simplify(self):
        self.operands = [x.simplify() for x in self.operands]

        # If all operands are numbers, evaluate the expression
        if all(isinstance(x, Number) for x in self.operands):
            return Number(self.evaluate(None))

        # Simplify x/a + y/a to (x-y)/a
        if all(isinstance(x, Division) for x in self.operands):
            denominators = [x.right for x in self.operands]
            if all(x == denominators[0] for x in denominators):
                return Division(Addition(x.left for x in self.operands), denominators[0])

        return self

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

    def simplify(self):
        self.left = self.left.simplify()
        self.right = self.right.simplify()

        # If both operands are numbers, evaluate them
        if isinstance(self.left, Number) and isinstance(self.right, Number):
            return Number(self.evaluate(None))

        # Simplify x/a - y/a to (x-y)/a
        if isinstance(self.left, Division) and isinstance(self.right, Division) \
                and self.left.right == self.right.right:
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
        raise NotImplementedError('Differentiation of multiplication expressions has not been implemented')

    def simplify(self):
        self.operands = [x.simplify() for x in operands]

        # Identities
        for operand in self.operands:
            if operand == 0:
                return Number(0)

        # x * 1 = x
        self.operands = [x for x in self.operands if x != 1]

        # If both operands are numbers, evaluate them
        if all(isinstance(x, Number) for x in self.operands):
            return Number(self.evaluate(None))

        # When there are only two factors
        # TODO: implement this logic for 3+ factor expressions
        if len(self.operands) == 2:
            left = self.operands[0]
            right = self.operands[1]

            # Simplify y*(x/y) to x
            if isinstance(left, Division) and left.right == right:
                return left.left
            if isinstance(right, Division) and right.right == left:
                return right.left

            # Simplify x^a * x^b to x^(a+b)
            if isinstance(left, Exponent) and isinstance(right, Exponent) \
                    and left.left == right.left:
                return Exponent(left.left, Addition(left.right, right.right))

        return self

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

    def simplify(self):
        self.left = self.left.simplify()
        self.right = self.right.simplify()

        # Identities
        if self.left == 0:
            return Number(0)
        if self.right == 1:
            return self.left

        # If both operands are numbers, evaluate them
        if isinstance(self.left, Number) and isinstance(self.right, Number):
            return Number(self.evaluate(None))

        # Simplify (x*y)/y to x
        if isinstance(self.left, Multiplication) and self.left.left == self.right:
            return self.left
        if isinstance(self.left, Multiplication) and self.left.right == self.right:
            return self.left

        # Simplify (x^a) / (x^b) to x^(a-b)
        if isinstance(self.left, Exponent) and isinstance(self.right, Exponent) \
                and self.left.left == self.right.left:
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

    def simplify(self):
        self.left = self.left.simplify()
        self.right = self.right.simplify()

        # 0^a == 0
        if self.left == 0:
            return Number(0)

        # x^0 == 1
        if self.right == 0:
            return Number(1)

        # x^1 == x
        if self.right == 1:
            return self.left

        # If both operands are numbers, evaluate them
        if isinstance(self.left, Number) and isinstance(self.right, Number):
            return Number(self.evaluate(None))

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
