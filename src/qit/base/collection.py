
class Collection:

    def take(self, count):
        return TakeTransformation(self, count)

    def declare_iterator(self, builder):
        pass

    def declare_generator(self, builder):
        pass

    def make_iterator(self, builder):
        return builder.make_iterator(self, ())

# To broke import cycle, we import following packages at the end
from qit.base.transformation import TakeTransformation
