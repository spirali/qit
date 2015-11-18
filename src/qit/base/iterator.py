
from qit.utils.eqmixin import EqMixin


class Iterator(EqMixin):

    def take(self, count):
        return TakeTransformation(self, count)

    def map(self, function):
        return MapTransformation(self, function)

    def declare(self, builder):
        self.output_type.declare(builder)

    def make_iterator(self, builder):
        return builder.make_iterator(self, ())


# To broke import cycle, we import following packages at the end
from qit.base.transformation import TakeTransformation
from qit.base.transformation import MapTransformation
