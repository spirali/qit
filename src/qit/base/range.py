
from qit.base.int import Int
from qit.base.type import Type, TypeIterator
from qit.base.generator import Generator

class Range(Int):

    def __init__(self, stop):
        super().__init__()
        self.stop = stop

    @property
    def iterator(self):
        return RangeIterator(self.stop)

    @property
    def generator(self):
        return RangeGenerator(self.stop)


class RangeIterator(TypeIterator):

    def __init__(self, stop):
        self.stop = stop

    @property
    def output_type(self):
        return Int()

    def get_element_type(self, builder):
        return builder.get_int_type()

    def get_iterator_type(self, builder):
        return builder.get_range_iterator()

    def make_iterator(self, builder):
        args = (str(self.stop),)
        return builder.make_iterator(self, args)


class RangeGenerator(Generator):

    def __init__(self, stop):
        self.stop = stop

    @property
    def output_type(self):
        return Int()

    def get_generator_type(self, builder):
        return builder.get_range_generator()

    def make_generator(self, builder):
        args = (str(self.stop),)
        return builder.make_generator(self, args)

