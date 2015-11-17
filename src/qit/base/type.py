
from qit.base.iterator import Iterator
from qit.base.generator import GeneratorIterator
from qit.utils.eqmixin import EqMixin

from copy import copy

class Type(EqMixin):

    def __init__(self):
        pass

    def is_basic_type(self):
        return self == self.basic_type

    def iterate(self):
        return self.iterator

    def generate(self):
        return GeneratorIterator(self.generator)

    def declare(self, builder):
        pass

    def read_all(self, f):
        while True:
            obj = self.read(f)
            if obj is not None:
                yield obj
            else:
                break

    def copy(self):
        return copy(self)

    def __mul__(self, other):
        return Product(None, self, other)

class TypeIterator(Iterator):
    pass


# To break import cycle
from qit.base.product import Product
