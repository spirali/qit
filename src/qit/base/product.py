
from qit.base.domain import Domain
from qit.base.iterator import IteratorType
from qit.base.struct import Struct
from qit.base.function import Function
from qit.base.int import Int
from qit.functions.int import multiplication_n

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
        type = Struct(*struct_args)
        super().__init__(
                type,
                self._make_iterator(type, domains),
                self._make_generator(type, domains),
                self._make_size(domains))
        self.domains = tuple(domains)

    def _make_iterator(self, type, domains):
        iterators = [ d.iterator for d in domains ]
        if all(iterators):
            return ProductIterator(type, iterators).make()

    def _make_generator(self, type, domains):
        generators = [ d.generator for d in domains ]
        if all(generators):
            return ProductGenerator(type, generators)()

    def _make_size(self, domains):
        sizes = [ d.size for d in domains ]
        if all(sizes):
            return multiplication_n(len(sizes))(*sizes)

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
