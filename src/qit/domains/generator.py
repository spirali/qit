
from qit.base.struct import Struct
from qit.domains.iterator import Iterator

class GeneratorIterator(Iterator):

    def __init__(self, generator):
        self.generator = generator
        itype = Struct()
        super().__init__(itype, generator.function.return_type, itype.value(()))
        self.next_fn.code("")
        self.value_fn.code("return {{generator}};", generator=generator)
        self.is_valid_fn.code("return true;")
