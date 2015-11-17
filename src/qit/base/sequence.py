from qit.base.type import Type
from qit.base.iterator import Iterator
from qit.base.generator import Generator
import struct

class Sequence(Type):

    struct = struct.Struct('<Q')
    struct_size = struct.size

    def __init__(self, element_type, size=None):
        super().__init__()
        self.element_type = element_type
        self.size = size

    @property
    def basic_type(self):
        return Sequence(self.element_type)

    def get_element_type(self, builder):
        return builder.get_sequence_type(self)

    def read(self, f):
        data = f.read(self.struct_size)
        if not data:
            return None
        size = self.struct.unpack(data)[0]
        return [ self.element_type.read(f) for i in range(size) ]

    @property
    def iterator(self):
        if self.size is not None:
            return SequenceIterator(self, self.size)
        else:
            raise Exception("Unbound sequence does not have iterator")

    @property
    def generator(self):
        if self.size is not None:
            return SequenceGenerator(self, self.size)
        else:
            raise Exception("Unbound sequence does not have generator")


class SequenceIterator(Iterator):

    def __init__(self, sequence, size=None):
        self.output_type = sequence
        self.size = size

    @property
    def element_iterator(self):
        return self.output_type.element_type.iterator

    def declare(self, builder):
        self.output_type.element_type.iterator.declare(builder)
        super().declare(builder)

    def get_iterator_type(self, builder):
        return builder.get_sequence_iterator(self)

    def make_iterator(self, builder):
        return builder.make_basic_iterator(
                self, (self.element_iterator,), (str(self.size),))


class SequenceGenerator(Generator):

    def __init__(self, sequence, size=None):
        self.output_type = sequence
        self.size = size

    @property
    def element_generator(self):
        return self.output_type.element_type.generator

    def get_generator_type(self, builder):
        return builder.get_sequence_generator(self)

    def make_generator(self, builder):
        return builder.make_basic_generator(
                self, (self.element_generator,), (str(self.size),))

    def declare(self, builder):
        self.output_type.element_type.generator.declare(builder)
        super().declare(builder)


