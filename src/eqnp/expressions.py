from abc import ABC, abstractmethod

class VariableMap:
    def __init__(self, initialMap: dict):
        self.map = initialMap

    def set(self, name: str, value):
        self.map[name] = value

    def remove(self, name: str):
        del self.map[name]

    def evaluate(self, name: str):
        return self.map[name].evaluate(self)

class Expression(ABC):
    @abstractmethod
    def evaluate(self, vm: VariableMap = None):
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass

    @abstractmethod
    def differentiate(self):
        pass

class Variable(Expression):
    def __init__(self, name: str):
        self.name = name

    def evaluate(self, vm: VariableMap):
        # TODO: catch errors
        if vm == None:
            raise ValueError(f'No value for variable {self.name}')
        return vm.evaluate(self.name)

    def __repr__(self) -> str:
        return self.name

    def differentiate(self) -> Expression:
        return Number(1)

class UnaryExpression(Expression, ABC):
    def __init__(self, value: Expression):
        self.value = value

    def __repr__(self):
        return f'{self.__class__.__name__}({self.value})'

class BinaryExpression(Expression, ABC):
    def __init__(self, left: Expression, right: Expression):
        self.left = left
        self.right = right

    def __repr__(self):
        return f'{self.__class__.__name__}({self.left}, {self.right})'

class Number(Expression):
    def __init__(self, value):
        self.value = value

    def evaluate(self, vm: VariableMap = None):
        return self.value

    def __repr__(self):
        return str(self.value)

    def differentiate(self) -> Expression:
        return Number(0)

class Addition(BinaryExpression):
    def evaluate(self, vm: VariableMap = None):
        return self.left.evaluate(vm) + self.right.evaluate(vm)

    def differentiate(self) -> Expression:
        return Addition(
            self.left.differentiate(),
            self.right.differentiate()
        )

class Subtraction(BinaryExpression):
    def evaluate(self, vm: VariableMap = None):
        return self.left.evaluate(vm) - self.right.evaluate(vm)

    def differentiate(self) -> Expression:
        return Subtraction(
            self.left.differentiate(),
            self.right.differentiate()
        )

class Multiplication(BinaryExpression):
    def evaluate(self, vm: VariableMap = None):
        return self.left.evaluate(vm) * self.right.evaluate(vm)

    def differentiate(self) -> Expression:
        return Addition(
            Multiplication(
                self.left,
                self.right.differentiate()
            ),
            Multiplication(
                self.right,
                self.left.differentiate()
            )
        )

class Division(BinaryExpression):
    def evaluate(self, vm: VariableMap = None):
        return self.left.evaluate(vm) / self.right.evaluate(vm)

    def differentiate(self) -> Expression:
        return Division(
            Subtraction(
                Multiplication(
                    self.left.differentiate(),
                    self.right
                ),
                Multiplication(
                    self.left,
                    self.right.differentiate()
                )
            ),
            Exponent(
                self.right,
                Number(2)
            )
        )

class Exponent(BinaryExpression):
    def evaluate(self, vm: VariableMap = None):
        return self.left.evaluate(vm) ** self.right.evaluate(vm)

    def differentiate(self):
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
            self.left.differentiate()
        )

# Root(base, num) is an alias for num^(1/base)
def Root(base: Expression, num: Expression) -> Expression:
    return Exponent(num, Division(Number(1), base))
