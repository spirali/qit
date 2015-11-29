
from qit.base.domain import Domain
from qit.base.iterator import IteratorType
from qit.base.struct import Struct
from qit.base.function import Function


class Product(Domain):

    def __init__(self, *args):

        domains = []
        struct_args = []

        for arg in args:
            if isinstance(arg, tuple) and len(arg) == 2:
                domain = arg[0].make_domain()
                domains.append(domain)
                struct_args.append((domain.type, arg[1]))
            else:
                domains.append(arg.make_domain())
                struct_args.append(arg.type)

        iterators = tuple(d.iterator for d in domains)
        generators = tuple(d.generator for d in domains)
        super().__init__(Struct(*struct_args))

        self.domains = tuple(domains)
        self.iterators = iterators
        self._update_iterator()
        self.generators = generators
        self._update_generator()

    def set_iterator(self, name, iterator):
        index = self.type.names.index(name)
        iterators = list(self.iterators)
        iterators[index] = iterator
        self.iterators = tuple(iterators)
        self._update_iterator()

    def set_generator(self, name, generator):
        index = self.type.names.index(name)
        generators = list(self.generators)
        generators[index] = generator
        self.generators = tuple(generators)
        self._update_generator()

    def set(self, name, domain):
        self.set_iterator(name, domain.iterator)
        self.set_generator(name, domain.generator)

    def _update_iterator(self):
        if all(self.iterators):
            self.iterator = ProductIterator(self.type, self.iterators).make()
        else:
            self.iterator = None

    def _update_generator(self):
        if all(self.iterators):
            self.generator = ProductGenerator(self.type, self.generators)()
        else:
            self.generator = None

    def __mul__(self, other):
        args = list(zip(self.domains, self.type.names))
        args.append(other)
        return Product(*args)


class ProductIterator(IteratorType):

    def __init__(self, type, iterators):
        super().__init__(type)
        assert len(type.names) == len(iterators)
        self.iterators = tuple(iterators)

    @property
    def childs(self):
        return super().childs + self.iterators

    def declare(self, builder):
        builder.declare_product_iterator(self)

    @property
    def constructor_args(self):
        return self.iterators


class ProductGenerator(Function):

    def __init__(self, type, generators):
        super().__init__()
        self.returns(type)
        self.generators = tuple(generators)

    @property
    def childs(self):
        return super().childs + self.generators

    def write_code(self, builder):
        builder.write_struct_generator(self.return_type, self.generators)
