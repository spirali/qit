
from qit.base.iterator import IteratorType
from qit.base.utils import sorted_variables

class GeneratorIterator(IteratorType):

    def __init__(self, generator):
        super().__init__(generator.type)
        self.generator = generator

    def declare(self, builder):
        builder.declare_generator_iterator(self)

    @property
    def constructor_args(self):
        return tuple(sorted_variables(self.generator.get_variables()))

    @property
    def childs(self):
        return super().childs + (self.generator,)
