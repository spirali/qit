
from qit.base.collection import Collection

class Tranformation(Collection):

    def __init__(self, collection):
        self.collection = collection

    @property
    def parent_collections(self):
        return (self.collection,)


class TakeTransformation(Tranformation):

    def __init__(self, collection, count):
        super().__init__(collection)
        self.count = count

    def get_iterator_type(self, builder):
        return builder.get_take_iterator(self)

    def get_constructor_args(self, builder):
        return builder.get_take_constructor_args(self)


class RandomTranformation(Tranformation):

    # Since we depend on generator
    # we do not have to construct parent collections
    parent_collections = ()

    @property
    def parent_generators(self):
        return (self.collection,)

    def get_iterator_type(self, builder):
        return builder.get_generator_iterator(self)
