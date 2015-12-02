from qit.base.iterator import IteratorType
from qit.base.int import Int
from qit.base.vector import Vector
from qit.base.domain import Domain
from qit.base.function import Function
from qit.functions.int import power

class Sequence(Domain):

    def __init__(self, domain, size):
        vector = Vector(domain.type)
        if domain.iterator is not None:
            iterator = SequenceIterator(domain.iterator, size).make()
        else:
            iterator = None

        if domain.generator is not None:
            generator = SequenceGenerator(domain.generator, size)()
        else:
            generator = None

        if domain.size is not None:
            size = Int().check_value(size)
            domain_size = power(domain.size, size)
        else:
            domain_size = None

        super().__init__(vector, iterator, generator, domain_size)


class SequenceIterator(IteratorType):

    def __init__(self, element_iterator, size):
        super().__init__(Vector(element_iterator.type.output_type))
        self.element_iterator = element_iterator
        self.size = Int().check_value(size)

    @property
    def childs(self):
        return super().childs + (self.size, self.element_iterator)

    @property
    def constructor_args(self):
        return (self.element_iterator, self.size)

    def build_type(self, builder):
        return builder.build_sequence_iterator(self)


class SequenceGenerator(Function):

    def __init__(self, element_generator, size):
        super().__init__()
        self.returns(Vector(element_generator.type))
        self.element_generator = element_generator
        self.size = Int().check_value(size)

    @property
    def childs(self):
        return super().childs + (self.size, self.element_generator)

    def write_code(self, builder):
        builder.write_sequence_generator(self)
