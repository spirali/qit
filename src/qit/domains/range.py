
from qit.base.int import Int
from qit.base.function import Function
from qit.domains.iterator import Iterator
from qit.domains.domain import Domain
from qit.functions.random import rand_int
from qit.functions.int import identity


class Range(Domain):
    """
        Range of integers
    """

    def __init__(self, start, end=None, step=1):
        if end is None:
            end = start
            start = 0

        start = Int().value(start)
        end = Int().value(end)
        step = Int().value(step)

        iterator = RangeIterator(start, end, step)
        generator = rand_int(start, end)

        if (start.is_constructor() and start.value == 0 and
                step.is_constructor() and step.value == 1):
            size = end
            indexer = identity
        else:
            size = range_size(start, end, step)
            indexer = Function().returns(Int())
            indexer.takes(Int(), "_v")
            indexer.code("return (_v - {{start}}) / {{step}};",
                         start=start, step=step)

        super().__init__(Int(),
                         iterator,
                         generator,
                         size,
                         indexer)


range_size = Function()
range_size.takes(Int(), "start")
range_size.takes(Int(), "end")
range_size.takes(Int(), "step")
range_size.returns(Int())
range_size.code("return (end - start) / step;")


class RangeIterator(Iterator):

    def __init__(self, start, end, step):
        itype = Int()
        super().__init__(itype, Int())
        self.reset_fn.code("iter = {{start}};", start=start)
        self.next_fn.code("iter+={{step}};", step=step)
        self.is_valid_fn.code("return iter < {{end}};", end=end)
        self.value_fn = identity
