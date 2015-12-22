
from qit.base.qitobject import QitObject
from qit.base.expression import Expression
from qit.base.utils import validate_variables, sorted_variables
from qit.base.eqmixin import HashableEqMixin


class FunctionParameter(HashableEqMixin):

    def __init__(self, type, name, const):
        self.type = type
        self.name = name
        self.const = const


class Function(QitObject):

    autoname_prefix = "Function"

    def __init__(self, name=None, returns=None):
        self.name = name
        self.params = ()
        self.return_type = returns
        self.filename = None
        self.external_file = None
        self.inline_code = None
        self.inline_code_vars = ()
        self.used_expressions = ()
        self.read_variables = ()

    def is_function(self):
        return True

    def takes(self, type, name=None, const=True):
        type = type.as_type()
        if name is None:
            name = "p" + str(len(self.params))
        self.params += (FunctionParameter(type, name, const),)
        return self

    def returns(self, return_type):
        self.return_type = return_type
        return self

    def code(self, code, **kw):
        self.inline_code = code
        self.inline_code_vars = tuple(sorted(kw.items(), key=lambda o: o[0]))
        self.external_file = None
        return self

    def reads(self, *variables):
        self.read_variables = variables
        self.uses(variables)
        return self

    def from_file(self, filename):
        self.filename = filename
        return self

    def is_external(self):
        return self.filename is not None

    def declare(self, builder):
        builder.declare_function(self)

    def uses(self, expressions):
        self.used_expressions += tuple(expressions)
        return self

    @property
    def childs(self):
        childs = tuple(p.type for p in self.params)
        childs += tuple(value for name, value in self.inline_code_vars
                        if not name.startswith("_"))
        childs += self.used_expressions
        return childs

    def build(self, builder):
        return builder.build_functor(self)

    def build_closure(self, builder, prefix):
        return builder.build_functor(self, prefix)

    def build_declaration(self, builder, name, skip_first=False):
        params = [ p.type.build_param(builder, p.name, p.const)
                   for p in self.params ]
        if skip_first:
            params = params[1:]
        return "{} {}({})".format(
                         self.return_type.build(builder)
                             if self.return_type else "void",
                         name,
                         ",".join(params))

    def write_code(self, builder):
        if self.is_external():
           builder.write_function_external_call(self)
        else:
           for v in self.read_variables:
               builder.writer.line("const {} &{} = {};",
                   v.type.build(builder),
                   v.name,
                   v.build(builder))
           assert self.inline_code is not None
           builder.write_code(
                   self.inline_code, self.inline_code_vars)

    def __call__(self, *args):
        return FunctionCall(self, args)


class FunctionCall(Expression):

    def __init__(self, function, args):
        super().__init__(function.return_type)
        self.function = function

        # TODO: Check args count with QitException
        assert len(args) == len(function.params)
        tmp = []
        for a, p in zip(args, function.params):
            tmp.append(p.type.value(a))
        self.args = tuple(tmp)

    @property
    def childs(self):
        return super().childs + self.args + (self.function,)

    def build(self, builder):
        return builder.build_function_call(self)


class FunctionFromExpression(Function):

    def __init__(self, expression, params=None):
        super().__init__()
        self.uses((expression,))
        if params is None:
            params = expression.get_variables()
        params = tuple(params)
        for v in params:
            self.takes(v.type, v.build(None))
        self.returns(expression.type)
        self.expression = expression
        self._bounded_variables = params

    @property
    def bounded_variables(self):
        return frozenset(self._bounded_variables)

    def write_code(self, builder):
        builder.write_return_expression(self.expression)

from qit.base.variable import Variable
