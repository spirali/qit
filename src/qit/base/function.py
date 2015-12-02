
from qit.base.qitobject import QitObject
from qit.base.expression import Expression
from qit.base.utils import validate_variables, sorted_variables

class Function(QitObject):

    autoname_prefix = "Function"

    def __init__(self, name=None):
        self.name = name
        self.params = ()
        self.return_type = None
        self.inline_code = None
        self.filename = None
        self.variables = ()

    def is_function(self):
        return True

    def takes(self, collection, name):
        self.params = self.params + ((collection, name),)
        return self

    def returns(self, return_type):
        self.return_type = return_type
        return self

    def code(self, code):
        self.inline_code = code
        self.external_file = None
        return self

    def reads(self, *variables):
        validate_variables(variables)
        self.variables = tuple(variables)
        return self

    def from_file(self, filename):
        self.filename = filename
        return self

    def is_external(self):
        return self.filename is not None

    def declare(self, builder):
        builder.declare_function(self)

    @property
    def childs(self):
        return tuple(t for t,name in self.params) + self.variables

    def build_value(self, builder):
        return builder.build_functor(self)

    def write_code(self, builder):
        if self.is_external():
           builder.write_function_external_call(self)
        else:
           assert self.inline_code is not None
           builder.write_function_inline_code(self)

    def __call__(self, *args):
        return FunctionCall(self, args)


class FunctionCall(Expression):

    def __init__(self, function, args):
        super().__init__(function.return_type)
        self.function = function

        # TODO: Check args count with QitException
        assert len(args) == len(function.params)
        tmp = []
        for a, (type, name) in zip(args, function.params):
            tmp.append(type.check_value(a))
        self.args = tuple(tmp)

    @property
    def childs(self):
        return super().childs + self.args + (self.function,)

    def build_value(self, builder):
        return builder.build_function_call(self)


class FunctionFromExpression(Function):

    def __init__(self, expression, params=None):
        super().__init__()
        variables = expression.get_variables()
        validate_variables(variables)
        if params is None:
            params = sorted_variables(variables)
        self.expression = expression
        for v in params:
            self.takes(v.type, v.name)
        self.reads(*sorted(set(variables).difference(params)))
        self.returns(self.expression.type)

    @property
    def childs(self):
        return super().childs + (self.expression,)

    @property
    def bounded_variables(self):
        return frozenset(Variable(t, name) for t, name in self.params)

    def write_code(self, builder):
        builder.write_function_from_expression(self.expression)

from qit.base.atom import Variable
