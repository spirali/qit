
from qit.base.type import BasicType, DerivedType, TypeIterator
from qit.base.generator import Generator

class Product(BasicType):

    def __init__(self, name):
        self.name = name
        self.items = []
        self.generators = {}
        self.iterators = {}

    @property
    def names(self):
        return tuple(name for name, t in self.items)

    @property
    def types(self):
        return tuple(t for name, t in self.items)

    @property
    def basic_types(self):
        return tuple(t.basic_type for name, t in self.items)

    @property
    def iterator(self):
        return ProductIterator(
                self, [self.get_iterator(name) for name in self.names])

    @property
    def generator(self):
        return ProductGenerator(
                self, [self.get_generator(name) for name in self.names])

    def set(self, name, type):
        self.set_generator(name, type.generator)
        self.set_iterator(name, type.iterator)

    def get_generator(self, name):
        return self.generators[name]

    def get_iterator(self, name):
        return self.iterators[name]

    def set_generator(self, name, generator):
        self.generators[name] = generator

    def set_iterator(self, name, iterator):
        self.iterator[name] = iterator

    def get_element_type(self, builder):
        return builder.get_product_type(self)

    def add(self, name, collection):
        self.items.append((name, collection))
        self.iterators[name] = collection.iterator
        self.generators[name] = collection.generator

    def declare(self, builder):
        builder.declare_product_class(self)

    def derive(self):
        return DerivedProduct(self)


class DerivedProduct(DerivedType):

    def __init__(self, product):
        super().__init__(product)
        self.generators = {}
        self.iterators = {}

    def get_generator(self, name):
        generator = self.generators.get(name)
        if generator:
            return generator
        else:
            return self.parent_type.get_generator(name)

    def get_iterator(self, name):
        iterator = self.iterators.get(name)
        if iterator:
            return iterator
        else:
            return self.parent_type.get_iterator(name)

    def set(self, name, type):
        self.set_generator(name, type.generator)
        self.set_iterator(name, type.iterator)

    def set_generator(self, name, generator):
        self.generators[name] = generator

    def set_iterator(self, name, iterator):
        self.iterators[name] = iterator

    @property
    def iterator(self):
        return ProductIterator(
                self.basic_type, [self.get_iterator(name) for name in self.basic_type.names])

    @property
    def generator(self):
        return ProductGenerator(
                self.basic_type, [self.get_generator(name) for name in self.basic_type.names])


class ProductIterator(TypeIterator):

    def __init__(self, product, iterators):
        self.output_type = product
        self.iterators = iterators

    def get_iterator_type(self, builder):
        return builder.get_product_iterator(self)

    def make_iterator(self, builder):
        return builder.make_basic_iterator(self, self.iterators)

    def declare(self, builder):
        for iterator in self.iterators:
            iterator.declare(builder)
        self.output_type.declare(builder)
        builder.declare_product_iterator(self)


class ProductGenerator(Generator):

    def __init__(self, product, generators):
        self.output_type = product
        self.generators = generators

    def get_generator_type(self, builder):
        return builder.get_product_generator(self)

    def make_generator(self, builder):
        return builder.make_basic_generator(self, self.generators)

    def declare(self, builder):
        for iterator in self.generators:
            iterator.declare(builder)
        self.output_type.declare(builder)
        builder.declare_product_generator(self)
