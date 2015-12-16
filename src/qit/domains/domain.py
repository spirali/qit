
from qit.base.qitobject import QitObject, check_qit_object
from qit.base.exception import QitException
from qit.domains.generator import GeneratorIterator
from qit.base.int import Int

class Domain(QitObject):

    def __init__(self, type, iterator=None, generator=None, size=None, indexer=None):
        check_qit_object(type)
        assert type.is_type()
        self.type = type
        self.iterator = iterator
        self.generator = generator
        if size is not None:
            self.size = Int().value(size)
        else:
            self.size = None
        self.indexer = indexer

    def iterate(self):
        if self.iterator is None:
            raise QitException(
                    "Domain '{}' does not have an iterator".format(repr(self)))
        return self.iterator

    def is_iterable(self):
        return self.iterator is not None

    def generate(self):
        if self.generator is None:
            raise QitException(
                    "Domain '{}' does not have an generator".format(repr(self)))
        return GeneratorIterator(self.generator)

    def is_generable(self):
        return self.generator is not None

    def values(self, *values):
        return self.type.values(*values)

    def make_domain(self):
        return self

    def __mul__(self, other):
        return Product(self, other)

def check_domain(obj, have_iterator=False):
    if not isinstance(obj, Domain):
        raise QitException("{} is not domain".format(obj))

from qit.domains.product import Product
