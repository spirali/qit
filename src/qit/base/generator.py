
from qit.base.iterator import Iterator

class Generator:

    def declare(self, builder):
        pass

class GeneratorIterator(Iterator):

    def __init__(self, generator):
        self.generator = generator

    @property
    def output_type(self):
        return self.generator.output_type

    def get_iterator_type(self, builder):
        return builder.get_generator_iterator(self)

    def make_iterator(self, builder):
        variable = self.generator.make_generator(builder)
        return builder.make_iterator(self, (variable,))

    def declare(self, builder):
        self.generator.declare(builder)
