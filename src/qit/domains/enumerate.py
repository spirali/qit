
from qit.base.int import Int
from qit.base.enum import Enum
from qit.base.function import Function
from qit.domains.iterator import Iterator
from qit.domains.domain import Domain
from qit.functions.random import rand_int


class Enumerate(Domain):

    def __init__(self, *names):
        type = Enum(*names)
        iterator = EnumIterator(type)
        generator = Function(("generator", self)).returns(type).code("""
            return static_cast<{{type}}>({{rand_int}}(0, {{_size}}));""",
            _size=len(names), rand_int=rand_int, type=type)()
        size = Int().value(len(names))
        super().__init__(type,
                         iterator,
                         generator,
                         size)


class EnumIterator(Iterator):

    def __init__(self, enum):
        super().__init__(enum, enum)
        self.reset_fn.code("iter = {{start}};", start=enum.value(enum.names[0]))
        self.next_fn.code("iter = static_cast<{{type}}>(iter + 1);", type=enum)
        self.is_valid_fn.code("return iter < {{_size}};", _size=len(enum.names))
        self.value_fn.code("return iter;")
