
from qit.base.collection import Collection

class Tranformation(Collection):

    def __init__(self, collection):
        self.collection = collection

    def declare_iterator(self, builder):
        self.collection.declare_iterator(builder)

    def declare_generator(self, builder):
        self.collection.declare_generator(builder)

    def make_iterator(self, builder):
        return builder.make_basic_iterator(self, (self.collection,))

    def get_element_type(self, builder):
        return self.collection.get_element_type(builder)


class TakeTransformation(Tranformation):

    def __init__(self, collection, count):
        super().__init__(collection)
        self.count = count

    def get_iterator_type(self, builder):
        return builder.get_take_iterator(self)

    def make_iterator(self, builder):
        return builder.make_basic_iterator(self,
                                           (self.collection,),
                                           (str(self.count),))
