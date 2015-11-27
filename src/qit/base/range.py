
from qit.base.int import Int
from qit.base.type import TypeIterator
from qit.base.generator import Generator

class Range(Int):

    def __init__(self, start, end=None, step=1):
        super().__init__()
        if end is None:
            self.start = 0
            self.end = start
        else:
            self.start = start
            self.end = end

        self.step = step

    @property
    def iterator(self):
        return RangeIterator(self.start, self.end, self.step)

    @property
    def generator(self):
        return RangeGenerator(self.start, self.end)


class RangeIterator(TypeIterator):

    def __init__(self, start, end, step):
        self.start = start
        self.end = end
        self.step = step

    @property
    def output_type(self):
        return Int()

    def get_element_type(self, builder):
        return builder.get_int_type()

    def get_iterator_type(self, builder):
        return builder.get_range_iterator()

    def make_iterator(self, builder):
        args = (str(self.start), str(self.end), str(self.step))
        return builder.make_iterator(self, args)


class RangeGenerator(Generator):

    def __init__(self, start, end):
        self.start = start
        self.end = end

    @property
    def output_type(self):
        return Int()

    def get_generator_type(self, builder):
        return builder.get_range_generator()

    def make_generator(self, builder):
        args = (str(self.start), str(self.end))
        return builder.make_generator(self, args)

