
from qit.base.iterator import Iterator
from qit.base.generator import Generator
from qit.base.type import Type


class Values(Type):

    def __init__(self, type, values):
        self.type = type
        self.values = values

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
        self.output_type = output_type
        self.values = values

    def get_iterator_type(self, builder):
        return builder.get_values_iterator_type(self)

    def declare(self, builder):
        super().declare(builder)
        builder.declare_values_iterator(self)


class ValuesGenerator(Generator):

    def __init__(self, output_type, values):
        self.output_type = output_type
        self.values = values

    def get_generator_type(self, builder):
        return builder.get_values_generator_type(self)

    def declare(self, builder):
        super().declare(builder)
        builder.declare_values_generator(self)
