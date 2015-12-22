
from qit.base.expression import Expression


class Variable(Expression):

    def __init__(self, type, name):
        super().__init__(type)
        self.name = name

    def is_variable(self):
        return True

    def build(self, builder):
        return "qit_freevar_" + self.name

    def get_variables(self):
        return frozenset((self,))

    def __repr__(self):
        return "Variable({}, {})".format(self.type, repr(self.name))
