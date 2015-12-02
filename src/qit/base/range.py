
from qit.base.int import Int
from qit.base.iterator import IteratorType
from qit.base.domain import Domain
from qit.base.function import Function
from qit.functions.random import rand_int


class Range(Domain):

    def __init__(self, start, end=None, step=1):
        if end is None:
            end = start
            start = 0

        start = Int().check_value(start)
        end = Int().check_value(end)
        step = Int().check_value(step)

        iterator = RangeIterator(start, end, step).make()
        generator = rand_int(start, end)

        if start.is_constant_value(0) and step.is_constant_value(1):
            size = end
        else:
            size = range_size(start, end, step)

        super().__init__(Int(),
                         iterator,
                         generator,
                         size)


range_size = Function()
range_size.takes(Int(), "start")
range_size.takes(Int(), "end")
range_size.takes(Int(), "step")
range_size.returns(Int())
range_size.code("return (end - start) / step;")


class RangeIterator(IteratorType):

    def __init__(self, start, end, step):
        super().__init__(Int())
        self.start = Int().check_value(start)
        self.end = Int().check_value(end)
        self.step = Int().check_value(step)

    @property
    def childs(self):
        return super().childs + (self.start, self.end, self.step)

    @property
    def constructor_args(self):
        return (self.start, self.end, self.step)

    def build_type(self, builder):
        return builder.build_range_iterator()
