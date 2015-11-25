
from qit.base.iterator import Iterator
from qit.base.generator import GeneratorIterator
from qit.base.qitobject import QitObject, check_qit_object
from qit.base.atom import Constant


from copy import copy

class Type(QitObject):

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

    def is_python_instance(self, obj):
        return False

    def transform_python_instance(self, obj):
        return obj

    def check_value(self, value):
        if self.is_python_instance(value):
            return Constant(self.basic_type,
                            self.transform_python_instance(value))
        check_qit_object(value)
        value.check_expression_type(self.basic_type)
        return value

    def read_all(self, f):
        while True:
            obj = self.read(f)
            if obj is not None:
                yield obj
            else:
                break

    def copy(self):
        return copy(self)

    def values(self, *args):
        return Values(self.basic_type, args)

    def __mul__(self, other):
        return Product(self, other)


class NamedType(Type):

    def declare(self, builder):
        if self.name:
            self.basic_type.declare(builder)
            builder.declare_type_alias(self)


class TypeIterator(Iterator):
    pass


# To break import cycle
from qit.base.product import Product
from qit.base.values import Values
