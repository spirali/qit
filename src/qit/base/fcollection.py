
from qit.base.collection import Collection


class FullCollection(Collection):

    def random(self):
        return RandomCollection(self)

class RandomCollection(Collection):

    def __init__(self, collection):
        self.collection = collection

    def get_iterator_type(self, builder):
        return builder.get_generator_iterator(self)

    def declare_iterator(self, builder):
        self.collection.declare_generator(builder)

    def get_element_type(self, builder):
        return self.collection.get_element_type(builder)

    def make_iterator(self, builder):
        generator = self.collection.make_generator(builder)
        return builder.make_iterator(self, (generator,))
