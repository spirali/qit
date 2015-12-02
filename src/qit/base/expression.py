
from qit.base.qitobject import QitObject

class Expression(QitObject):

    def __init__(self, type):
        self.type = type

    @property
    def childs(self):
        return (self.type,)

    def is_expression(self):
        return True

    def is_constant_value(self, value):
        return False

    def write_into_variable(self, builder):
        return builder.write_expression_into_variable(self)

    def make_function(self, params=None):
        from qit.base.function import FunctionFromExpression
        return FunctionFromExpression(self, params)
