
from qit.base.type import Type
from qit.base.expression import Expression
from qit.base.function import Function
from qit.base.vector import Vector
import struct

class IteratorType(Type):

    constructor_args = ()
    struct = struct.Struct('<c')
    struct_size = struct.size


    def __init__(self, output_type):
        self.output_type = output_type

    @property
    def childs(self):
        return (self.output_type,)

    def check_args(self, args):
        assert len(args) == 0 # By default, take no arguments
        return args

    def read_iterator(self, f):
        while True:
            data = f.read(self.struct_size)
            if not data or data[0] == 0:
                return None
            assert data[0] == 1
            obj = self.output_type.read(f)
            assert obj is not None
            yield obj

    def make(self):
        return IteratorInstance(self)

    def read(self, f):
        return list(self.read_iterator(f))


class IteratorInstance(Expression):

    def __init__(self, type):
        super().__init__(type)
        assert isinstance(type, IteratorType)

    def build_value(self, builder):
        return builder.build_object(self.type, self.type.constructor_args)

    # Transformations

    def take(self, count):
        return TakeTransformation(self, count).make()

    def map(self, function):
        return MapTransformation(self, function).make()

    def sort(self, asceding=True):
        return SortTransformation(self, asceding).make()

    def filter(self, function):
        return FilterTransformation(self, function).make()

    def to_vector(self):
        return IteratorToVector(self.type)(self)

    def iterate(self):
        return self


class IteratorToVector(Function):

    def __init__(self, iterator_type):
        super().__init__()
        self.takes(iterator_type, "i")
        self.returns(Vector(iterator_type.output_type))
        self.code("return qit::iterator_to_vector(i);")


class Iterator:
    pass # Deleteme


# To broke import cycle, we import following packages at the end
from qit.base.transformation import TakeTransformation, FilterTransformation
from qit.base.transformation import MapTransformation
from qit.base.transformation import SortTransformation
