
from qit.base.type import NamedType, TypeIterator
from qit.base.generator import Generator

class Product(NamedType):

    def __init__(self, *args):
        self.name = None
        names = []
        types = []

        for arg in args:
            if isinstance(arg, tuple) and len(arg) == 2:
                types.append(arg[0])
                names.append(arg[1])
            else:
                types.append(arg)
                names.append("_v{}".format(len(names)))

        assert len(set(names)) == len(names)
        self.names = tuple(names)
        self.types = tuple(types)
        self.generators = (None,) * len(names)
        self.iterators = (None,) * len(names)

    def set_name(self, name):
        self.name = name
        return self

    @property
    def basic_type(self):
        return Product(*zip(self.basic_types, self.names))

    @property
    def basic_types(self):
        return tuple(t.basic_type for t in self.types)

    @property
    def iterator(self):
        return ProductIterator(
                self.basic_type,
                tuple(self.get_iterator(name) for name in self.names))

    @property
    def generator(self):
        return ProductGenerator(
                self.basic_type,
                tuple(self.get_generator(name) for name in self.names))

    def __mul__(self, other):
        return Product(*(tuple(zip(self.types, self.names)) + (other,)))

    def make_instance(self, builder, value):
        return builder.make_product_instance(self, value)

    def is_python_instance(self, obj):
        return (isinstance(obj, tuple) or isinstance(obj, list)) \
                and len(obj) == len(self.names)

    def set(self, name, type):
        index = self.names.index(name)
        assert type.basic_type == self.types[index].basic_type
        lst = list(self.types)
        lst[index] = type
        self.types = tuple(lst)

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
        lst = list(self.generators)
        lst[index] = generator
        self.generators = tuple(lst)

    def set_iterator(self, name, iterator):
        index = self.names.index(name)
        lst = list(self.iterators)
        lst[index] = iterator
        self.iterators = tuple(lst)

    def get_element_type(self, builder):
        return builder.get_product_type(self)

    def declare(self, builder):
        super().declare(builder)
        builder.declare_product_class(self.basic_type)

    @property
    def childs(self):
        return self.types

    def copy(self):
        return Product(*zip(self.types, self.names))

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


class ProductIterator(TypeIterator):

    def __init__(self, product, iterators):
        self.output_type = product
        self.iterators = tuple(iterators)

    def get_iterator_type(self, builder):
        return builder.get_product_iterator(self)

    def make_iterator(self, builder):
        return builder.make_basic_iterator(self, self.iterators)

    @property
    def childs(self):
        return super().childs + (self.output_type,) + self.iterators

    def declare(self, builder):
        builder.declare_product_iterator(self)


class ProductGenerator(Generator):

    def __init__(self, product, generators):
        self.output_type = product
        self.generators = tuple(generators)

    def get_generator_type(self, builder):
        return builder.get_product_generator(self)

    def make_generator(self, builder):
        return builder.make_basic_generator(self, self.generators)

    def declare(self, builder):
        builder.declare_product_generator(self)

    @property
    def childs(self):
        return super().childs + (self.output_type,) + self.generators
