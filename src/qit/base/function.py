
from qit.base.qitobject import QitObject
from qit.base.sequence import Sequence
from qit.base.atom import validate_variables, Variable, sort_variables
from qit.base.expression import Expression

class Function(QitObject):

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
        self.variables = variables
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

    def make_functor(self, builder):
        return builder.make_functor(self)

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
        super().__init__(function.return_type.basic_type)
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

    def get_code(self, builder):
        return builder.get_function_call_code(self)


class FunctionFromIterator(Function):

    def __init__(self, iterator, params=None, return_type=None):
        super().__init__()
        variables = iterator.get_variables()
        validate_variables(variables)
        if params is None:
            params = sort_variables(variables)
        self.iterator = iterator
        for v in params:
            self.takes(v.type, v.name)
        for v in sorted(set(variables).difference(params)):
            self.reads(v)
        if return_type is None:
            return_type = Sequence(iterator.output_type.basic_type)
        self.returns(return_type)

    @property
    def childs(self):
        return super().childs + (self.iterator,)

    @property
    def bounded_variables(self):
        return frozenset(Variable(t, name) for t, name in self.params)

    def write_code(self, builder):
        if self.iterator.output_type.basic_type == self.return_type.basic_type:
            builder.write_function_from_iterator(self, sequence=False)
        else:
            builder.write_function_from_iterator(self, sequence=True)
