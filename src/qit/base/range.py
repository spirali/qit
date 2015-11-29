
from qit.base.int import Int
from qit.base.type import TypeIterator
from qit.base.generator import Generator

class Range(Int):

    def __init__(self, start, end=None, step=1):
        super().__init__()
        if end is None:
            end = start
            start = 0

        self.start = self.check_value(start)
        self.end = self.check_value(end)
        self.step = self.check_value(step)

    @property
    def iterator(self):
        return RangeIterator(self.start, self.end, self.step)

    @property
    def generator(self):
        return RangeGenerator(self.start, self.end)


class RangeIterator(TypeIterator):

    def __init__(self, start, end, step):
        self.start = Int().check_value(start)
        self.end = Int().check_value(end)
        self.step = Int().check_value(step)

    @property
    def output_type(self):
        return Int()

    def get_element_type(self, builder):
        return builder.get_int_type()

    def get_iterator_type(self, builder):
        return builder.get_range_iterator()

    def make_iterator(self, builder):
        args = (self.start.get_code(builder),
                self.end.get_code(builder),
                self.step.get_code(builder))
        return builder.make_iterator(self, args)

    @property
    def childs(self):
        return (self.start, self.end, self.step)


class RangeGenerator(Generator):

    def __init__(self, start, end):
        self.start = Int().check_value(start)
        self.end = Int().check_value(end)

    @property
    def output_type(self):
        return Int()

    def get_generator_type(self, builder):
        return builder.get_range_generator()

    def make_generator(self, builder):
        args = (self.start.get_code(builder),
                self.end.get_code(builder))
        return builder.make_generator(self, args)

    @property
    def childs(self):
        return (self.start, self.end)
