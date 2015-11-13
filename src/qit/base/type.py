
from qit.base.iterator import Iterator
from qit.base.generator import GeneratorIterator
from qit.utils.eqmixin import EqMixin

class Type(EqMixin):

    def declare_element(self, builder):
        pass

    def iterate(self):
        return self.iterator

    def generate(self):
        return GeneratorIterator(self.generator)

    def declare(self, builder):
        pass


class BasicType(Type):

    @property
    def basic_type(self):
        return self


class DerivedType(Type):

    def __init__(self, parent_type):
        self.parent_type = parent_type

    @property
    def basic_type(self):
        return self.parent_type.basic_type

    def get_element_type(self, builder):
        return self.basic_type.get_element_type(builder)

    def declare(self, builder):
        return self.basic_type.declare(builder)


class TypeIterator(Iterator):
    pass
