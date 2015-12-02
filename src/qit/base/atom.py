
from qit.base.expression import Expression
from qit.base.exception import InvalidConstant


class Atom(Expression):

    def is_atom(self):
        return True


class Variable(Atom):

    def __init__(self, type, name):
        super().__init__(type)
        self.name = name

    def is_variable(self):
        return True

    def build_value(self, builder):
        return self.name

    def get_variables(self):
        return frozenset((self,))

    def __repr__(self):
        return "Variable({}, {})".format(self.type, repr(self.name))


class Constant(Atom):

    def __init__(self, type, value):
        super().__init__(type)
        if not type.is_python_instance(value):
            raise InvalidConstant(type, value)
        self.value = value

    def build_value(self, builder):
        return self.type.build_constant(builder, self.value)

    def is_constant_value(self, value):
        return self.value == value

    def __repr__(self):
        return "Constant({}, {})".format(self.type, repr(self.value))
