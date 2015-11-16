
from qit.base.iterator import Iterator
from qit.base.generator import GeneratorIterator
from qit.utils.eqmixin import EqMixin



class Type(EqMixin):

    def __init__(self, parent_type=None):
        self.parent_type = parent_type

    def is_basic_type(self):
        return self.parent_type is None

    @property
    def basic_type(self):
        if self.parent_type:
            return self.parent_type
        else:
            return self

    def get_element_type(self, builder):
        return self.parent_type.get_element_type(builder)

    def iterate(self):
        return self.iterator

    def generate(self):
        return GeneratorIterator(self.generator)

    def declare(self, builder):
        if self.parent_type:
            self.parent_type.declare(builder)

    def read_all(self, f):
        while True:
            obj = self.read(f)
            if obj is not None:
                yield obj
            else:
                break

    def __mul__(self, other):
        return Product(None, self, other)

class TypeIterator(Iterator):
    pass


# To break import cycle
from qit.base.product import Product
