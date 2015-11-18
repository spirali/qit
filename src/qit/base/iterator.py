
from qit.utils.eqmixin import EqMixin


class Iterator(EqMixin):

    # Transformations

    def take(self, count):
        return TakeTransformation(self, count)

    def map(self, function):
        return MapTransformation(self, function)

    def sort(self, asceding=True):
        return SortTransformation(self, asceding)

    def filter(self, function):
        return FilterTransformation(self, function)

    # Non-public

    def declare(self, builder):
        self.output_type.declare(builder)

    def make_iterator(self, builder):
        return builder.make_iterator(self, ())

    def get_functions(self):
        return set()

    @property
    def iterator(self):
        return self


# To broke import cycle, we import following packages at the end
from qit.base.transformation import TakeTransformation, FilterTransformation
from qit.base.transformation import MapTransformation
from qit.base.transformation import SortTransformation
