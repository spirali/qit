
from qit.base.expression import Expression
from qit.base.exception import InvalidConstant
from qit.base.exception import QitException

class Atom(Expression):

    def is_atom(self):
        return True


class Variable(Atom):

    def __init__(self, type, name):
        super().__init__(type)
        self.name = name

    def is_variable(self):
        return True

    def get_code(self, builder):
        return self.name

    def __repr__(self):
        return "Variable({}, {})".format(self.type, repr(self.name))


def sort_variables(variables):
    return sorted(variables, key=lambda v: v.name)


def validate_variables(variables):
    tmp = list(variables)
    tmp.sort(key=lambda v: v.name)
    for i, v in enumerate(tmp[:-1]):
        if v.name == tmp[i+1].name:
            raise QitException(
                    "Variable '{0}.name' was used with two different types:"
                    "{0.type} and {1.type}".format(v, tmp[i+1]))

def assign_values(variables, args):
    result = {}
    for v in variables:
        value = args.get(v.name)
        if value is None:
            raise QitException("Unbound variable {}".format(v.name))
        result[v] = v.type.check_value(args[v.name])
    return result


class Constant(Atom):

    def __init__(self, type, value):
        super().__init__(type)
        if not type.is_python_instance(value):
            raise InvalidConstant(type, value)
        self.value = value

    def get_code(self, builder):
        return self.type.make_instance(builder, self.value)
