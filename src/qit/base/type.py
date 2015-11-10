
from qit.base.fcollection import FullCollection


class Range(FullCollection):

    def __init__(self, stop):
        self.stop = stop

    def get_iterator_type(self, builder):
        return builder.get_range_iterator()

    def get_generator_type(self, builder):
        return builder.get_range_generator()

    def get_element_type(self, builder):
        return builder.get_range_type()

    def make_iterator(self, builder):
        args = (str(self.stop),)
        return builder.make_iterator(self, args)

    def make_generator(self, builder):
        args = (str(self.stop),)
        return builder.make_generator(self, args)


class Product(FullCollection):

    def __init__(self, name):
        self.name = name
        self.items = []

    @property
    def names(self):
        return tuple(name for name, c in self.items)

    @property
    def collections(self):
        return tuple(c for name, c in self.items)

    def make_iterator(self, builder):
        return builder.make_basic_iterator(self, self.collections)

    def make_generator(self, builder):
        return builder.make_basic_generator(self, self.collections)

    def add(self, name, collection):
        self.items.append((name, collection))

    def declare_iterator(self, builder):
        for c in self.collections:
            c.declare_iterator(builder)
        builder.declare_product_class(self)
        builder.declare_product_class(self)
        builder.declare_product_iterator(self)

    def declare_generator(self, builder):
        for c in self.collections:
            c.declare_generator(builder)
        builder.declare_product_class(self)
        builder.declare_product_generator(self)

    def get_iterator_type(self, builder):
        return builder.get_product_iterator(self)

    def get_generator_type(self, builder):
        return builder.get_product_generator(self)

    def get_element_type(self, builder):
        return builder.get_product_type(self)
