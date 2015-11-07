
from qit.base.fcollection import FullCollection


class Range(FullCollection):

    def __init__(self, stop):
        self.stop = stop

    def get_constructor_args(self, builder):
        return builder.get_range_constructor_args(self)

    def get_iterator_type(self, builder):
        return builder.get_range_iterator()

    def get_rgenerator_type(self, builder):
        return builder.get_range_rgenerator()


class Product(FullCollection):

    def __init__(self, name):
        self.name = name
        self.items = []

    @property
    def parent_collections(self):
        return tuple(c for name, c in self.items)

    @property
    def names(self):
        return tuple(name for name, c in self.items)

    def add(self, name, collection):
        self.items.append((name, collection))

    def declare(self, builder):
        builder.declare_product(self)

    def get_iterator_type(self, builder):
        return builder.get_product_iterator(self)

    def get_rgenerator_type(self, builder):
        return builder.get_product_rgenerator(self)
