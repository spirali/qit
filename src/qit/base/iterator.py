
from qit.base.qitobject import QitObject

class Iterator(QitObject):

    def __init__(self, output_type):
        self.output_type = output_type

    @property
    def childs(self):
        return (self.output_type,)

    # Transformations

    def take(self, count):
        return TakeTransformation(self, count)

    def map(self, function):
        return MapTransformation(self, function)

    def sort(self, asceding=True):
        return SortTransformation(self, asceding)

    def filter(self, function):
        return FilterTransformation(self, function)

    def make_function(self, params=None, return_type=None):
        return FunctionFromIterator(self, params, return_type)

    # Non-public

    def make_iterator(self, builder):
        return builder.make_iterator(self, ())

    @property
    def iterator(self):
        return self


# To broke import cycle, we import following packages at the end
from qit.base.transformation import TakeTransformation, FilterTransformation
from qit.base.transformation import MapTransformation
from qit.base.transformation import SortTransformation
from qit.base.function import FunctionFromIterator
