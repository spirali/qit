from qit.base.type import Type
from qit.base.iterator import Iterator
from qit.base.generator import Generator
from qit.base.int import Int
import struct


class Sequence(Type):

    struct = struct.Struct('<Q')
    struct_size = struct.size

    def __init__(self, element_type, size=None):
        super().__init__()
        self.element_type = element_type
        if size is not None:
            self.size = Int().check_value(size)
        else:
            self.size = None

    @property
    def basic_type(self):
        return Sequence(self.element_type)

    @property
    def childs(self):
        return super().childs + (self.element_type,)

    def get_element_type(self, builder):
        return builder.get_sequence_type(self)

    def read(self, f):
        data = f.read(self.struct_size)
        if not data:
            return None
        size = self.struct.unpack(data)[0]
        return [ self.element_type.read(f) for i in range(size) ]

    def make_instance(self, builder, value):
        return builder.make_sequence_instance(self, value)

    def is_python_instance(self, obj):
        return isinstance(obj, tuple) or isinstance(obj, list)

    def transform_python_instance(self, obj):
        return tuple(obj)

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
        super().__init__(sequence)
        self.size = Int().check_value(size)

    @property
    def childs(self):
        return super().childs + (self.size, self.element_iterator)

    @property
    def element_iterator(self):
        return self.output_type.element_type.iterator

    def get_iterator_type(self, builder):
        return builder.get_sequence_iterator(self)

    def make_iterator(self, builder):
        return builder.make_basic_iterator(
                self, (self.element_iterator,), (self.size.get_code(builder),))


class SequenceGenerator(Generator):

    def __init__(self, sequence, size=None):
        super().__init__(sequence)
        self.size = Int().check_value(size)

    @property
    def childs(self):
        return super().childs + (self.size, self.element_generator)

    @property
    def element_generator(self):
        return self.output_type.element_type.generator

    def get_generator_type(self, builder):
        return builder.get_sequence_generator(self)

    def make_generator(self, builder):
        return builder.make_basic_generator(
                self, (self.element_generator,), (self.size.get_code(builder),))
