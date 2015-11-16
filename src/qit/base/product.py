
from qit.base.type import Type, TypeIterator
from qit.base.generator import Generator

class Product(Type):

    def __init__(self, name=None, *args):
        names = []
        types = []

        for arg in args:
            if isinstance(arg, tuple) and len(arg) == 2:
                types.append(arg[0])
                names.append(arg[1])
            else:
                types.append(arg)
                names.append("_v{}".format(len(names)))

        if all(t.is_basic_type() for t in types):
            super().__init__()
        else:
            basic_types = [ t.basic_type for t in types ]
            super().__init__(Product(name, *(zip(basic_types, names))))

        assert len(set(names)) == len(names)

        self.name = name
        self.names = names
        self.types = types
        self.generators = [ None ] * len(names)
        self.iterators = [ None ] * len(names)

    @property
    def basic_types(self):
        return tuple(t.basic_type for t in self.types)

    @property
    def iterator(self):
        return ProductIterator(
                self, [self.get_iterator(name) for name in self.names])

    @property
    def generator(self):
        return ProductGenerator(
                self, [self.get_generator(name) for name in self.names])

    def __mul__(self, other):
        return Product(None,
                       *(tuple(zip(self.types, self.names)) + (other,)))

    def set(self, name, type):
        index = self.names.index(name)
        self.types[index] = type

    def get_iterator(self, name):
        index = self.names.index(name)
        iterator = self.iterators[index]
        if iterator is not None:
            return iterator
        else:
            return self.types[index].iterator

    def get_generator(self, name):
        index = self.names.index(name)
        iterator = self.generators[index]
        if iterator is not None:
            return iterator
        else:
            return self.types[index].generator

    def set_generator(self, name, generator):
        index = self.names.index(name)
        self.generators[index] = generator

    def set_iterator(self, name, iterator):
        index = self.names.index(name)
        self.iterators[index] = iterator

    def get_element_type(self, builder):
        return builder.get_product_type(self)

    def declare(self, builder):
        if self.parent_type:
            self.parent_type.declare(builder)
        else:
            builder.declare_product_class(self)

    def derive(self):
        return Product(self.name, *zip(self.types, self.names))

    def read(self, f):
        if not self.names:
            return ()
        lst = []
        for t in self.types:
            element = t.basic_type.read(f)
            if element is None:
                if not lst:
                    return None # First element
                else:
                    raise Exception("Incomplete product")
            lst.append(element)
        return tuple(lst)

"""
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
"""

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
