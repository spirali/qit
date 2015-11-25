
from qit.base.iterator import Iterator
from qit.base.qitobject import QitObject

class Generator(QitObject):

    def __init__(self, output_type):
        self.output_type = output_type

    def make_generator(self, builder):
        return builder.make_generator(self, ())


class GeneratorIterator(Iterator):

    def __init__(self, generator):
        super().__init__(generator.output_type)
        self.generator = generator

    def get_iterator_type(self, builder):
        return builder.get_generator_iterator(self)

    def make_iterator(self, builder):
        variable = self.generator.make_generator(builder)
        return builder.make_iterator(self, (variable,))

    @property
    def childs(self):
        return super().childs + (self.generator,)
