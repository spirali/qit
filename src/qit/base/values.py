
from qit.base.iterator import IteratorType
from qit.base.domain import Domain
from qit.base.function import Function
from qit.base.utils import sorted_variables


class Values(Domain):

    def __init__(self, type, values):
        iterator = ValuesIterator(type, values).make()
        generator = ValuesGenerator(type, values)()
        super().__init__(type, iterator, generator)


class ValuesIterator(IteratorType):

    def __init__(self, type, values):
        super().__init__(type)
        self.values =  tuple(type.check_value(v) for v in values)

    def declare(self, builder):
        builder.declare_values_iterator(self)

    @property
    def constructor_args(self):
        return sorted_variables(self.get_variables())

    @property
    def childs(self):
        return super().childs + self.values


class ValuesGenerator(Function):

    def __init__(self, type, values):
        super().__init__()
        self.returns(type)
        self.values = tuple(type.check_value(v) for v in values)
        variables = frozenset()
        for v in self.values:
            variables = variables.union(v.get_variables())
        self.reads(*sorted_variables(variables))

    @property
    def childs(self):
        return super().childs + self.values

    def write_code(self, builder):
        builder.write_values_generator(self)
