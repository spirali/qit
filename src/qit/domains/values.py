
from qit.base.function import Function
from qit.domains.iterator import Iterator
from qit.domains.domain import Domain


class Values(Domain):

    def __init__(self, type, values):
        iterator = ValuesIterator(type, values)
        generator = ValuesGenerator(type, values)()
        super().__init__(type, iterator, generator)

class ValuesIterator(Iterator):
    pass
