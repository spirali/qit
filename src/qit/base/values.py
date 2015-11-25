
from qit.base.iterator import Iterator
from qit.base.generator import Generator
from qit.base.type import Type
from qit.base.atom import sort_variables


class Values(Type):

    def __init__(self, type, values):
        self.type = type
        self.values = tuple(type.check_value(v) for v in values)

    def get_element_type(self, builder):
        return self.type.get_element_type(builder)

    @property
    def basic_type(self):
        return self.type.basic_type

    @property
    def iterator(self):
        return ValuesIterator(self.basic_type, self.values)

    @property
    def generator(self):
        return ValuesGenerator(self.basic_type, self.values)


class ValuesIterator(Iterator):

    def __init__(self, output_type, values):
        super().__init__(output_type)
        self.values = tuple(output_type.check_value(v) for v in values)

    def get_iterator_type(self, builder):
        return builder.get_values_iterator_type(self)

    def make_iterator(self, builder):
        args = [ v.get_code(self)
                 for v in sort_variables(self.get_variables()) ]
        return builder.make_iterator(self, args)

    @property
    def childs(self):
        return super().childs + self.values

    def declare(self, builder):
        builder.declare_values_iterator(self)


class ValuesGenerator(Generator):

    def __init__(self, output_type, values):
        super().__init__(output_type)
        self.values = tuple(output_type.check_value(v) for v in values)

    @property
    def childs(self):
        return super().childs + self.values

    def get_generator_type(self, builder):
        return builder.get_values_generator_type(self)

    def declare(self, builder):
        builder.declare_values_generator(self)
